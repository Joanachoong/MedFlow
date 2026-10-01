from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.modules.identity.models import Profile


class IdentityRepository:
    """All SQL for the identity module. Only called by IdentityService."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, profile_id: UUID) -> Profile:
        result = await self._session.get(Profile, profile_id)
        if result is None or result.is_deleted:
            raise NotFoundError("Profile", str(profile_id))
        return result

    async def get_by_email(self, email: str) -> Profile | None:
        stmt = select(Profile).where(Profile.email == email, Profile.deleted_at.is_(None))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, skip: int = 0, limit: int = 20) -> tuple[list[Profile], int]:
        from sqlalchemy import func

        count_stmt = select(func.count()).select_from(Profile).where(Profile.deleted_at.is_(None))
        total = (await self._session.execute(count_stmt)).scalar_one()

        stmt = (
            select(Profile)
            .where(Profile.deleted_at.is_(None))
            .order_by(Profile.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return list(rows), total

    async def set_role(self, profile_id: UUID, role: str) -> Profile:
        profile = await self.get_by_id(profile_id)
        profile.role = role
        self._session.add(profile)
        return profile

    async def set_active(self, profile_id: UUID, is_active: bool) -> Profile:
        profile = await self.get_by_id(profile_id)
        profile.is_active = is_active
        self._session.add(profile)
        return profile

    async def update(self, profile_id: UUID, **fields) -> Profile:
        profile = await self.get_by_id(profile_id)
        for key, value in fields.items():
            if value is not None:
                setattr(profile, key, value)
        self._session.add(profile)
        return profile
