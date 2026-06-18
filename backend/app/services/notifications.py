from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.entities import Notification, NotificationChannel
from app.services.audit import AuditService


class NotificationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.audit = AuditService(db)

    def create(
        self,
        *,
        tenant_id: UUID | None,
        channel: NotificationChannel,
        subject: str,
        body: str,
        user_id: UUID | None = None,
    ) -> Notification:
        delivered_at = datetime.now(timezone.utc) if channel == NotificationChannel.portal else None
        notification = Notification(
            tenant_id=tenant_id,
            user_id=user_id,
            channel=channel,
            subject=subject,
            body=body,
            delivered_at=delivered_at,
        )
        self.db.add(notification)
        self.db.flush()
        self.audit.record(
            tenant_id=tenant_id,
            user_id=user_id,
            action="notification.created",
            target_type="notifications",
            target_id=str(notification.id),
            details={"channel": channel.value},
        )
        return notification

    def send_email(self, notification: Notification) -> None:
        notification.delivered_at = datetime.now(timezone.utc)

    def send_teams_stub(self, notification: Notification) -> None:
        notification.delivered_at = datetime.now(timezone.utc)
