from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import Principal, require_permission
from app.db.session import get_db
from app.models.entities import AuditLog
from app.schemas.common import AuditRead

router = APIRouter()


@router.get("", response_model=list[AuditRead])
def list_audit_log(
    principal: Principal = Depends(require_permission("audit:read")),
    db: Session = Depends(get_db),
) -> list[AuditLog]:
    tenant_id = UUID(principal.tenant_id) if principal.tenant_id else None
    return list(db.scalars(select(AuditLog).where(AuditLog.tenant_id == tenant_id).order_by(AuditLog.created_at.desc()).limit(200)))
