import enum
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class CommandStatus(str, enum.Enum):
    queued = "queued"
    sent = "sent"
    acknowledged = "acknowledged"
    completed = "completed"
    error = "error"
    timed_out = "timed_out"


class TicketStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class NotificationChannel(str, enum.Enum):
    portal = "portal"
    email = "email"
    teams = "teams"


class TenantMixin:
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True, nullable=True)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    entra_tenant_id: Mapped[str | None] = mapped_column(String(128), nullable=True, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class User(Base, TenantMixin, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entra_object_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(64), nullable=False, default="Read Only")
    department: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Device(Base, TenantMixin, TimestampMixin):
    __tablename__ = "devices"
    __table_args__ = (UniqueConstraint("tenant_id", "serial_number", name="uq_devices_tenant_serial"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assigned_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    serial_number: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    udid: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    platform: Mapped[str] = mapped_column(String(32), default="macOS", nullable=False)
    os_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    chip: Mapped[str | None] = mapped_column(String(120), nullable=True)
    ram_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    disk_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    battery_health: Mapped[str | None] = mapped_column(String(64), nullable=True)
    supervised: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    enrolled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    push_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    push_magic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_checkin_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    inventory: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    assigned_user: Mapped[User | None] = relationship()


class DeviceGroup(Base, TenantMixin, TimestampMixin):
    __tablename__ = "device_groups"
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_device_groups_tenant_name"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class DeviceGroupMember(Base, TimestampMixin):
    __tablename__ = "device_group_members"
    __table_args__ = (UniqueConstraint("device_id", "group_id", name="uq_device_group_member"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False, index=True)
    group_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("device_groups.id"), nullable=False, index=True)


class Command(Base, TenantMixin, TimestampMixin):
    __tablename__ = "commands"
    __table_args__ = (Index("ix_commands_device_status", "device_id", "status"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False, index=True)
    request_type: Mapped[str] = mapped_column(String(120), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[CommandStatus] = mapped_column(Enum(CommandStatus), default=CommandStatus.queued, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Profile(Base, TenantMixin, TimestampMixin):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    identifier: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class EnrollmentProfile(Base, TenantMixin, TimestampMixin):
    __tablename__ = "enrolment_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    mandatory_mdm: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    non_removable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    await_device_configured: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    setup_assistant_skips: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)


class Application(Base, TenantMixin, TimestampMixin):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    bundle_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)


class Script(Base, TenantMixin, TimestampMixin):
    __tablename__ = "scripts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    shell: Mapped[str] = mapped_column(String(64), default="/bin/zsh", nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class ScriptRun(Base, TenantMixin, TimestampMixin):
    __tablename__ = "script_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    script_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("scripts.id"), nullable=False)
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="queued")
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_ref: Mapped[str | None] = mapped_column(Text, nullable=True)


class Policy(Base, TenantMixin, TimestampMixin):
    __tablename__ = "policies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    rules: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ComplianceResult(Base, TenantMixin, TimestampMixin):
    __tablename__ = "compliance_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False, index=True)
    policy_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("policies.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)


class FileVaultKey(Base, TenantMixin, TimestampMixin):
    __tablename__ = "filevault_keys"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False, index=True)
    encrypted_key: Mapped[str] = mapped_column(Text, nullable=False)
    nonce: Mapped[str] = mapped_column(Text, nullable=False)
    kek_version: Mapped[str] = mapped_column(String(64), nullable=False, default="env")
    escrowed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)


class Asset(Base, TenantMixin, TimestampMixin):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_tag: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    device_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="in_stock")
    purchase_info: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class Ticket(Base, TenantMixin, TimestampMixin):
    __tablename__ = "tickets"
    __table_args__ = (UniqueConstraint("tenant_id", "number", name="uq_tickets_tenant_number"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    number: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    requester_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    device_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus), default=TicketStatus.open, nullable=False)
    priority: Mapped[str] = mapped_column(String(32), default="normal", nullable=False)


class TicketComment(Base, TimestampMixin):
    __tablename__ = "ticket_comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False, index=True)
    author_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    internal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True, nullable=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    target_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)


class ProvisioningWorkflow(Base, TenantMixin, TimestampMixin):
    __tablename__ = "provisioning_workflows"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    steps: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ProvisioningRun(Base, TenantMixin, TimestampMixin):
    __tablename__ = "provisioning_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("provisioning_workflows.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="queued")
    current_step: Mapped[str | None] = mapped_column(String(120), nullable=True)
    context: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)


class Notification(Base, TenantMixin, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    channel: Mapped[NotificationChannel] = mapped_column(Enum(NotificationChannel), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class M365Action(Base, TenantMixin, TimestampMixin):
    __tablename__ = "m365_actions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    request: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    response: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class ABMServerToken(Base, TenantMixin, TimestampMixin):
    __tablename__ = "abm_server_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    encrypted_token: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class APNsTokenHistory(Base, TenantMixin):
    __tablename__ = "apns_token_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False, index=True)
    push_token: Mapped[str] = mapped_column(Text, nullable=False)
    push_magic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)


class VPPToken(Base, TenantMixin, TimestampMixin):
    __tablename__ = "vpp_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    encrypted_token: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


AuditLog.__table__.append_constraint(CheckConstraint("created_at IS NOT NULL", name="ck_audit_created_at_not_null"))
