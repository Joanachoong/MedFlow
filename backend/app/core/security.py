from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from jose import JWTError, jwt

from app.core.config import settings
from app.core.errors import UnauthorizedError
from app.core.permissions import CurrentUser, Role

logger = logging.getLogger(__name__)


def decode_supabase_jwt(token: str) -> dict[str, Any]:
    """
    Verify and decode a Supabase-issued JWT (HS256, signed with SUPABASE_JWT_SECRET).
    Raises UnauthorizedError if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        return payload
    except JWTError as exc:
        logger.warning("JWT decode failed: %s", exc)
        raise UnauthorizedError("Invalid or expired token")


def build_current_user(payload: dict[str, Any]) -> CurrentUser:
    """
    Build a CurrentUser from a verified JWT payload.
    Role is read from app_metadata.role (set server-side only by Supabase service_role).
    """
    raw_id = payload.get("sub")
    if not raw_id:
        raise UnauthorizedError("Token missing subject claim")

    app_metadata: dict = payload.get("app_metadata") or {}
    raw_role = app_metadata.get("role")

    try:
        role = Role(raw_role)
    except (ValueError, TypeError):
        raise UnauthorizedError(f"Unknown or missing role '{raw_role}' in token")

    try:
        user_id = UUID(raw_id)
    except ValueError:
        raise UnauthorizedError("Token subject is not a valid UUID")

    email: str = payload.get("email", "")
    return CurrentUser(id=user_id, role=role, email=email)
