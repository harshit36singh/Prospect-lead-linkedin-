from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    icp_id: Mapped[int] = mapped_column(ForeignKey("icps.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/running/completed/failed
    stage: Mapped[str] = mapped_column(String(40), default="")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    companies_found: Mapped[int] = mapped_column(Integer, default=0)
    contacts_found: Mapped[int] = mapped_column(Integer, default=0)
    leads_created: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
