from __future__ import annotations

import re

from sqlalchemy.orm import Session

from app.discovery.base import DiscoveredCompany
from app.models.company import Company

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
