from __future__ import annotations

from app.dedupe.deduper import (
    dedupe_contacts_for_run,
    normalize_company_name,
    normalize_domain,
    normalize_email,
)
from app.models.company import Company, Contact
from app.models.icp import Icp
from app.models.lead import Lead
from app.models.pipeline_run import PipelineRun


def test_normalize_domain_strips_protocol_and_www():
    assert normalize_domain("https://www.Docker.com/") == "docker.com"
    assert normalize_domain("Docker.com") == "docker.com"


def test_normalize_company_name_strips_legal_suffixes():
    assert normalize_company_name("Acme Inc.") == "acme"
    assert normalize_company_name("Acme, LLC") == "acme"


def test_normalize_email_lowercases_and_trims():
    assert normalize_email("  Alex.Rivera@Docker.COM ") == "alex.rivera@docker.com"
    assert normalize_email(None) == ""


def _seed_icp_company(db):
    icp = Icp(name="Test", industries=[], locations=[], technologies=[], target_titles=[])
    db.add(icp)
    db.commit()
    db.refresh(icp)

    company = Company(
        name="Docker",
        domain="docker.com",
        industry="Developer Tools",
        size_label="300-500",
        location="Palo Alto, USA",
        technologies=[],
        source="seed",
        source_ref="docker.com",
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return icp, company


def _add_lead(db, run, icp, company, contact):
    lead = Lead(
        pipeline_run_id=run.id,
        icp_id=icp.id,
        company_id=company.id,
        contact_id=contact.id,
        score=50,
        grade="Warm",
        score_breakdown={},
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def test_exact_email_duplicate_is_flagged_across_runs(db_session):
    icp, company = _seed_icp_company(db_session)

    run1 = PipelineRun(icp_id=icp.id, status="completed")
    db_session.add(run1)
    db_session.commit()
    db_session.refresh(run1)
    c1 = Contact(company_id=company.id, full_name="Alex Rivera", email="alex.rivera@docker.com")
    db_session.add(c1)
    db_session.commit()
    db_session.refresh(c1)
    lead1 = _add_lead(db_session, run1, icp, company, c1)
    dedupe_contacts_for_run(db_session, run1.id)

    run2 = PipelineRun(icp_id=icp.id, status="completed")
    db_session.add(run2)
    db_session.commit()
    db_session.refresh(run2)
    c2 = Contact(company_id=company.id, full_name="Alex Rivera", email="alex.rivera@docker.com")
    db_session.add(c2)
    db_session.commit()
    db_session.refresh(c2)
    lead2 = _add_lead(db_session, run2, icp, company, c2)

    stats = dedupe_contacts_for_run(db_session, run2.id)

    db_session.refresh(c1)
    db_session.refresh(c2)
    db_session.refresh(lead1)
    db_session.refresh(lead2)

    assert stats.exact_duplicates == 1
    assert c1.is_duplicate is False
    assert c2.is_duplicate is True
    assert c2.duplicate_of_contact_id == c1.id
    assert lead1.is_duplicate is False
    assert lead2.is_duplicate is True


def test_fuzzy_name_duplicate_is_flagged(db_session):
    icp, company = _seed_icp_company(db_session)

    run1 = PipelineRun(icp_id=icp.id, status="completed")
    db_session.add(run1)
    db_session.commit()
    db_session.refresh(run1)
    c1 = Contact(company_id=company.id, full_name="Alex Rivera", email="alex.rivera@docker.com")
    db_session.add(c1)
    db_session.commit()
    db_session.refresh(c1)
    _add_lead(db_session, run1, icp, company, c1)
    dedupe_contacts_for_run(db_session, run1.id)

    run2 = PipelineRun(icp_id=icp.id, status="completed")
    db_session.add(run2)
    db_session.commit()
    db_session.refresh(run2)
    c2 = Contact(company_id=company.id, full_name="Alex Rivara", email=None)  # typo, no email
    db_session.add(c2)
    db_session.commit()
    db_session.refresh(c2)
    _add_lead(db_session, run2, icp, company, c2)

    stats = dedupe_contacts_for_run(db_session, run2.id)

    db_session.refresh(c2)
    assert stats.fuzzy_duplicates == 1
    assert c2.is_duplicate is True
    assert c2.duplicate_of_contact_id == c1.id


def test_genuinely_different_person_is_not_flagged(db_session):
    icp, company = _seed_icp_company(db_session)
    run = PipelineRun(icp_id=icp.id, status="completed")
    db_session.add(run)
    db_session.commit()
    db_session.refresh(run)

    c1 = Contact(company_id=company.id, full_name="Alex Rivera", email="alex.rivera@docker.com")
    c2 = Contact(company_id=company.id, full_name="Priya Shah", email="priya.shah@docker.com")
    db_session.add_all([c1, c2])
    db_session.commit()
    db_session.refresh(c1)
    db_session.refresh(c2)
    _add_lead(db_session, run, icp, company, c1)
    _add_lead(db_session, run, icp, company, c2)

    stats = dedupe_contacts_for_run(db_session, run.id)

    db_session.refresh(c1)
    db_session.refresh(c2)
    assert stats.exact_duplicates == 0
    assert stats.fuzzy_duplicates == 0
    assert c1.is_duplicate is False
    assert c2.is_duplicate is False
