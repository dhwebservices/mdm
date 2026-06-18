from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import Principal, current_principal, require_permission
from app.db.session import get_db
from app.models.entities import Device
from app.repositories.devices import DeviceRepository
from app.schemas.common import AssignGroupRequest, AssignUserRequest, DeviceCreate, DeviceRead
from app.services.devices import DeviceService

router = APIRouter()


@router.get("", response_model=list[DeviceRead])
def list_devices(
    principal: Principal = Depends(require_permission("devices:read")),
    db: Session = Depends(get_db),
) -> list[Device]:
    return DeviceRepository(db).list(UUID(principal.tenant_id) if principal.tenant_id else None)


@router.post("", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
def create_device(
    body: DeviceCreate,
    principal: Principal = Depends(require_permission("devices:write")),
    db: Session = Depends(get_db),
) -> Device:
    try:
        device = DeviceService(db).create(
            tenant_id=UUID(principal.tenant_id) if principal.tenant_id else None,
            serial_number=body.serial_number,
            values=body.model_dump(exclude={"serial_number"}),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    db.commit()
    return device


@router.post("/{device_id}/assign-user", response_model=DeviceRead)
def assign_user(
    device_id: UUID,
    body: AssignUserRequest,
    principal: Principal = Depends(require_permission("devices:write")),
    db: Session = Depends(get_db),
) -> Device:
    try:
        device = DeviceService(db).assign_user(
            tenant_id=UUID(principal.tenant_id) if principal.tenant_id else None,
            device_id=device_id,
            user_id=body.user_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    db.commit()
    return device


@router.post("/{device_id}/assign-group", status_code=status.HTTP_204_NO_CONTENT)
def assign_group(
    device_id: UUID,
    body: AssignGroupRequest,
    principal: Principal = Depends(require_permission("devices:write")),
    db: Session = Depends(get_db),
) -> None:
    try:
        DeviceService(db).add_to_group(
            tenant_id=UUID(principal.tenant_id) if principal.tenant_id else None,
            device_id=device_id,
            group_id=body.group_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    db.commit()
