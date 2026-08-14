from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.database import SessionLocal
from app.dedupe.deduper import upsert_company
from app.discovery.registry import get_discovery_source
from app.models.company import Contact
from app.models.icp import Icp
from app.models.pipeline_run import PipelineRun
from app.schemas.icp import IcpRead

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

        contacts_found = 0
        for discovered, company in companies:
            people = source.find_people(discovered, icp)
            for person in people:
                contact = Contact(
                    company_id=company.id,
                    full_name=person.full_name,
                    title=person.title,
                    location=person.location,
                    source=person.source,
                    source_ref=person.source_ref,
                )
                db.add(contact)
                contacts_found += 1
        db.commit()

        run.contacts_found = contacts_found
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
