from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.entities import APNsTokenHistory, CommandStatus, Device
from app.repositories.commands import CommandRepository
from app.repositories.devices import DeviceRepository


class MDMService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.devices = DeviceRepository(db)
        self.commands = CommandRepository(db)

    def token_update(self, payload: dict[str, Any]) -> Device:
        udid = payload["UDID"]
        device = self.devices.by_udid(udid)
        if device is None:
            device = Device(serial_number=payload.get("SerialNumber") or udid, udid=udid, enrolled=True)
            self.db.add(device)
        device.push_token = payload.get("Token")
        device.push_magic = payload.get("PushMagic")
        device.last_checkin_at = datetime.now(timezone.utc)
        device.enrolled = True
        self.db.flush()
        self.db.add(
            APNsTokenHistory(
                tenant_id=device.tenant_id,
                device_id=device.id,
                push_token=device.push_token or "",
                push_magic=device.push_magic,
            )
        )
        return device

    def checkout(self, udid: str) -> None:
        device = self.devices.by_udid(udid)
        if device:
            device.enrolled = False
            device.last_checkin_at = datetime.now(timezone.utc)

    def next_command_payload(self, udid: str) -> dict[str, Any]:
        device = self.devices.by_udid(udid)
        if device is None:
            return {"Status": "Idle"}
        command = self.commands.next_queued_for_device(device.id)
        if command is None:
            return {"Status": "Idle"}
        command.status = CommandStatus.sent
        command.attempts += 1
        command.sent_at = datetime.now(timezone.utc)
        return {"CommandUUID": str(command.id), "Command": {"RequestType": command.request_type, **command.payload}}

    def record_response(self, payload: dict[str, Any]) -> None:
        command_uuid = payload.get("CommandUUID")
        if not command_uuid:
            return
        command = self.commands.get(command_uuid)
        if command is None:
            return
        status = payload.get("Status")
        command.result = payload
        command.acknowledged_at = datetime.now(timezone.utc)
        if status == "Acknowledged":
            command.status = CommandStatus.acknowledged
        elif status == "Error":
            command.status = CommandStatus.error
        elif status == "NotNow":
            command.status = CommandStatus.queued
