from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IcpBase(BaseModel):
    name: str
    industries: list[str] = []
    company_size_min: int | None = None
    company_size_max: int | None = None
    locations: list[str] = []
    technologies: list[str] = []
    target_titles: list[str] = []


class IcpCreate(IcpBase):
    pass


class IcpUpdate(IcpBase):
    pass


class IcpRead(IcpBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
