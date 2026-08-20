from __future__ import annotations

from pydantic import BaseModel


class PdfExportRequest(BaseModel):
    run_id: int


class PdfExportResponse(BaseModel):
    filename: str
    lead_count: int


class SheetsExportRequest(BaseModel):
    run_id: int
    sheet_name: str


class SheetsExportResponse(BaseModel):
    sheet_url: str
    lead_count: int
