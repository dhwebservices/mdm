from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import Principal, current_principal
from app.db.session import get_db
from app.models.entities import Command, CommandStatus, Device, Notification, Ticket, TicketStatus, User
from app.schemas.common import DashboardSummary

router = APIRouter()


@router.get("", response_model=DashboardSummary)
def summary(principal: Principal = Depends(current_principal), db: Session = Depends(get_db)) -> DashboardSummary:
    tenant_id = principal.tenant_id

    def count(stmt):
        return db.scalar(stmt) or 0

    return DashboardSummary(
        devices=count(select(func.count()).select_from(Device).where(Device.tenant_id == tenant_id)),
        enrolled_devices=count(select(func.count()).select_from(Device).where(Device.tenant_id == tenant_id, Device.enrolled.is_(True))),
        users=count(select(func.count()).select_from(User).where(User.tenant_id == tenant_id)),
        open_tickets=count(select(func.count()).select_from(Ticket).where(Ticket.tenant_id == tenant_id, Ticket.status != TicketStatus.closed)),
        failed_commands=count(select(func.count()).select_from(Command).where(Command.tenant_id == tenant_id, Command.status == CommandStatus.error)),
        unread_notifications=count(select(func.count()).select_from(Notification).where(Notification.tenant_id == tenant_id, Notification.read_at.is_(None))),
    )
