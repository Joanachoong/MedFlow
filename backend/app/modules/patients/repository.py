from __future__ import annotations

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.modules.patients.models import Patient


class PatientRepository:
    """All SQL for the patients module. Only called by PatientService."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, patient_id: UUID) -> Patient:
        result = await self._session.get(Patient, patient_id)
        if result is None or result.is_deleted:
            raise NotFoundError("Patient", str(patient_id))
        return result

    async def get_by_user_id(self, user_id: UUID) -> Patient | None:
        stmt = select(Patient).where(
            Patient.user_id == user_id,
            Patient.deleted_at.is_(None),
        )
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def list_by_doctor(
        self, doctor_id: UUID, skip: int = 0, limit: int = 20
    ) -> tuple[list[Patient], int]:
        from sqlalchemy import func

        # Patients registered by this doctor OR currently assigned to them
        # For MVP: just registered_by. Assignments handled via care_team.
        stmt = (
            select(Patient)
            .where(Patient.created_by == doctor_id, Patient.deleted_at.is_(None))
            .order_by(Patient.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        count_stmt = select(func.count()).select_from(
            select(Patient)
            .where(Patient.created_by == doctor_id, Patient.deleted_at.is_(None))
            .subquery()
        )
        total = (await self._session.execute(count_stmt)).scalar_one()
        rows = (await self._session.execute(stmt)).scalars().all()
        return list(rows), total

    async def create(
        self,
        *,
        created_by: UUID,
        public_id: str,
        **fields,
    ) -> Patient:
        patient = Patient(
            id=uuid.uuid4(),
            public_id=public_id,
            created_by=created_by,
            **fields,
        )
        self._session.add(patient)
        await self._session.flush()
        await self._session.refresh(patient)
        return patient

    async def update(self, patient_id: UUID, **fields) -> Patient:
        patient = await self.get_by_id(patient_id)
        for key, value in fields.items():
            if value is not None:
                setattr(patient, key, value)
        self._session.add(patient)
        return patient

    async def next_sequence(self) -> int:
        """Count active patients to generate P-NNNN public IDs."""
        from sqlalchemy import func
        result = await self._session.execute(
            select(func.count()).select_from(Patient)
        )
        return (result.scalar_one() or 0) + 1
