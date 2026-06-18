from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Command, CommandStatus
from app.repositories.base import Repository


class CommandRepository(Repository[Command]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Command)

    def next_queued_for_device(self, device_id: UUID) -> Command | None:
        return self.db.scalar(
            select(Command)
            .where(Command.device_id == device_id, Command.status == CommandStatus.queued)
            .order_by(Command.created_at)
            .limit(1)
            .with_for_update(skip_locked=True)
        )
