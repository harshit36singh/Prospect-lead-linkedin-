from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.icp import Icp
from app.schemas.icp import IcpCreate, IcpRead, IcpUpdate

router = APIRouter(prefix="/api/icps", tags=["icps"])


@router.post("", response_model=IcpRead, status_code=201)
def create_icp(payload: IcpCreate, db: Session = Depends(get_db)) -> Icp:
    icp = Icp(**payload.model_dump())
    db.add(icp)
    db.commit()
    db.refresh(icp)
    return icp


@router.get("", response_model=list[IcpRead])
def list_icps(db: Session = Depends(get_db)) -> list[Icp]:
    return db.query(Icp).order_by(Icp.created_at.desc()).all()


@router.get("/{icp_id}", response_model=IcpRead)
def get_icp(icp_id: int, db: Session = Depends(get_db)) -> Icp:
    icp = db.get(Icp, icp_id)
    if icp is None:
        raise HTTPException(status_code=404, detail="ICP not found")
    return icp


@router.put("/{icp_id}", response_model=IcpRead)
def update_icp(icp_id: int, payload: IcpUpdate, db: Session = Depends(get_db)) -> Icp:
    icp = db.get(Icp, icp_id)
    if icp is None:
        raise HTTPException(status_code=404, detail="ICP not found")
    for field, value in payload.model_dump().items():
        setattr(icp, field, value)
    db.commit()
    db.refresh(icp)
    return icp


@router.delete("/{icp_id}", status_code=204)
def delete_icp(icp_id: int, db: Session = Depends(get_db)) -> None:
    icp = db.get(Icp, icp_id)
    if icp is None:
        raise HTTPException(status_code=404, detail="ICP not found")
    db.delete(icp)
    db.commit()
