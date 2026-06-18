from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Any

import httpx
import jwt
from fastapi import Depends, HTTPException, Request, status
from jwt import PyJWKClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.entities import User
from app.services.audit import AuditService


class Role(str, Enum):
    admin = "Admin"
    it_manager = "IT Manager"
    helpdesk = "Helpdesk"
    read_only = "Read Only"


ROLE_PERMISSIONS: dict[Role, set[str]] = {
    Role.admin: {"*"},
    Role.it_manager: {"devices:write", "devices:read", "users:read", "policies:write", "audit:read"},
    Role.helpdesk: {"devices:read", "tickets:write", "users:read"},
    Role.read_only: {"devices:read", "users:read", "audit:read"},
}


@dataclass(frozen=True)
class Principal:
    subject: str
    email: str
    name: str
    role: Role
    tenant_id: str | None
    claims: dict[str, Any]


@lru_cache
def jwk_client() -> PyJWKClient:
    return PyJWKClient(str(settings.jwt_jwks_url))


def decode_access_token(token: str) -> dict[str, Any]:
    key = jwk_client().get_signing_key_from_jwt(token).key
    return jwt.decode(
        token,
        key=key,
        algorithms=["RS256"],
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer,
        options={"verify_at_hash": False},
    )


async def current_principal(request: Request, db: Session = Depends(get_db)) -> Principal:
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    try:
        claims = decode_access_token(authorization.removeprefix("Bearer ").strip())
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    email = claims.get("preferred_username") or claims.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has no email claim")

    user = db.query(User).filter(User.email == email).one_or_none()
    if user is None:
        user = User(
            tenant_id=None,
            entra_object_id=claims.get("oid"),
            email=email,
            display_name=claims.get("name") or email,
            role=Role.read_only.value,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        AuditService(db).record(user_id=user.id, tenant_id=None, action="login.first_seen", target_type="users", target_id=str(user.id))

    return Principal(
        subject=claims.get("sub", ""),
        email=email,
        name=user.display_name,
        role=Role(user.role),
        tenant_id=str(user.tenant_id) if user.tenant_id else None,
        claims=claims,
    )


def require_permission(permission: str):
    def dependency(principal: Principal = Depends(current_principal)) -> Principal:
        allowed = ROLE_PERMISSIONS[principal.role]
        if "*" not in allowed and permission not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        return principal

    return dependency
