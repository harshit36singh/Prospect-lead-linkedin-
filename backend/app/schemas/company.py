from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CompanyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    domain: str
    industry: str
    size_label: str
    size_min: int | None
    size_max: int | None
    location: str
    technologies: list[str]
    github_org: str | None
    source: str
    created_at: datetime


class ContactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    full_name: str
    title: str
    location: str
    email: str | None
    email_confidence: float
    email_source: str | None
    email_verification_status: str
    phone: str | None
    phone_confidence: float
    phone_verification_status: str
    is_duplicate: bool
    duplicate_of_contact_id: int | None
    created_at: datetime
