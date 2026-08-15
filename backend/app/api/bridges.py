from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.bridge import Bridge
from app.models.component import BridgeComponent

from app.models.inspection import Inspection
from app.models.finding import Finding

router = APIRouter(
    prefix="/api/v1/bridges",
    tags=["Bridges"],
)


class BridgeCreate(BaseModel):
    project_id: UUID
    name: str
    bridge_type: str | None = None
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None


@router.post("/", status_code=201)
def create_bridge(
    bridge: BridgeCreate,
    db: Session = Depends(get_db),
):
    new_bridge = Bridge(
        project_id=bridge.project_id,
        name=bridge.name,
        bridge_type=bridge.bridge_type,
        location=bridge.location,
        latitude=bridge.latitude,
        longitude=bridge.longitude,
    )

    db.add(new_bridge)
    db.commit()
    db.refresh(new_bridge)

    return {
        "message": "Bridge created successfully",
        "bridge": {
            "id": str(new_bridge.id),
            "project_id": str(new_bridge.project_id),
            "name": new_bridge.name,
            "bridge_type": new_bridge.bridge_type,
            "location": new_bridge.location,
            "latitude": new_bridge.latitude,
            "longitude": new_bridge.longitude,
            "created_at": new_bridge.created_at,
        },
    }


@router.get("/")
def get_bridges(
    db: Session = Depends(get_db),
):
    bridges = db.query(Bridge).all()

    return {
        "items": [
            {
                "id": str(bridge.id),
                "project_id": str(bridge.project_id),
                "name": bridge.name,
                "bridge_type": bridge.bridge_type,
                "location": bridge.location,
                "latitude": bridge.latitude,
                "longitude": bridge.longitude,
                "created_at": bridge.created_at,
            }
            for bridge in bridges
        ]
    }


@router.get("/{bridge_id}")
def get_bridge(
    bridge_id: UUID,
    db: Session = Depends(get_db),
):
    bridge = db.query(Bridge).filter(Bridge.id == bridge_id).first()

    if not bridge:
        raise HTTPException(
            status_code=404,
            detail="Bridge not found",
        )

    return {
        "id": str(bridge.id),
        "project_id": str(bridge.project_id),
        "name": bridge.name,
        "bridge_type": bridge.bridge_type,
        "location": bridge.location,
        "latitude": bridge.latitude,
        "longitude": bridge.longitude,
        "created_at": bridge.created_at,
    }


@router.delete("/{bridge_id}", status_code=204)
def delete_bridge(
    bridge_id: UUID,
    db: Session = Depends(get_db),
):
    bridge = db.query(Bridge).filter(Bridge.id == bridge_id).first()

    if not bridge:
        raise HTTPException(
            status_code=404,
            detail="Bridge not found",
        )

    db.delete(bridge)
    db.commit()

    return None
@router.get("/{bridge_id}/findings/history")
def get_bridge_finding_history(
    bridge_id: UUID,
    db: Session = Depends(get_db),
):
    # Check bridge exists
    bridge = db.get(Bridge, bridge_id)

    if not bridge:
        raise HTTPException(
            status_code=404,
            detail="Bridge not found",
        )

    # Get all findings belonging to inspections
    # of this bridge
    findings = (
        db.query(Finding, Inspection)
        .join(
            Inspection,
            Finding.inspection_id == Inspection.id,
        )
        .filter(
            Inspection.bridge_id == bridge_id
        )
        .order_by(
            Inspection.created_at.asc(),
            Finding.created_at.asc(),
        )
        .all()
    )

    return {
        "bridge_id": bridge_id,
        "total_findings": len(findings),
        "history": [
            {
                "inspection_id": inspection.id,
                "inspection_name": inspection.name,
                "inspection_date": inspection.created_at,
                "finding_id": finding.id,
                "defect_type": finding.defect_type,
                "description": finding.description,
                "severity": finding.severity,
                "confidence": finding.confidence,
                "created_at": finding.created_at,
            }
            for finding, inspection in findings
        ],
    }
@router.get("/{bridge_id}/comparison")
def compare_bridge_inspections(
    bridge_id: UUID,
    db: Session = Depends(get_db),
):
    # Check bridge exists
    bridge = db.get(Bridge, bridge_id)

    if not bridge:
        raise HTTPException(
            status_code=404,
            detail="Bridge not found",
        )

    # Get inspections in chronological order
    inspections = (
        db.query(Inspection)
        .filter(Inspection.bridge_id == bridge_id)
        .order_by(Inspection.created_at.asc())
        .all()
    )

    if len(inspections) < 2:
        return {
            "bridge_id": bridge_id,
            "inspection_count": len(inspections),
            "comparisons": [],
            "message": "At least two inspections are required for comparison",
        }

    comparisons = []

    for i in range(1, len(inspections)):
        previous = inspections[i - 1]
        current = inspections[i]

        previous_findings = (
            db.query(Finding)
            .filter(
                Finding.inspection_id == previous.id
            )
            .all()
        )

        current_findings = (
            db.query(Finding)
            .filter(
                Finding.inspection_id == current.id
            )
            .all()
        )

        # Compare findings by defect type
        previous_by_type = {}

        for finding in previous_findings:
            previous_by_type.setdefault(
                finding.defect_type.lower(),
                []
            ).append(finding)

        for current_finding in current_findings:
            defect_key = current_finding.defect_type.lower()

            previous_matches = previous_by_type.get(
                defect_key,
                []
            )

            if not previous_matches:
                comparisons.append({
                    "defect_type": current_finding.defect_type,
                    "previous_severity": None,
                    "current_severity": current_finding.severity,
                    "progression": "new",
                    "previous_inspection_id": previous.id,
                    "current_inspection_id": current.id,
                })
                continue

            previous_finding = previous_matches[0]

            severity_rank = {
                "low": 1,
                "medium": 2,
                "high": 3,
                "critical": 4,
            }

            previous_rank = severity_rank.get(
                previous_finding.severity.lower(),
                0,
            )

            current_rank = severity_rank.get(
                current_finding.severity.lower(),
                0,
            )

            if current_rank > previous_rank:
                progression = "worsened"
            elif current_rank < previous_rank:
                progression = "improved"
            else:
                progression = "unchanged"

            comparisons.append({
                "defect_type": current_finding.defect_type,
                "previous_severity": previous_finding.severity,
                "current_severity": current_finding.severity,
                "progression": progression,
                "previous_inspection_id": previous.id,
                "current_inspection_id": current.id,
                "previous_finding_id": previous_finding.id,
                "current_finding_id": current_finding.id,
            })

    return {
        "bridge_id": bridge_id,
        "inspection_count": len(inspections),
        "comparisons": comparisons,
    }
@router.get("/{bridge_id}/components/condition")
def get_component_conditions(
    bridge_id: UUID,
    db: Session = Depends(get_db),
):
    bridge = db.get(Bridge, bridge_id)

    if not bridge:
        raise HTTPException(
            status_code=404,
            detail="Bridge not found",
        )

    components = (
        db.query(BridgeComponent)
        .filter(BridgeComponent.bridge_id == bridge_id)
        .all()
    )

    results = []

    severity_weights = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }

    for component in components:

        findings = (
            db.query(Finding)
            .join(Inspection)
            .filter(
                Finding.component_id == component.id,
                Inspection.bridge_id == bridge_id,
            )
            .all()
        )

        risk_score = 0.0

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

            risk_score += weight * confidence

        if risk_score >= 4:
            condition = "poor"
            priority = "high"
        elif risk_score >= 2:
            condition = "fair"
            priority = "medium"
        elif risk_score > 0:
            condition = "good"
            priority = "low"
        else:
            condition = "no_findings"
            priority = "none"

        results.append({
            "component_id": component.id,
            "component_name": component.name,
            "component_type": component.component_type,
            "finding_count": len(findings),
            "risk_score": round(risk_score, 2),
            "condition": condition,
            "priority": priority,
        })

    return {
        "bridge_id": bridge.id,
        "component_count": len(results),
        "components": results,
    }
@router.get("/{bridge_id}/condition")
def get_bridge_condition(
    bridge_id: UUID,
    db: Session = Depends(get_db),
):
    bridge = db.get(Bridge, bridge_id)

    if not bridge:
        raise HTTPException(
            status_code=404,
            detail="Bridge not found",
        )

    components = (
        db.query(BridgeComponent)
        .filter(
            BridgeComponent.bridge_id == bridge_id
        )
        .all()
    )

    severity_weights = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }

    total_findings = 0
    total_risk = 0.0
    component_results = []

    for component in components:

        findings = (
            db.query(Finding)
            .join(Inspection)
            .filter(
                Finding.component_id == component.id,
                Inspection.bridge_id == bridge_id,
            )
            .all()
        )

        component_risk = 0.0

        for finding in findings:
            weight = severity_weights.get(
                finding.severity.lower(),
                0,
            )

            confidence = (
                finding.confidence
                if finding.confidence is not None
                else 1.0
            )

            component_risk += weight * confidence

        total_findings += len(findings)
        total_risk += component_risk

        component_results.append({
            "component_id": component.id,
            "component_name": component.name,
            "risk_score": round(component_risk, 2),
            "finding_count": len(findings),
        })

    total_risk = round(total_risk, 2)

    if total_risk >= 8:
        condition = "critical"
        priority = "immediate"
    elif total_risk >= 4:
        condition = "poor"
        priority = "high"
    elif total_risk > 0:
        condition = "fair"
        priority = "medium"
    else:
        condition = "good"
        priority = "low"

    human_review_required = (
        condition in ["critical", "poor", "fair"]
    )

    return {
        "bridge_id": bridge.id,
        "bridge_name": bridge.name,
        "component_count": len(components),
        "finding_count": total_findings,
        "risk_score": total_risk,
        "condition": condition,
        "priority": priority,
        "human_review_required": human_review_required,
        "components": component_results,
    }
@router.get("/{bridge_id}/priority")
def get_bridge_inspection_priority(
    bridge_id: UUID,
    db: Session = Depends(get_db),
):
    bridge = db.get(Bridge, bridge_id)

    if not bridge:
        raise HTTPException(
            status_code=404,
            detail="Bridge not found",
        )

    components = (
        db.query(BridgeComponent)
        .filter(
            BridgeComponent.bridge_id == bridge_id
        )
        .all()
    )

    severity_weights = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }

    priorities = []

    for component in components:

        findings = (
            db.query(Finding)
            .join(Inspection)
            .filter(
                Finding.component_id == component.id,
                Inspection.bridge_id == bridge_id,
            )
            .all()
        )

        risk_score = 0.0
        highest_severity = None
        highest_rank = 0

        for finding in findings:
            severity = finding.severity.lower()
            rank = severity_weights.get(severity, 0)

            confidence = (
                finding.confidence
                if finding.confidence is not None
                else 1.0
            )

            risk_score += rank * confidence

            if rank > highest_rank:
                highest_rank = rank
                highest_severity = finding.severity

        risk_score = round(risk_score, 2)

        if highest_rank >= 4 or risk_score >= 8:
            priority = "critical"
        elif highest_rank >= 3 or risk_score >= 4:
            priority = "high"
        elif highest_rank >= 2 or risk_score > 0:
            priority = "medium"
        else:
            priority = "low"

        priorities.append({
            "component_id": component.id,
            "component_name": component.name,
            "component_type": component.component_type,
            "finding_count": len(findings),
            "highest_severity": highest_severity,
            "risk_score": risk_score,
            "priority": priority,
            "human_review_required": (
                highest_rank >= 3
            ),
        })

    priorities.sort(
        key=lambda item: (
            severity_weights.get(
                item["highest_severity"].lower()
                if item["highest_severity"]
                else "",
                0,
            ),
            item["risk_score"],
        ),
        reverse=True,
    )

    return {
        "bridge_id": bridge.id,
        "bridge_name": bridge.name,
        "priority_count": len(priorities),
        "priorities": priorities,
    }
@router.get("/{bridge_id}/progression")
def get_bridge_progression(
    bridge_id: UUID,
    db: Session = Depends(get_db),
):
    bridge = db.get(Bridge, bridge_id)

    if not bridge:
        raise HTTPException(
            status_code=404,
            detail="Bridge not found",
        )

    inspections = (
        db.query(Inspection)
        .filter(Inspection.bridge_id == bridge_id)
        .order_by(Inspection.created_at.asc())
        .all()
    )

    if not inspections:
        return {
            "bridge_id": bridge.id,
            "inspection_count": 0,
            "defects": [],
            "message": "No inspections found",
        }

    severity_rank = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }

    # Collect findings grouped by defect type
    defect_history = {}

    for inspection in inspections:
        findings = (
            db.query(Finding)
            .filter(
                Finding.inspection_id == inspection.id
            )
            .all()
        )

        for finding in findings:
            key = finding.defect_type.lower()

            if key not in defect_history:
                defect_history[key] = []

            defect_history[key].append({
            "defect_type": finding.defect_type,
            "inspection_id": inspection.id,
            "inspection_name": inspection.name,
            "inspection_date": inspection.created_at,
            "finding_id": finding.id,
            "severity": finding.severity,
            "confidence": finding.confidence,
            "description": finding.description,
})

    results = []

    for defect_type, history in defect_history.items():

        first = history[0]
        latest = history[-1]

        first_rank = severity_rank.get(
            first["severity"].lower(),
            0,
        )

        latest_rank = severity_rank.get(
            latest["severity"].lower(),
            0,
        )

        if len(history) == 1:
            progression = "new"
        elif latest_rank > first_rank:
            progression = "worsened"
        elif latest_rank < first_rank:
            progression = "improved"
        else:
            progression = "unchanged"

        results.append({
            "defect_type": latest["defect_type"]
            if "defect_type" in latest
            else defect_type,
            "inspection_count": len(history),
            "first_detected": {
                "inspection_id": first["inspection_id"],
                "inspection_name": first["inspection_name"],
                "inspection_date": first["inspection_date"],
                "severity": first["severity"],
            },
            "latest": {
                "inspection_id": latest["inspection_id"],
                "inspection_name": latest["inspection_name"],
                "inspection_date": latest["inspection_date"],
                "finding_id": latest["finding_id"],
                "severity": latest["severity"],
                "confidence": latest["confidence"],
            },
            "progression": progression,
            "severity_change": latest_rank - first_rank,
            "human_review_required": (
                latest_rank >= 3
            ),
            "history": history,
        })

    return {
        "bridge_id": bridge.id,
        "bridge_name": bridge.name,
        "inspection_count": len(inspections),
        "defect_count": len(results),
        "defects": results,
    }
@router.get("/{bridge_id}/risk")
def get_bridge_risk(
    bridge_id: UUID,
    db: Session = Depends(get_db),
):
    bridge = db.get(Bridge, bridge_id)

    if not bridge:
        raise HTTPException(
            status_code=404,
            detail="Bridge not found",
        )

    inspections = (
        db.query(Inspection)
        .filter(Inspection.bridge_id == bridge_id)
        .order_by(Inspection.created_at.asc())
        .all()
    )

    if not inspections:
        return {
            "bridge_id": bridge.id,
            "bridge_name": bridge.name,
            "inspection_count": 0,
            "risk_score": 0,
            "risk_level": "unknown",
            "priority": "none",
            "human_review_required": False,
        }

    findings = (
        db.query(Finding)
        .join(Inspection)
        .filter(
            Inspection.bridge_id == bridge_id
        )
        .all()
    )

    severity_weights = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }

    base_risk = 0.0
    critical_count = 0
    high_count = 0

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

        base_risk += weight * confidence

        if severity == "critical":
            critical_count += 1

        elif severity == "high":
            high_count += 1

    # Historical progression bonus
    progression_bonus = 0.0

    if len(inspections) >= 2:

        for i in range(1, len(inspections)):

            previous_findings = (
                db.query(Finding)
                .filter(
                    Finding.inspection_id
                    == inspections[i - 1].id
                )
                .all()
            )

            current_findings = (
                db.query(Finding)
                .filter(
                    Finding.inspection_id
                    == inspections[i].id
                )
                .all()
            )

            previous_by_type = {}

            for finding in previous_findings:
                previous_by_type.setdefault(
                    finding.defect_type.lower(),
                    [],
                ).append(finding)

            for current in current_findings:

                matches = previous_by_type.get(
                    current.defect_type.lower(),
                    [],
                )

                if not matches:
                    continue

                previous = matches[0]

                previous_rank = severity_weights.get(
                    previous.severity.lower(),
                    0,
                )

                current_rank = severity_weights.get(
                    current.severity.lower(),
                    0,
                )

                if current_rank > previous_rank:
                    progression_bonus += 2.0

                elif current_rank < previous_rank:
                    progression_bonus -= 0.5

    # Recurring finding bonus
    recurrence_bonus = 0.0

    defect_types = {}

    for finding in findings:
        key = finding.defect_type.lower()

        defect_types.setdefault(
            key,
            0,
        )

        defect_types[key] += 1

    for count in defect_types.values():

        if count >= 2:
            recurrence_bonus += 1.0

    risk_score = (
        base_risk
        + progression_bonus
        + recurrence_bonus
    )

    risk_score = round(
        max(risk_score, 0),
        2,
    )

    # Risk classification
    if risk_score >= 10 or critical_count >= 2:
        risk_level = "critical"
        priority = "immediate_review"

    elif risk_score >= 6 or critical_count >= 1:
        risk_level = "high"
        priority = "urgent_review"

    elif risk_score >= 3:
        risk_level = "medium"
        priority = "scheduled_review"

    elif risk_score > 0:
        risk_level = "low"
        priority = "routine_monitoring"

    else:
        risk_level = "none"
        priority = "none"

    human_review_required = (
        critical_count > 0
        or high_count > 0
        or progression_bonus > 0
    )

    return {
        "bridge_id": bridge.id,
        "bridge_name": bridge.name,
        "inspection_count": len(inspections),
        "finding_count": len(findings),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "priority": priority,
        "human_review_required": human_review_required,
        "risk_breakdown": {
            "base_risk": round(base_risk, 2),
            "progression_bonus": round(
                progression_bonus,
                2,
            ),
            "recurrence_bonus": round(
                recurrence_bonus,
                2,
            ),
            "critical_findings": critical_count,
            "high_findings": high_count,
        },
    }