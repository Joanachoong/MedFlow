from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.errors import ForbiddenError, InactiveAccountError
from app.core.permissions import CurrentUser, Role
from app.core.security import build_current_user, decode_supabase_jwt
from app.db.session import async_session_factory
from app.db.unit_of_work import UnitOfWork

# ── HTTP Bearer extraction ────────────────────────────────────────────────────

_bearer = HTTPBearer(auto_error=True)


# ── Session & UoW ─────────────────────────────────────────────────────────────


async def get_session() -> AsyncGenerator:
    """Yield a single AsyncSession for the request, auto-closed after response."""
    async with async_session_factory() as session:
        yield session


async def get_uow(
    session=Depends(get_session),
) -> UnitOfWork:
    return UnitOfWork(session)


# ── Auth ──────────────────────────────────────────────────────────────────────


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> CurrentUser:
    payload = decode_supabase_jwt(credentials.credentials)
    user = build_current_user(payload)
    if not user.is_active:
        raise InactiveAccountError()
    return user


# ── Role guards (dependency factories) ───────────────────────────────────────


def require_roles(*roles: Role):
    """
    Returns a FastAPI dependency that enforces the user has one of `roles`.

    Usage:
        @router.get("/admin-only")
        async def admin_only(user: CurrentUser = Depends(require_roles(Role.ADMIN))):
            ...
    """

    async def _guard(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not user.has_role(*roles):
            raise ForbiddenError(
                f"Requires one of: {', '.join(r.value for r in roles)}"
            )
        return user

    return _guard
