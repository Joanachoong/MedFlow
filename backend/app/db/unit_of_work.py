from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork:
    """
    Wraps an AsyncSession and exposes commit / rollback.

    The same UoW (and therefore the same session) is passed through:
      service → repository  (writes)
      service → event → audit subscriber  (audit write in same transaction)

    This guarantees that a business change and its audit log are
    always committed or rolled back together.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def flush(self) -> None:
        """Flush pending writes to DB (assigns server-side PKs) without committing."""
        await self.session.flush()

    async def refresh(self, instance: Any) -> None:
        """Reload a model instance from the DB after a flush/commit."""
        await self.session.refresh(instance)
