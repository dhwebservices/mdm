from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.entities import Device
from app.repositories.devices import DeviceGroupRepository, DeviceRepository
from app.services.audit import AuditService


class DeviceService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.devices = DeviceRepository(db)
        self.groups = DeviceGroupRepository(db)
        self.audit = AuditService(db)

    def create(self, *, tenant_id: UUID | None, serial_number: str, values: dict[str, Any], actor_id: UUID | None = None) -> Device:
        existing = self.devices.by_serial(tenant_id, serial_number)
        if existing:
            raise ValueError("Device serial number already exists")
        device = self.devices.add(Device(tenant_id=tenant_id, serial_number=serial_number, **values))
        self.audit.record(action="device.created", tenant_id=tenant_id, user_id=actor_id, target_type="devices", target_id=str(device.id))
        return device

    def assign_user(self, *, tenant_id: UUID | None, device_id: UUID, user_id: UUID, actor_id: UUID | None = None) -> Device:
        device = self.devices.get(device_id)
        if device is None or device.tenant_id != tenant_id:
            raise LookupError("Device not found")
        device.assigned_user_id = user_id
        self.audit.record(
            action="device.assigned_user",
            tenant_id=tenant_id,
            user_id=actor_id,
            target_type="devices",
            target_id=str(device.id),
            details={"assigned_user_id": str(user_id)},
        )
        self.db.flush()
        return device

    def add_to_group(self, *, tenant_id: UUID | None, device_id: UUID, group_id: UUID, actor_id: UUID | None = None) -> None:
        device = self.devices.get(device_id)
        if device is None or device.tenant_id != tenant_id:
            raise LookupError("Device not found")
        self.groups.add_member(device_id, group_id)
        self.audit.record(
            action="device.assigned_group",
            tenant_id=tenant_id,
            user_id=actor_id,
            target_type="devices",
            target_id=str(device_id),
            details={"group_id": str(group_id)},
        )
