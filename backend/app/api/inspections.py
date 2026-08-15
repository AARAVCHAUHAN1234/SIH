from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models.finding import Finding
from app.core.database import get_db
from app.models.bridge import Bridge
from app.models.inspection import Inspection
from app.models.component import BridgeComponent
from app.models.media import MediaAsset
from app.models.finding import Finding
from app.models.component import BridgeComponent
from app.models.media import MediaAsset
from fastapi.responses import Response
from app.services.report_service import generate_inspection_report
router = APIRouter(
    prefix="/api/v1/inspections",
    tags=["Inspections"],
)

class InspectionStatusUpdate(BaseModel):
    status: str

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
@router.get("/{inspection_id}/summary")
def get_inspection_summary(
    inspection_id: UUID,
    db: Session = Depends(get_db),
):
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

    media_count = (
        db.query(MediaAsset)
        .filter(MediaAsset.inspection_id == inspection_id)
        .count()
    )

    component_count = (
        db.query(BridgeComponent)
        .filter(
            BridgeComponent.bridge_id == inspection.bridge_id
        )
        .count()
    )

    summary = {
        "total": len(findings),
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    for finding in findings:
        severity = finding.severity.lower()

        if severity in summary:
            summary[severity] += 1

    return {
        "inspection": {
            "id": inspection.id,
            "bridge_id": inspection.bridge_id,
            "name": inspection.name,
            "status": inspection.status,
            "notes": inspection.notes,
            "created_at": inspection.created_at,
        },
        "statistics": {
            "component_count": component_count,
            "media_count": media_count,
            "finding_count": len(findings),
        },
        "findings": summary,
    }
@router.patch("/{inspection_id}/status")
def update_inspection_status(
    inspection_id: UUID,
    status_update: InspectionStatusUpdate,
    db: Session = Depends(get_db),
):
    inspection = db.get(Inspection, inspection_id)

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found",
        )

    allowed_statuses = {
        "created",
        "processing",
        "completed",
        "reviewed",
    }

    new_status = status_update.status.lower()

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed statuses: {sorted(allowed_statuses)}",
        )

    current_status = inspection.status.lower()

    allowed_transitions = {
        "created": ["processing"],
        "processing": ["completed"],
        "completed": ["reviewed"],
        "reviewed": [],
    }

    if new_status not in allowed_transitions[current_status]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change inspection status from '{current_status}' to '{new_status}'",
        )

    inspection.status = new_status

    db.commit()
    db.refresh(inspection)

    return {
        "id": inspection.id,
        "bridge_id": inspection.bridge_id,
        "name": inspection.name,
        "status": inspection.status,
        "notes": inspection.notes,
        "created_at": inspection.created_at,
    }
@router.get("/{inspection_id}/risk")
def get_inspection_risk(
    inspection_id: UUID,
    db: Session = Depends(get_db),
):
    inspection = db.get(Inspection, inspection_id)

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found",
        )

    findings = (
        db.query(Finding)
        .filter(
            Finding.inspection_id == inspection_id
        )
        .all()
    )

    severity_weights = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }

    total_score = 0.0

    for finding in findings:
        severity = finding.severity.lower()

        weight = severity_weights.get(
            severity,
            0,
        )

        confidence = (
            finding.confidence
            if finding.confidence is not None
            else 1.0
        )

        total_score += weight * confidence

    # Simple inspection-level risk classification
    if total_score >= 4:
        risk_level = "high"
        priority = "immediate_review"
    elif total_score >= 2:
        risk_level = "medium"
        priority = "scheduled_review"
    elif total_score > 0:
        risk_level = "low"
        priority = "routine_review"
    else:
        risk_level = "none"
        priority = "no_findings"

    return {
        "inspection_id": inspection.id,
        "finding_count": len(findings),
        "risk_score": round(total_score, 2),
        "risk_level": risk_level,
        "priority": priority,
        "human_review_required": True,
    }
@router.get("/{inspection_id}/intelligence")
def get_inspection_intelligence(
    inspection_id: UUID,
    db: Session = Depends(get_db),
):
    inspection = db.get(Inspection, inspection_id)

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found",
        )

    # --------------------------------------------------
    # Findings
    # --------------------------------------------------

    findings = (
        db.query(Finding)
        .filter(
            Finding.inspection_id == inspection_id
        )
        .all()
    )

    severity_weights = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }

    severity_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    base_risk = 0.0
    highest_severity = None
    highest_rank = 0

    for finding in findings:

        severity = finding.severity.lower()

        if severity in severity_counts:
            severity_counts[severity] += 1

        rank = severity_weights.get(
            severity,
            0,
        )

        confidence = (
            finding.confidence
            if finding.confidence is not None
            else 1.0
        )

        base_risk += rank * confidence

        if rank > highest_rank:
            highest_rank = rank
            highest_severity = finding.severity

    base_risk = round(base_risk, 2)

    # --------------------------------------------------
    # Inspection risk classification
    # --------------------------------------------------

    if highest_rank >= 4:
        risk_level = "high"
        priority = "urgent_review"

    elif highest_rank >= 3:
        risk_level = "high"
        priority = "urgent_review"

    elif highest_rank >= 2:
        risk_level = "medium"
        priority = "scheduled_review"

    elif highest_rank > 0:
        risk_level = "low"
        priority = "routine_monitoring"

    else:
        risk_level = "none"
        priority = "none"

    human_review_required = (
        highest_rank >= 3
    )

    # --------------------------------------------------
    # Component information
    # --------------------------------------------------

    component_ids = {
        finding.component_id
        for finding in findings
        if finding.component_id is not None
    }

    components = []

    for component_id in component_ids:

        component = db.get(
            BridgeComponent,
            component_id,
        )

        if not component:
            continue

        component_findings = [
            finding
            for finding in findings
            if finding.component_id == component_id
        ]

        component_risk = 0.0

        for finding in component_findings:

            weight = severity_weights.get(
                finding.severity.lower(),
                0,
            )

            confidence = (
                finding.confidence
                if finding.confidence is not None
                else 1.0
            )

            component_risk += (
                weight * confidence
            )

        component_risk = round(
            component_risk,
            2,
        )

        if component_risk >= 4:
            condition = "poor"
        elif component_risk >= 2:
            condition = "fair"
        elif component_risk > 0:
            condition = "good"
        else:
            condition = "no_findings"

        components.append({
            "component_id": component.id,
            "component_name": component.name,
            "component_type": component.component_type,
            "finding_count": len(
                component_findings
            ),
            "risk_score": component_risk,
            "condition": condition,
        })

    # --------------------------------------------------
    # Media
    # --------------------------------------------------

    media_count = (
        db.query(MediaAsset)
        .filter(
            MediaAsset.inspection_id
            == inspection_id
        )
        .count()
    )

    # --------------------------------------------------
    # Final intelligence response
    # --------------------------------------------------

    return {
        "inspection": {
            "id": inspection.id,
            "bridge_id": inspection.bridge_id,
            "name": inspection.name,
            "status": inspection.status,
            "created_at": inspection.created_at,
        },

        "intelligence": {
            "finding_count": len(findings),
            "media_count": media_count,
            "highest_severity": highest_severity,
            "risk_score": base_risk,
            "risk_level": risk_level,
            "priority": priority,
            "human_review_required": (
                human_review_required
            ),
        },

        "severity_summary": severity_counts,

        "components": components,

        "recommendation": (
            "Immediate human engineering review required"
            if human_review_required
            else "Routine inspection monitoring recommended"
        ),
    }
@router.get("/{inspection_id}/report-data")
def get_inspection_report_data(
    inspection_id: UUID,
    db: Session = Depends(get_db),
):
    inspection = db.get(Inspection, inspection_id)

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found",
        )

    bridge = db.get(
        Bridge,
        inspection.bridge_id,
    )

    if not bridge:
        raise HTTPException(
            status_code=404,
            detail="Bridge not found",
        )

    # --------------------------------------------------
    # Findings
    # --------------------------------------------------

    findings = (
        db.query(Finding)
        .filter(
            Finding.inspection_id == inspection_id
        )
        .order_by(Finding.created_at.asc())
        .all()
    )

    severity_weights = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }

    severity_summary = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    risk_score = 0.0
    highest_severity = None
    highest_rank = 0

    finding_items = []

    for finding in findings:

        severity = finding.severity.lower()

        if severity in severity_summary:
            severity_summary[severity] += 1

        rank = severity_weights.get(
            severity,
            0,
        )

        confidence = (
            finding.confidence
            if finding.confidence is not None
            else 1.0
        )

        risk_score += rank * confidence

        if rank > highest_rank:
            highest_rank = rank
            highest_severity = finding.severity

        component_name = None

        if finding.component_id:
            component = db.get(
                BridgeComponent,
                finding.component_id,
            )

            if component:
                component_name = component.name

        media_filename = None

        if finding.media_id:
            media = db.get(
                MediaAsset,
                finding.media_id,
            )

            if media:
                media_filename = media.original_filename

        finding_items.append({
            "id": finding.id,
            "defect_type": finding.defect_type,
            "description": finding.description,
            "severity": finding.severity,
            "confidence": finding.confidence,
            "component_id": finding.component_id,
            "component_name": component_name,
            "media_id": finding.media_id,
            "media_filename": media_filename,
            "created_at": finding.created_at,
        })

    risk_score = round(
        risk_score,
        2,
    )

    # --------------------------------------------------
    # Risk classification
    # --------------------------------------------------

    if highest_rank >= 4:
        risk_level = "high"
        priority = "urgent_review"

    elif highest_rank >= 3:
        risk_level = "high"
        priority = "urgent_review"

    elif highest_rank >= 2:
        risk_level = "medium"
        priority = "scheduled_review"

    elif highest_rank > 0:
        risk_level = "low"
        priority = "routine_monitoring"

    else:
        risk_level = "none"
        priority = "none"

    human_review_required = (
        highest_rank >= 3
    )

    # --------------------------------------------------
    # Media
    # --------------------------------------------------

    media_assets = (
        db.query(MediaAsset)
        .filter(
            MediaAsset.inspection_id
            == inspection_id
        )
        .order_by(
            MediaAsset.created_at.asc()
        )
        .all()
    )

    media_items = [
        {
            "id": media.id,
            "filename": media.original_filename,
            "media_type": media.media_type,
            "file_size": media.file_size,
            "storage_path": media.storage_path,
            "processing_status": media.processing_status,
            "created_at": media.created_at,
        }
        for media in media_assets
    ]

    # --------------------------------------------------
    # Components involved in this inspection
    # --------------------------------------------------

    component_ids = {
        finding.component_id
        for finding in findings
        if finding.component_id is not None
    }

    components = []

    for component_id in component_ids:

        component = db.get(
            BridgeComponent,
            component_id,
        )

        if not component:
            continue

        component_findings = [
            finding
            for finding in findings
            if finding.component_id
            == component.id
        ]

        component_risk = 0.0

        for finding in component_findings:

            weight = severity_weights.get(
                finding.severity.lower(),
                0,
            )

            confidence = (
                finding.confidence
                if finding.confidence is not None
                else 1.0
            )

            component_risk += (
                weight * confidence
            )

        component_risk = round(
            component_risk,
            2,
        )

        if component_risk >= 4:
            condition = "poor"
        elif component_risk >= 2:
            condition = "fair"
        elif component_risk > 0:
            condition = "good"
        else:
            condition = "no_findings"

        components.append({
            "id": component.id,
            "name": component.name,
            "type": component.component_type,
            "description": component.description,
            "finding_count": len(
                component_findings
            ),
            "risk_score": component_risk,
            "condition": condition,
        })

    # --------------------------------------------------
    # Historical information
    # --------------------------------------------------

    inspection_count = (
        db.query(Inspection)
        .filter(
            Inspection.bridge_id
            == inspection.bridge_id
        )
        .count()
    )

    previous_inspections = (
        db.query(Inspection)
        .filter(
            Inspection.bridge_id
            == inspection.bridge_id,
            Inspection.created_at
            < inspection.created_at,
        )
        .order_by(
            Inspection.created_at.asc()
        )
        .all()
    )

    # --------------------------------------------------
    # Final report payload
    # --------------------------------------------------

    return {
        "report": {
            "title": "Bridge Inspection Report",
            "generated_for": bridge.name,
            "inspection_name": inspection.name,
        },

        "bridge": {
            "id": bridge.id,
            "name": bridge.name,
            "bridge_type": bridge.bridge_type,
            "location": bridge.location,
            "latitude": bridge.latitude,
            "longitude": bridge.longitude,
            "created_at": bridge.created_at,
        },

        "inspection": {
            "id": inspection.id,
            "name": inspection.name,
            "status": inspection.status,
            "notes": inspection.notes,
            "created_at": inspection.created_at,
        },

        "overview": {
            "inspection_count": inspection_count,
            "previous_inspection_count": len(
                previous_inspections
            ),
            "finding_count": len(findings),
            "media_count": len(media_assets),
            "component_count": len(components),
        },

        "risk_assessment": {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "priority": priority,
            "highest_severity": highest_severity,
            "human_review_required": (
                human_review_required
            ),
        },

        "severity_summary": severity_summary,

        "findings": finding_items,

        "components": components,

        "media": media_items,

        "report_notes": (
            "This report contains AI-assisted inspection "
            "information and requires qualified human "
            "engineering review before structural decisions."
        ),
    }
@router.get("/{inspection_id}/report")
def generate_inspection_pdf(
    inspection_id: UUID,
    db: Session = Depends(get_db),
):
    inspection = db.get(
        Inspection,
        inspection_id,
    )

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found",
        )

    bridge = db.get(
        Bridge,
        inspection.bridge_id,
    )

    if not bridge:
        raise HTTPException(
            status_code=404,
            detail="Bridge not found",
        )

    findings = (
        db.query(Finding)
        .filter(
            Finding.inspection_id == inspection_id
        )
        .order_by(Finding.created_at.asc())
        .all()
    )

    media_assets = (
        db.query(MediaAsset)
        .filter(
            MediaAsset.inspection_id
            == inspection_id
        )
        .order_by(
            MediaAsset.created_at.asc()
        )
        .all()
    )

    severity_weights = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }

    severity_summary = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    risk_score = 0.0
    highest_rank = 0
    highest_severity = None

    finding_items = []

    for finding in findings:

        severity = finding.severity.lower()

        if severity in severity_summary:
            severity_summary[severity] += 1

        rank = severity_weights.get(
            severity,
            0,
        )

        confidence = (
            finding.confidence
            if finding.confidence is not None
            else 1.0
        )

        risk_score += (
            rank * confidence
        )

        if rank > highest_rank:
            highest_rank = rank
            highest_severity = finding.severity

        component_name = None

        if finding.component_id:

            component = db.get(
                BridgeComponent,
                finding.component_id,
            )

            if component:
                component_name = component.name

        finding_items.append({
            "id": finding.id,
            "defect_type": finding.defect_type,
            "description": finding.description,
            "severity": finding.severity,
            "confidence": finding.confidence,
            "component_id": finding.component_id,
            "component_name": component_name,
            "media_id": finding.media_id,
            "media_filename": None,
            "created_at": finding.created_at,
        })

    risk_score = round(
        risk_score,
        2,
    )

    if highest_rank >= 3:
        risk_level = "high"
        priority = "urgent_review"
    elif highest_rank == 2:
        risk_level = "medium"
        priority = "scheduled_review"
    elif highest_rank == 1:
        risk_level = "low"
        priority = "routine_monitoring"
    else:
        risk_level = "none"
        priority = "none"

    components = []

    component_ids = {
        finding.component_id
        for finding in findings
        if finding.component_id
    }

    for component_id in component_ids:

        component = db.get(
            BridgeComponent,
            component_id,
        )

        if not component:
            continue

        component_findings = [
            finding
            for finding in findings
            if finding.component_id
            == component.id
        ]

        component_risk = sum(
            severity_weights.get(
                finding.severity.lower(),
                0,
            )
            * (
                finding.confidence
                if finding.confidence is not None
                else 1.0
            )
            for finding in component_findings
        )

        component_risk = round(
            component_risk,
            2,
        )

        if component_risk >= 4:
            condition = "poor"
        elif component_risk >= 2:
            condition = "fair"
        elif component_risk > 0:
            condition = "good"
        else:
            condition = "no_findings"

        components.append({
            "id": component.id,
            "name": component.name,
            "type": component.component_type,
            "description": component.description,
            "finding_count": len(
                component_findings
            ),
            "risk_score": component_risk,
            "condition": condition,
        })

    inspection_count = (
        db.query(Inspection)
        .filter(
            Inspection.bridge_id
            == inspection.bridge_id
        )
        .count()
    )

    report_data = {
        "report": {
            "title": "Bridge Inspection Report",
            "generated_for": bridge.name,
            "inspection_name": inspection.name,
        },
        "bridge": {
            "id": bridge.id,
            "name": bridge.name,
            "bridge_type": bridge.bridge_type,
            "location": bridge.location,
            "latitude": bridge.latitude,
            "longitude": bridge.longitude,
            "created_at": bridge.created_at,
        },
        "inspection": {
            "id": inspection.id,
            "name": inspection.name,
            "status": inspection.status,
            "notes": inspection.notes,
            "created_at": inspection.created_at,
        },
        "overview": {
            "inspection_count": inspection_count,
            "previous_inspection_count": max(
                inspection_count - 1,
                0,
            ),
            "finding_count": len(findings),
            "media_count": len(media_assets),
            "component_count": len(components),
        },
        "risk_assessment": {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "priority": priority,
            "highest_severity": highest_severity,
            "human_review_required": (
                highest_rank >= 3
            ),
        },
        "severity_summary": severity_summary,
        "findings": finding_items,
        "components": components,
        "media": [
            {
                "id": media.id,
                "filename": media.original_filename,
                "media_type": media.media_type,
                "file_size": media.file_size,
                "storage_path": media.storage_path,
                "processing_status": media.processing_status,
                "created_at": media.created_at,
            }
            for media in media_assets
        ],
        "report_notes": (
            "This report contains AI-assisted inspection "
            "information and requires qualified human "
            "engineering review before structural decisions."
        ),
    }

    pdf_bytes = generate_inspection_report(
        report_data
    )

    filename = (
        f"inspection_{inspection.id}.pdf"
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            )
        },
    )
class InspectionStatusUpdate(BaseModel):
    status: str
@router.patch("/{inspection_id}/status")
def update_inspection_status(
    inspection_id: UUID,
    data: InspectionStatusUpdate,
    db: Session = Depends(get_db),
):
    inspection = db.get(Inspection, inspection_id)

    if not inspection:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found",
        )

    allowed_statuses = {
        "created",
        "processing",
        "completed",
        "failed",
    }

    if data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed statuses: {sorted(allowed_statuses)}",
        )

    inspection.status = data.status

    db.commit()
    db.refresh(inspection)

    return {
        "id": inspection.id,
        "status": inspection.status,
        "message": "Inspection status updated successfully",
    } 