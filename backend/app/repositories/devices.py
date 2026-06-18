from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Device, DeviceGroup, DeviceGroupMember
from app.repositories.base import Repository


class DeviceRepository(Repository[Device]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Device)

    def by_serial(self, tenant_id: UUID | None, serial_number: str) -> Device | None:
        return self.db.scalar(select(Device).where(Device.tenant_id == tenant_id, Device.serial_number == serial_number))

    def by_udid(self, udid: str) -> Device | None:
        return self.db.scalar(select(Device).where(Device.udid == udid))


class DeviceGroupRepository(Repository[DeviceGroup]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, DeviceGroup)

    def add_member(self, device_id: UUID, group_id: UUID) -> DeviceGroupMember:
        member = DeviceGroupMember(device_id=device_id, group_id=group_id)
        self.db.add(member)
        self.db.flush()
        self.db.refresh(member)
        return member
