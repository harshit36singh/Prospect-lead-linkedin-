from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.database import get_db
from app.export.pdf_exporter import PdfExportError, render_lead_report
from app.export.sheets_exporter import SheetsExportError, export_leads_to_sheet
from app.models.icp import Icp
from app.models.lead import Lead
from app.models.pipeline_run import PipelineRun
from app.schemas.export import (
    PdfExportRequest,
    PdfExportResponse,
    SheetsExportRequest,
    SheetsExportResponse,
)

router = APIRouter(prefix="/api/exports", tags=["exports"])


def _load_run_leads(db: Session, run_id: int) -> tuple[PipelineRun, Icp, list[Lead]]:
    run = db.get(PipelineRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    icp = db.get(Icp, run.icp_id)
    if icp is None:
        raise HTTPException(status_code=404, detail="ICP not found")
    leads = (
        db.query(Lead)
        .options(joinedload(Lead.company), joinedload(Lead.contact))
        .filter(Lead.pipeline_run_id == run_id, Lead.is_duplicate.is_(False))
        .all()
    )
    return run, icp, leads


@router.post("/pdf", response_model=PdfExportResponse)
def export_pdf(payload: PdfExportRequest, db: Session = Depends(get_db)) -> PdfExportResponse:
    _run, icp, leads = _load_run_leads(db, payload.run_id)

    try:
        path = render_lead_report(leads, icp)
    except PdfExportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    for lead in leads:
        lead.exported_pdf_path = str(path)
    db.commit()

    return PdfExportResponse(filename=path.name, lead_count=len(leads))


@router.get("/pdf/{filename}")
def download_pdf(filename: str):
    path = settings.reports_dir / filename
    if not path.exists() or path.parent != settings.reports_dir:
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(path, media_type="application/pdf", filename=filename)


@router.post("/sheets", response_model=SheetsExportResponse)
def export_sheets(payload: SheetsExportRequest, db: Session = Depends(get_db)) -> SheetsExportResponse:
    _run, _icp, leads = _load_run_leads(db, payload.run_id)

    try:
        sheet_url = export_leads_to_sheet(leads, payload.sheet_name)
    except SheetsExportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    for lead in leads:
        from datetime import datetime, timezone

        lead.exported_to_sheets_at = datetime.now(timezone.utc)
    db.commit()

    return SheetsExportResponse(sheet_url=sheet_url, lead_count=len(leads))
