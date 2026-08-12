from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.bridge import Bridge


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