from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DeviceCreate(BaseModel):
    serial_number: str = Field(min_length=1, max_length=120)
    udid: str | None = None
    model: str | None = None
    platform: str = "macOS"


class DeviceRead(ORMModel):
    id: UUID
    tenant_id: UUID | None
    assigned_user_id: UUID | None
    serial_number: str
    udid: str | None
    model: str | None
    platform: str
    os_version: str | None
    supervised: bool
    enrolled: bool
    last_checkin_at: datetime | None
    inventory: dict[str, Any]


class AssignUserRequest(BaseModel):
    user_id: UUID


class AssignGroupRequest(BaseModel):
    group_id: UUID


class DashboardSummary(BaseModel):
    devices: int
    enrolled_devices: int
    users: int
    open_tickets: int
    failed_commands: int
    unread_notifications: int


class NotificationCreate(BaseModel):
    channel: str
    subject: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1)
    user_id: UUID | None = None


class NotificationRead(ORMModel):
    id: UUID
    channel: str
    subject: str
    body: str
    delivered_at: datetime | None
    read_at: datetime | None
    created_at: datetime


class AuditRead(ORMModel):
    id: UUID
    action: str
    target_type: str | None
    target_id: str | None
    details: dict[str, Any]
    created_at: datetime


class MDMMessage(BaseModel):
    model_config = ConfigDict(extra="allow")

    MessageType: str | None = None
    UDID: str | None = None
    Status: str | None = None
    CommandUUID: str | None = None
