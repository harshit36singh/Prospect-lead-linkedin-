from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.database import SessionLocal
from app.dedupe.deduper import upsert_company
from app.discovery.registry import get_discovery_source
from app.enrichment.pattern_provider import PatternEnrichmentProvider
from app.models.company import Contact
from app.models.icp import Icp
from app.models.lead import Lead
from app.models.pipeline_run import PipelineRun
from app.schemas.icp import IcpRead
from app.scoring.scorer import score_lead
from app.verification.email_verifier import verify_email
from app.verification.phone_verifier import verify_phone

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def run_pipeline(pipeline_run_id: int) -> None:
    """Runs the full discovery -> ... pipeline for a PipelineRun row.

    Owns its own DB session since it may run in a FastAPI BackgroundTask
    after the request-scoped session has closed.
    """
    db = SessionLocal()
    try:
        run = db.get(PipelineRun, pipeline_run_id)
        if run is None:
            logger.error("PipelineRun %s not found", pipeline_run_id)
            return

        icp_row = db.get(Icp, run.icp_id)
        if icp_row is None:
            run.status = "failed"
            run.error_message = "ICP not found"
            run.finished_at = _utcnow()
            db.commit()
            return

        icp = IcpRead.model_validate(icp_row)

        run.status = "running"
        run.stage = "discovery"
        run.started_at = _utcnow()
        db.commit()

        source = get_discovery_source()
        discovered_companies = source.search_companies(icp)

        companies = []
        for discovered in discovered_companies:
            company = upsert_company(db, discovered)
            companies.append((discovered, company))
        db.commit()

        run.companies_found = len(companies)
        run.stage = "find_people"
        db.commit()

        enrichment = PatternEnrichmentProvider()
        new_contacts: list[Contact] = []
        company_by_id = {company.id: company for _, company in companies}
        for discovered, company in companies:
            people = source.find_people(discovered, icp)
            for person in people:
                enrichment_result = enrichment.enrich(person, discovered)
                contact = Contact(
                    company_id=company.id,
                    full_name=person.full_name,
                    title=person.title,
                    location=person.location,
                    source=person.source,
                    source_ref=person.source_ref,
                    email=enrichment_result.email,
                    email_confidence=enrichment_result.email_confidence,
                    email_source=enrichment_result.email_source,
                    phone=enrichment_result.phone,
                    phone_confidence=enrichment_result.phone_confidence,
                )
                db.add(contact)
                new_contacts.append(contact)
        db.commit()

        run.contacts_found = len(new_contacts)
        run.stage = "verification"
        db.commit()

        for contact in new_contacts:
            email_result = verify_email(contact.email)
            phone_result = verify_phone(contact.phone)
            contact.email_verification_status = email_result.status
            contact.phone_verification_status = phone_result.status
        db.commit()

        run.stage = "scoring"
        db.commit()

        leads_created = 0
        for contact in new_contacts:
            company = company_by_id[contact.company_id]
            breakdown = score_lead(company, contact, icp_row)
            lead = Lead(
                pipeline_run_id=run.id,
                icp_id=icp_row.id,
                company_id=company.id,
                contact_id=contact.id,
                score=breakdown.total,
                grade=breakdown.grade,
                score_breakdown=breakdown.as_dict(),
            )
            db.add(lead)
            leads_created += 1
        db.commit()

        run.leads_created = leads_created
        run.stage = "done"
        run.status = "completed"
        run.finished_at = _utcnow()
        db.commit()
    except Exception as exc:  # noqa: BLE001
        logger.exception("Pipeline run %s failed", pipeline_run_id)
        db.rollback()
        run = db.get(PipelineRun, pipeline_run_id)
        if run is not None:
            run.status = "failed"
            run.error_message = str(exc)[:1000]
            run.finished_at = _utcnow()
            db.commit()
    finally:
        db.close()
