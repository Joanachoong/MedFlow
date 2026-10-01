from __future__ import annotations

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.modules.scheduling.models import Appointment


class SchedulingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, patient_id: UUID, doctor_id: UUID, created_by: UUID, **fields) -> Appointment:
        appt = Appointment(id=uuid.uuid4(), patient_id=patient_id, doctor_id=doctor_id, created_by=created_by, **fields)
        self._session.add(appt)
        await self._session.flush()
        await self._session.refresh(appt)
        return appt

    async def get_by_id(self, appt_id: UUID) -> Appointment:
        result = await self._session.get(Appointment, appt_id)
        if result is None:
            raise NotFoundError("Appointment", str(appt_id))
        return result

    async def list_for_doctor(self, doctor_id: UUID, limit: int = 20) -> list[Appointment]:
        stmt = select(Appointment).where(Appointment.doctor_id == doctor_id).order_by(Appointment.starts_at).limit(limit)
        return list((await self._session.execute(stmt)).scalars().all())

    async def list_for_patient(self, patient_id: UUID, limit: int = 20) -> list[Appointment]:
        stmt = select(Appointment).where(Appointment.patient_id == patient_id).order_by(Appointment.starts_at).limit(limit)
        return list((await self._session.execute(stmt)).scalars().all())

    async def update(self, appt_id: UUID, **fields) -> Appointment:
        appt = await self.get_by_id(appt_id)
        for k, v in fields.items():
            if v is not None:
                setattr(appt, k, v)
        self._session.add(appt)
        return appt
