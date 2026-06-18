import base64
import os
from uuid import UUID

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import FileVaultKey
from app.services.audit import AuditService


class FileVaultService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.audit = AuditService(db)

    def _aesgcm(self) -> AESGCM:
        kek = settings.filevault_kek.encode("utf-8")
        key = kek[:32].ljust(32, b"0")
        return AESGCM(key)

    def escrow(self, *, tenant_id: UUID | None, device_id: UUID, recovery_key: str, actor_id: UUID | None = None) -> FileVaultKey:
        nonce = os.urandom(12)
        encrypted = self._aesgcm().encrypt(nonce, recovery_key.encode("utf-8"), str(device_id).encode("utf-8"))
        record = FileVaultKey(
            tenant_id=tenant_id,
            device_id=device_id,
            encrypted_key=base64.b64encode(encrypted).decode("ascii"),
            nonce=base64.b64encode(nonce).decode("ascii"),
            kek_version="env",
        )
        self.db.add(record)
        self.db.flush()
        self.audit.record(
            tenant_id=tenant_id,
            user_id=actor_id,
            action="filevault_key.escrowed",
            target_type="devices",
            target_id=str(device_id),
        )
        return record

    def retrieve(self, *, tenant_id: UUID | None, key_id: UUID, actor_id: UUID | None) -> str:
        record = self.db.get(FileVaultKey, key_id)
        if record is None or record.tenant_id != tenant_id:
            raise LookupError("FileVault key not found")
        self.audit.record(
            tenant_id=tenant_id,
            user_id=actor_id,
            action="filevault_key.retrieved",
            target_type="filevault_keys",
            target_id=str(key_id),
        )
        nonce = base64.b64decode(record.nonce)
        encrypted = base64.b64decode(record.encrypted_key)
        return self._aesgcm().decrypt(nonce, encrypted, str(record.device_id).encode("utf-8")).decode("utf-8")
