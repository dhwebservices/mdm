from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class Repository(Generic[ModelT]):
    def __init__(self, db: Session, model: type[ModelT]) -> None:
        self.db = db
        self.model = model

    def get(self, item_id: UUID) -> ModelT | None:
        return self.db.get(self.model, item_id)

    def list(self, tenant_id: UUID | None, limit: int = 100, offset: int = 0) -> list[ModelT]:
        stmt: Select[tuple[ModelT]] = select(self.model).limit(limit).offset(offset)
        if hasattr(self.model, "tenant_id"):
            stmt = stmt.where(self.model.tenant_id == tenant_id)  # type: ignore[attr-defined]
        return list(self.db.scalars(stmt))

    def add(self, instance: ModelT) -> ModelT:
        self.db.add(instance)
        self.db.flush()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: ModelT) -> None:
        self.db.delete(instance)
        self.db.flush()
