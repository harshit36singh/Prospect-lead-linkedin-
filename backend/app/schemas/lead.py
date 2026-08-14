from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.company import CompanyRead, ContactRead


class LeadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pipeline_run_id: int
    icp_id: int
    score: int
    grade: str
    score_breakdown: dict
    is_duplicate: bool
    exported_to_sheets_at: datetime | None
    exported_pdf_path: str | None
    created_at: datetime
    company: CompanyRead
    contact: ContactRead
