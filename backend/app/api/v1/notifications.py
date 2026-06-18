from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import Principal, current_principal
from app.db.session import get_db
from app.models.entities import Notification, NotificationChannel
from app.repositories.base import Repository
from app.schemas.common import NotificationCreate, NotificationRead
from app.services.notifications import NotificationService

router = APIRouter()


@router.get("", response_model=list[NotificationRead])
def list_notifications(principal: Principal = Depends(current_principal), db: Session = Depends(get_db)) -> list[Notification]:
    return Repository(db, Notification).list(UUID(principal.tenant_id) if principal.tenant_id else None)


@router.post("", response_model=NotificationRead)
def create_notification(body: NotificationCreate, principal: Principal = Depends(current_principal), db: Session = Depends(get_db)) -> Notification:
    try:
        channel = NotificationChannel(body.channel)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Unsupported notification channel") from exc
    notification = NotificationService(db).create(
        tenant_id=UUID(principal.tenant_id) if principal.tenant_id else None,
        channel=channel,
        subject=body.subject,
        body=body.body,
        user_id=body.user_id,
    )
    db.commit()
    return notification
