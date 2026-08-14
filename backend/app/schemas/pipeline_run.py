from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PipelineRunCreate(BaseModel):
    icp_id: int


class PipelineRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    icp_id: int
    status: str
    stage: str
    started_at: datetime | None
    finished_at: datetime | None
    companies_found: int
    contacts_found: int
    leads_created: int
    error_message: str | None
    created_at: datetime
