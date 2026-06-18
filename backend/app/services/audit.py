from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.entities import AuditLog


class AuditService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def record(
        self,
        *,
        action: str,
        tenant_id: UUID | None,
        user_id: UUID | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details or {},
            ip_address=ip_address,
        )
        self.db.add(entry)
        self.db.flush()
        return entry
