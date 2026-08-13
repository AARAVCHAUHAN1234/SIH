from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.bridge import Bridge
from app.models.inspection import Inspection

router = APIRouter(
    prefix="/api/v1/inspections",
    tags=["Inspections"],
)


class InspectionCreate(BaseModel):
    bridge_id: UUID
    name: str
    notes: str | None = None


@router.post("/", status_code=201)
def create_inspection(
    inspection: InspectionCreate,
    db: Session = Depends(get_db),
):
    # Check that the bridge exists
    bridge = db.get(Bridge, inspection.bridge_id)

    if not bridge:
        raise HTTPException(
            status_code=404,
            detail="Bridge not found",
        )

    new_inspection = Inspection(
        bridge_id=inspection.bridge_id,
        name=inspection.name,
        notes=inspection.notes,
    )

    db.add(new_inspection)
    db.commit()
    db.refresh(new_inspection)

    return {
        "id": new_inspection.id,
        "bridge_id": new_inspection.bridge_id,
        "name": new_inspection.name,
        "status": new_inspection.status,
        "notes": new_inspection.notes,
        "created_at": new_inspection.created_at,
    }


# GET all inspections
@router.get("/")
def get_inspections(
    db: Session = Depends(get_db),
):
    inspections = db.query(Inspection).all()

    return {
        "count": len(inspections),
        "items": [
            {
                "id": inspection.id,
                "bridge_id": inspection.bridge_id,
                "name": inspection.name,
                "status": inspection.status,
                "notes": inspection.notes,
                "created_at": inspection.created_at,
            }
            for inspection in inspections
        ],
    }


# GET one inspection
@router.get("/{inspection_id}")
def get_inspection(
    inspection_id: UUID,
    db: Session = Depends(get_db),
):
    inspection = db.get(Inspection, inspection_id)

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found",
        )

    return {
        "id": inspection.id,
        "bridge_id": inspection.bridge_id,
        "name": inspection.name,
        "status": inspection.status,
        "notes": inspection.notes,
        "created_at": inspection.created_at,
    }