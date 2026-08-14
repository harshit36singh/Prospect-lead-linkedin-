from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.icp import Icp
from app.models.pipeline_run import PipelineRun
from app.pipeline.runner import run_pipeline
from app.schemas.pipeline_run import PipelineRunCreate, PipelineRunRead

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


@router.post("/runs", response_model=PipelineRunRead, status_code=202)
def create_run(
    payload: PipelineRunCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> PipelineRun:
    icp = db.get(Icp, payload.icp_id)
    if icp is None:
        raise HTTPException(status_code=404, detail="ICP not found")

    run = PipelineRun(icp_id=payload.icp_id, status="pending")
    db.add(run)
    db.commit()
    db.refresh(run)

    background_tasks.add_task(run_pipeline, run.id)
    return run


@router.get("/runs", response_model=list[PipelineRunRead])
def list_runs(icp_id: int | None = None, db: Session = Depends(get_db)) -> list[PipelineRun]:
    query = db.query(PipelineRun)
    if icp_id is not None:
        query = query.filter(PipelineRun.icp_id == icp_id)
    return query.order_by(PipelineRun.created_at.desc()).all()


@router.get("/runs/{run_id}", response_model=PipelineRunRead)
def get_run(run_id: int, db: Session = Depends(get_db)) -> PipelineRun:
    run = db.get(PipelineRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    return run
