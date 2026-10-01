from __future__ import annotations

import uuid
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.modules.encounters.models import Encounter


class EncounterRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, **fields) -> Encounter:
        enc = Encounter(id=uuid.uuid4(), **fields)
        self._session.add(enc)
        await self._session.flush()
        await self._session.refresh(enc)
        return enc

    async def get_by_id(self, enc_id: UUID) -> Encounter:
        result = await self._session.get(Encounter, enc_id)
        if result is None:
            raise NotFoundError("Encounter", str(enc_id))
        return result

    async def list_active_admissions(self) -> list[Encounter]:
        stmt = select(Encounter).where(
            Encounter.encounter_type == "admission",
            Encounter.ended_at.is_(None),
        ).order_by(Encounter.started_at)
        return list((await self._session.execute(stmt)).scalars().all())

    async def discharge(self, enc_id: UUID, ended_at: datetime) -> Encounter:
        enc = await self.get_by_id(enc_id)
        enc.ended_at = ended_at
        self._session.add(enc)
        return enc
