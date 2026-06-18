"""initial DH MDM schema

Revision ID: 20260618_0001
Revises:
Create Date: 2026-06-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260618_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


command_status = postgresql.ENUM("queued", "sent", "acknowledged", "completed", "error", "timed_out", name="commandstatus", create_type=False)
ticket_status = postgresql.ENUM("open", "in_progress", "resolved", "closed", name="ticketstatus", create_type=False)
notification_channel = postgresql.ENUM("portal", "email", "teams", name="notificationchannel", create_type=False)


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    ]


def tenant_column(nullable: bool = True) -> sa.Column:
    return sa.Column("tenant_id", sa.UUID(), sa.ForeignKey("tenants.id"), nullable=nullable)


def upgrade() -> None:
    command_status.create(op.get_bind(), checkfirst=True)
    ticket_status.create(op.get_bind(), checkfirst=True)
    notification_channel.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "tenants",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(120), nullable=False, unique=True),
        sa.Column("entra_tenant_id", sa.String(128), nullable=True, unique=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *timestamps(),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), primary_key=True),
        tenant_column(),
        sa.Column("entra_object_id", sa.String(128), nullable=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(64), nullable=False, server_default="Read Only"),
        sa.Column("department", sa.String(120), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *timestamps(),
        sa.UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_entra_object_id", "users", ["entra_object_id"])
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])

    op.create_table(
        "devices",
        sa.Column("id", sa.UUID(), primary_key=True),
        tenant_column(),
        sa.Column("assigned_user_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("serial_number", sa.String(120), nullable=False),
        sa.Column("udid", sa.String(160), nullable=True),
        sa.Column("model", sa.String(120), nullable=True),
        sa.Column("platform", sa.String(32), nullable=False, server_default="macOS"),
        sa.Column("os_version", sa.String(64), nullable=True),
        sa.Column("chip", sa.String(120), nullable=True),
        sa.Column("ram_bytes", sa.Integer(), nullable=True),
        sa.Column("disk_bytes", sa.Integer(), nullable=True),
        sa.Column("battery_health", sa.String(64), nullable=True),
        sa.Column("supervised", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("enrolled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("push_token", sa.Text(), nullable=True),
        sa.Column("push_magic", sa.String(255), nullable=True),
        sa.Column("last_checkin_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("inventory", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        *timestamps(),
        sa.UniqueConstraint("tenant_id", "serial_number", name="uq_devices_tenant_serial"),
    )
    op.create_index("ix_devices_serial_number", "devices", ["serial_number"])
    op.create_index("ix_devices_tenant_id", "devices", ["tenant_id"])
    op.create_index("ix_devices_udid", "devices", ["udid"])

    op.create_table(
        "device_groups",
        sa.Column("id", sa.UUID(), primary_key=True),
        tenant_column(),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        *timestamps(),
        sa.UniqueConstraint("tenant_id", "name", name="uq_device_groups_tenant_name"),
    )
    op.create_index("ix_device_groups_tenant_id", "device_groups", ["tenant_id"])

    op.create_table(
        "device_group_members",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("device_id", sa.UUID(), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("group_id", sa.UUID(), sa.ForeignKey("device_groups.id"), nullable=False),
        *timestamps(),
        sa.UniqueConstraint("device_id", "group_id", name="uq_device_group_member"),
    )
    op.create_index("ix_device_group_members_device_id", "device_group_members", ["device_id"])
    op.create_index("ix_device_group_members_group_id", "device_group_members", ["group_id"])

    op.create_table(
        "commands",
        sa.Column("id", sa.UUID(), primary_key=True),
        tenant_column(),
        sa.Column("device_id", sa.UUID(), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("request_type", sa.String(120), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("status", command_status, nullable=False, server_default="queued"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
    )
    op.create_index("ix_commands_device_id", "commands", ["device_id"])
    op.create_index("ix_commands_tenant_id", "commands", ["tenant_id"])
    op.create_index("ix_commands_device_status", "commands", ["device_id", "status"])

    simple_tables = [
        ("profiles", [sa.Column("name", sa.String(200), nullable=False), sa.Column("identifier", sa.String(255), nullable=False), sa.Column("payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true())]),
        ("enrolment_profiles", [sa.Column("name", sa.String(200), nullable=False), sa.Column("mandatory_mdm", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("non_removable", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("await_device_configured", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("setup_assistant_skips", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json"))]),
        ("applications", [sa.Column("name", sa.String(255), nullable=False), sa.Column("bundle_id", sa.String(255), nullable=True), sa.Column("source", sa.String(32), nullable=False), sa.Column("version", sa.String(64), nullable=True), sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json"))]),
        ("scripts", [sa.Column("name", sa.String(255), nullable=False), sa.Column("shell", sa.String(64), nullable=False, server_default="/bin/zsh"), sa.Column("body", sa.Text(), nullable=False), sa.Column("parameters", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json"))]),
        ("policies", [sa.Column("name", sa.String(255), nullable=False), sa.Column("rules", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")), sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true())]),
        ("provisioning_workflows", [sa.Column("name", sa.String(255), nullable=False), sa.Column("steps", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")), sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true())]),
        ("abm_server_tokens", [sa.Column("name", sa.String(200), nullable=False), sa.Column("encrypted_token", sa.Text(), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True)]),
        ("vpp_tokens", [sa.Column("name", sa.String(200), nullable=False), sa.Column("encrypted_token", sa.Text(), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True)]),
    ]
    for table_name, columns in simple_tables:
        op.create_table(table_name, sa.Column("id", sa.UUID(), primary_key=True), tenant_column(), *columns, *timestamps())
        op.create_index(f"ix_{table_name}_tenant_id", table_name, ["tenant_id"])

    op.create_table(
        "script_runs",
        sa.Column("id", sa.UUID(), primary_key=True),
        tenant_column(),
        sa.Column("script_id", sa.UUID(), sa.ForeignKey("scripts.id"), nullable=False),
        sa.Column("device_id", sa.UUID(), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("status", sa.String(40), nullable=False, server_default="queued"),
        sa.Column("exit_code", sa.Integer(), nullable=True),
        sa.Column("output_ref", sa.Text(), nullable=True),
        *timestamps(),
    )
    op.create_index("ix_script_runs_tenant_id", "script_runs", ["tenant_id"])

    op.create_table(
        "compliance_results",
        sa.Column("id", sa.UUID(), primary_key=True),
        tenant_column(),
        sa.Column("device_id", sa.UUID(), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("policy_id", sa.UUID(), sa.ForeignKey("policies.id"), nullable=True),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        *timestamps(),
    )
    op.create_index("ix_compliance_results_device_id", "compliance_results", ["device_id"])
    op.create_index("ix_compliance_results_tenant_id", "compliance_results", ["tenant_id"])

    op.create_table(
        "filevault_keys",
        sa.Column("id", sa.UUID(), primary_key=True),
        tenant_column(),
        sa.Column("device_id", sa.UUID(), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("encrypted_key", sa.Text(), nullable=False),
        sa.Column("nonce", sa.Text(), nullable=False),
        sa.Column("kek_version", sa.String(64), nullable=False, server_default="env"),
        sa.Column("escrowed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        *timestamps(),
    )
    op.create_index("ix_filevault_keys_device_id", "filevault_keys", ["device_id"])
    op.create_index("ix_filevault_keys_tenant_id", "filevault_keys", ["tenant_id"])

    op.create_table(
        "assets",
        sa.Column("id", sa.UUID(), primary_key=True),
        tenant_column(),
        sa.Column("asset_tag", sa.String(120), nullable=False),
        sa.Column("device_id", sa.UUID(), sa.ForeignKey("devices.id"), nullable=True),
        sa.Column("status", sa.String(64), nullable=False, server_default="in_stock"),
        sa.Column("purchase_info", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        *timestamps(),
    )
    op.create_index("ix_assets_asset_tag", "assets", ["asset_tag"])
    op.create_index("ix_assets_tenant_id", "assets", ["tenant_id"])

    op.create_table(
        "tickets",
        sa.Column("id", sa.UUID(), primary_key=True),
        tenant_column(),
        sa.Column("number", sa.String(32), nullable=False),
        sa.Column("requester_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("assignee_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("device_id", sa.UUID(), sa.ForeignKey("devices.id"), nullable=True),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", ticket_status, nullable=False, server_default="open"),
        sa.Column("priority", sa.String(32), nullable=False, server_default="normal"),
        *timestamps(),
        sa.UniqueConstraint("tenant_id", "number", name="uq_tickets_tenant_number"),
    )
    op.create_index("ix_tickets_number", "tickets", ["number"])
    op.create_index("ix_tickets_tenant_id", "tickets", ["tenant_id"])

    op.create_table(
        "ticket_comments",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("ticket_id", sa.UUID(), sa.ForeignKey("tickets.id"), nullable=False),
        sa.Column("author_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("internal", sa.Boolean(), nullable=False, server_default=sa.false()),
        *timestamps(),
    )
    op.create_index("ix_ticket_comments_ticket_id", "ticket_comments", ["ticket_id"])

    op.create_table(
        "audit_log",
        sa.Column("id", sa.UUID(), primary_key=True),
        tenant_column(),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(160), nullable=False),
        sa.Column("target_type", sa.String(120), nullable=True),
        sa.Column("target_id", sa.String(120), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("ip_address", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("created_at IS NOT NULL", name="ck_audit_created_at_not_null"),
    )
    op.create_index("ix_audit_log_action", "audit_log", ["action"])
    op.create_index("ix_audit_log_tenant_id", "audit_log", ["tenant_id"])

    op.create_table(
        "provisioning_runs",
        sa.Column("id", sa.UUID(), primary_key=True),
        tenant_column(),
        sa.Column("workflow_id", sa.UUID(), sa.ForeignKey("provisioning_workflows.id"), nullable=False),
        sa.Column("status", sa.String(40), nullable=False, server_default="queued"),
        sa.Column("current_step", sa.String(120), nullable=True),
        sa.Column("context", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("error", sa.Text(), nullable=True),
        *timestamps(),
    )
    op.create_index("ix_provisioning_runs_tenant_id", "provisioning_runs", ["tenant_id"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.UUID(), primary_key=True),
        tenant_column(),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("channel", notification_channel, nullable=False),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
    )
    op.create_index("ix_notifications_tenant_id", "notifications", ["tenant_id"])

    op.create_table(
        "m365_actions",
        sa.Column("id", sa.UUID(), primary_key=True),
        tenant_column(),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(120), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("request", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("response", sa.JSON(), nullable=True),
        *timestamps(),
    )
    op.create_index("ix_m365_actions_tenant_id", "m365_actions", ["tenant_id"])

    op.create_table(
        "apns_token_history",
        sa.Column("id", sa.UUID(), primary_key=True),
        tenant_column(),
        sa.Column("device_id", sa.UUID(), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("push_token", sa.Text(), nullable=False),
        sa.Column("push_magic", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_apns_token_history_device_id", "apns_token_history", ["device_id"])
    op.create_index("ix_apns_token_history_tenant_id", "apns_token_history", ["tenant_id"])


def downgrade() -> None:
    for table_name in [
        "apns_token_history",
        "m365_actions",
        "notifications",
        "provisioning_runs",
        "audit_log",
        "ticket_comments",
        "tickets",
        "assets",
        "filevault_keys",
        "compliance_results",
        "script_runs",
        "vpp_tokens",
        "abm_server_tokens",
        "provisioning_workflows",
        "policies",
        "scripts",
        "applications",
        "enrolment_profiles",
        "profiles",
        "commands",
        "device_group_members",
        "device_groups",
        "devices",
        "users",
        "tenants",
    ]:
        op.drop_table(table_name)
    notification_channel.drop(op.get_bind(), checkfirst=True)
    ticket_status.drop(op.get_bind(), checkfirst=True)
    command_status.drop(op.get_bind(), checkfirst=True)
