import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.finding import Finding
from app.models.inspection import Inspection
from app.models.component import BridgeComponent
from app.models.media import MediaAsset

router = APIRouter(
    prefix="/api/v1/findings",
    tags=["Findings"],
)

class FindingUpdate(BaseModel):
    component_id: uuid.UUID | None = None
    media_id: uuid.UUID | None = None
    defect_type: str | None = None
    description: str | None = None
    severity: str | None = None
    confidence: float | None = Field(
    default=None,
    ge=0.0,
    le=1.0,
)

class FindingCreate(BaseModel):
    inspection_id: uuid.UUID
    component_id: uuid.UUID | None = None
    media_id: uuid.UUID | None = None
    defect_type: str
    description: str | None = None

    severity: Literal[
        "low",
        "medium",
        "high",
        "critical",
    ] = "low"

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )


@router.post("/", status_code=201)
def create_finding(
    finding: FindingCreate,
    db: Session = Depends(get_db),
):
    # Check inspection
    inspection = db.get(Inspection, finding.inspection_id)

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found",
        )

    # Check component if supplied
    if finding.component_id:
        component = db.get(BridgeComponent, finding.component_id)

        if not component:
            raise HTTPException(
                status_code=404,
                detail="Component not found",
            )

    # Check media if supplied
    if finding.media_id:
        media = db.get(MediaAsset, finding.media_id)

        if not media:
            raise HTTPException(
                status_code=404,
                detail="Media asset not found",
            )

    new_finding = Finding(
        inspection_id=finding.inspection_id,
        component_id=finding.component_id,
        media_id=finding.media_id,
        defect_type=finding.defect_type,
        description=finding.description,
        severity=finding.severity,
        confidence=finding.confidence,
    )

    db.add(new_finding)
    db.commit()
    db.refresh(new_finding)

    return {
        "id": new_finding.id,
        "inspection_id": new_finding.inspection_id,
        "component_id": new_finding.component_id,
        "media_id": new_finding.media_id,
        "defect_type": new_finding.defect_type,
        "description": new_finding.description,
        "severity": new_finding.severity,
        "confidence": new_finding.confidence,
        "created_at": new_finding.created_at,
    }
@router.get("/{finding_id}")
def get_finding(
    finding_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    finding = db.get(Finding, finding_id)

    if not finding:
        raise HTTPException(
            status_code=404,
            detail="Finding not found",
        )

    return {
        "id": finding.id,
        "inspection_id": finding.inspection_id,
        "component_id": finding.component_id,
        "media_id": finding.media_id,
        "defect_type": finding.defect_type,
        "description": finding.description,
        "severity": finding.severity,
        "confidence": finding.confidence,
        "created_at": finding.created_at,
    }
@router.get("/")
def get_findings(
    inspection_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    # Check inspection exists
    inspection = db.get(Inspection, inspection_id)

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found",
        )

    findings = (
        db.query(Finding)
        .filter(Finding.inspection_id == inspection_id)
        .all()
    )

    return [
        {
            "id": finding.id,
            "inspection_id": finding.inspection_id,
            "component_id": finding.component_id,
            "media_id": finding.media_id,
            "defect_type": finding.defect_type,
            "description": finding.description,
            "severity": finding.severity,
            "confidence": finding.confidence,
            "created_at": finding.created_at,
        }
        for finding in findings
    ]
@router.delete("/{finding_id}", status_code=204)
def delete_finding(
    finding_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    finding = db.get(Finding, finding_id)

    if not finding:
        raise HTTPException(
            status_code=404,
            detail="Finding not found",
        )

    db.delete(finding)
    db.commit()

    return None
