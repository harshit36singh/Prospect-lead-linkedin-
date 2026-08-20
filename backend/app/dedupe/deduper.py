from __future__ import annotations

import re
from dataclasses import dataclass

from rapidfuzz import fuzz
from sqlalchemy.orm import Session

from app.discovery.base import DiscoveredCompany
from app.models.company import Company, Contact
from app.models.lead import Lead

_LEGAL_SUFFIXES = re.compile(
    r"\b(inc|incorporated|llc|ltd|limited|corp|corporation|co|company|plc|gmbh)\b\.?",
    re.IGNORECASE,
)


def normalize_domain(raw: str) -> str:
    domain = raw.strip().lower()
    domain = re.sub(r"^https?://", "", domain)
    domain = re.sub(r"^www\.", "", domain)
    return domain.split("/")[0]


def normalize_company_name(raw: str) -> str:
    name = raw.strip().lower()
    name = re.sub(r"[,.]", " ", name)
    name = _LEGAL_SUFFIXES.sub("", name)
    return re.sub(r"\s+", " ", name).strip()


def find_existing_company(db: Session, name: str, domain: str) -> Company | None:
    normalized_domain = normalize_domain(domain)
    existing = db.query(Company).filter(Company.domain == normalized_domain).first()
    if existing is not None:
        return existing

    normalized_name = normalize_company_name(name)
    for candidate in db.query(Company).all():
        if normalize_company_name(candidate.name) == normalized_name:
            return candidate
    return None


def upsert_company(db: Session, discovered: DiscoveredCompany) -> Company:
    """Insert a new Company or update the mutable fields of an existing one.

    Companies are a shared reference entity across pipeline runs, so they are
    never duplicated -- matched by normalized domain (fallback: normalized
    name).
    """
    existing = find_existing_company(db, discovered.name, discovered.domain)
    if existing is not None:
        existing.industry = discovered.industry
        existing.size_label = discovered.size_label
        existing.size_min = discovered.size_min
        existing.size_max = discovered.size_max
        existing.location = discovered.location
        existing.technologies = discovered.technologies
        existing.github_org = discovered.github_org
        db.flush()
        return existing

    company = Company(
        name=discovered.name,
        domain=normalize_domain(discovered.domain),
        industry=discovered.industry,
        size_label=discovered.size_label,
        size_min=discovered.size_min,
        size_max=discovered.size_max,
        location=discovered.location,
        technologies=discovered.technologies,
        github_org=discovered.github_org,
        source=discovered.source,
        source_ref=discovered.source_ref,
    )
    db.add(company)
    db.flush()
    return company


def normalize_email(raw: str | None) -> str:
    if not raw:
        return ""
    return raw.strip().lower()


@dataclass(slots=True)
class DedupeStats:
    exact_duplicates: int
    fuzzy_duplicates: int


FUZZY_NAME_THRESHOLD = 90


def dedupe_contacts_for_run(db: Session, pipeline_run_id: int) -> DedupeStats:
    """Flags duplicate Contact rows for every company touched by this run.

    Contacts are created per pipeline run (never merged, to keep run
    history intact), so re-running the same ICP can rediscover the same
    person as a fresh row. This groups ALL contacts for each affected
    company (across every run, not just this one) by normalized email
    (exact phase), then by fuzzy name match among what's left (fuzzy
    phase), keeping the earliest-created row in each group as the
    non-duplicate "primary" and flagging the rest. Only this run's Lead
    rows are then synced to match -- earlier runs' leads were already
    correctly flagged when their own dedupe pass ran.
    """
    run_leads = db.query(Lead).filter(Lead.pipeline_run_id == pipeline_run_id).all()
    company_ids = {lead.company_id for lead in run_leads}

    exact_count = 0
    fuzzy_count = 0

    for company_id in company_ids:
        contacts = (
            db.query(Contact)
            .filter(Contact.company_id == company_id)
            .order_by(Contact.created_at.asc(), Contact.id.asc())
            .all()
        )

        email_groups: dict[str, list[Contact]] = {}
        for contact in contacts:
            key = normalize_email(contact.email)
            if key:
                email_groups.setdefault(key, []).append(contact)

        for group in email_groups.values():
            if len(group) <= 1:
                continue
            primary = group[0]
            for duplicate in group[1:]:
                duplicate.is_duplicate = True
                duplicate.duplicate_of_contact_id = primary.id
                exact_count += 1

        remaining = [c for c in contacts if not c.is_duplicate]
        for i, contact in enumerate(remaining):
            if contact.is_duplicate:
                continue
            for earlier in remaining[:i]:
                if earlier.is_duplicate:
                    continue
                ratio = fuzz.token_sort_ratio(contact.full_name.lower(), earlier.full_name.lower())
                if ratio >= FUZZY_NAME_THRESHOLD:
                    contact.is_duplicate = True
                    contact.duplicate_of_contact_id = earlier.id
                    fuzzy_count += 1
                    break

    db.commit()

    for lead in run_leads:
        contact = db.get(Contact, lead.contact_id)
        lead.is_duplicate = contact.is_duplicate if contact else False
    db.commit()

    return DedupeStats(exact_duplicates=exact_count, fuzzy_duplicates=fuzzy_count)
