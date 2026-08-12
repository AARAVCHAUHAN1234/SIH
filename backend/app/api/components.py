from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.component import BridgeComponent
from app.models.bridge import Bridge

router = APIRouter(
    prefix="/api/v1/components",
    tags=["Bridge Components"],
)


class ComponentCreate(BaseModel):
    bridge_id: UUID
    name: str
    component_type: str
    description: str | None = None


@router.post("/", status_code=201)
def create_component(
    component: ComponentCreate,
    db: Session = Depends(get_db),
):
    bridge = db.get(Bridge, component.bridge_id)

    if not bridge:
        raise HTTPException(
            status_code=404,
            detail="Bridge not found",
        )

    new_component = BridgeComponent(
        bridge_id=component.bridge_id,
        name=component.name,
        component_type=component.component_type,
        description=component.description,
    )

    db.add(new_component)
    db.commit()
    db.refresh(new_component)

    return new_component