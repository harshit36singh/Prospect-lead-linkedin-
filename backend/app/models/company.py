from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    domain: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    industry: Mapped[str] = mapped_column(String(120), default="")
    size_label: Mapped[str] = mapped_column(String(40), default="")
    size_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    size_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location: Mapped[str] = mapped_column(String(200), default="")
    technologies: Mapped[list[str]] = mapped_column(JSON, default=list)
    github_org: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source: Mapped[str] = mapped_column(String(60), default="")
    source_ref: Mapped[str] = mapped_column(String(200), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    contacts: Mapped[list["Contact"]] = relationship(back_populates="company")


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[str] = mapped_column(String(200), default="")
    location: Mapped[str] = mapped_column(String(200), default="")

    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email_confidence: Mapped[float] = mapped_column(default=0.0)
    email_source: Mapped[str | None] = mapped_column(String(60), nullable=True)
    email_verification_status: Mapped[str] = mapped_column(String(20), default="unverified")

    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    phone_confidence: Mapped[float] = mapped_column(default=0.0)
    phone_verification_status: Mapped[str] = mapped_column(String(20), default="not_available")

    is_duplicate: Mapped[bool] = mapped_column(default=False)
    duplicate_of_contact_id: Mapped[int | None] = mapped_column(
        ForeignKey("contacts.id"), nullable=True
    )

    source: Mapped[str] = mapped_column(String(60), default="")
    source_ref: Mapped[str] = mapped_column(String(200), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    company: Mapped["Company"] = relationship(back_populates="contacts")
