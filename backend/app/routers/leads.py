from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.company import Company, Contact
from app.models.lead import Lead
from app.schemas.lead import LeadRead

router = APIRouter(prefix="/api/leads", tags=["leads"])

SORTABLE_FIELDS = {
    "score": Lead.score,
    "created_at": Lead.created_at,
}


@router.get("", response_model=list[LeadRead])
def list_leads(
    icp_id: int | None = None,
    run_id: int | None = None,
    min_score: int | None = None,
    grade: str | None = None,
    verification_status: str | None = None,
    company: str | None = None,
    title: str | None = None,
    include_duplicates: bool = False,
    sort_by: str = "score",
    order: str = "desc",
    db: Session = Depends(get_db),
) -> list[Lead]:
    query = db.query(Lead).options(joinedload(Lead.company), joinedload(Lead.contact))

    if icp_id is not None:
        query = query.filter(Lead.icp_id == icp_id)
    if run_id is not None:
        query = query.filter(Lead.pipeline_run_id == run_id)
    if min_score is not None:
        query = query.filter(Lead.score >= min_score)
    if grade is not None:
        query = query.filter(Lead.grade == grade)
    if not include_duplicates:
        query = query.filter(Lead.is_duplicate.is_(False))
    if company is not None:
        query = query.join(Lead.company).filter(Company.name.ilike(f"%{company}%"))
    if title is not None:
        query = query.join(Lead.contact).filter(Contact.title.ilike(f"%{title}%"))
    if verification_status is not None:
        query = query.join(Lead.contact).filter(
            Contact.email_verification_status == verification_status
        )

    sort_column = SORTABLE_FIELDS.get(sort_by, Lead.score)
    query = query.order_by(sort_column.desc() if order == "desc" else sort_column.asc())

    return query.all()


@router.get("/{lead_id}", response_model=LeadRead)
def get_lead(lead_id: int, db: Session = Depends(get_db)) -> Lead:
    lead = (
        db.query(Lead)
        .options(joinedload(Lead.company), joinedload(Lead.contact))
        .filter(Lead.id == lead_id)
        .first()
    )
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
