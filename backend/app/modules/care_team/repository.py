from __future__ import annotations

import uuid
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.modules.care_team.models import (
    DoctorPatientAssignment,
    NursePatientAssignment,
    PatientTransfer,
    TransferItem,
)


class CareTeamRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Doctor assignments ────────────────────────────────────────────────────

    async def get_active_doctor_assignment(
        self, patient_id: UUID
    ) -> DoctorPatientAssignment | None:
        stmt = select(DoctorPatientAssignment).where(
            DoctorPatientAssignment.patient_id == patient_id,
            DoctorPatientAssignment.unassigned_at.is_(None),
        )
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def is_doctor_assigned(self, doctor_id: UUID, patient_id: UUID) -> bool:
        stmt = select(DoctorPatientAssignment).where(
            DoctorPatientAssignment.doctor_id == doctor_id,
            DoctorPatientAssignment.patient_id == patient_id,
            DoctorPatientAssignment.unassigned_at.is_(None),
        )
        return (await self._session.execute(stmt)).scalar_one_or_none() is not None

    async def create_doctor_assignment(
        self, doctor_id: UUID, patient_id: UUID, transfer_id: UUID | None = None
    ) -> DoctorPatientAssignment:
        now = datetime.now(timezone.utc)
        row = DoctorPatientAssignment(
            id=uuid.uuid4(),
            doctor_id=doctor_id,
            patient_id=patient_id,
            transfer_id=transfer_id,
            assigned_at=now,
        )
        self._session.add(row)
        return row

    async def close_doctor_assignment(self, patient_id: UUID) -> None:
        assignment = await self.get_active_doctor_assignment(patient_id)
        if assignment:
            assignment.unassigned_at = datetime.now(timezone.utc)
            self._session.add(assignment)

    # ── Nurse assignments ─────────────────────────────────────────────────────

    async def is_nurse_on_care_team(self, nurse_id: UUID, patient_id: UUID) -> bool:
        stmt = select(NursePatientAssignment).where(
            NursePatientAssignment.nurse_id == nurse_id,
            NursePatientAssignment.patient_id == patient_id,
            NursePatientAssignment.unassigned_at.is_(None),
        )
        return (await self._session.execute(stmt)).scalar_one_or_none() is not None

    async def create_nurse_assignment(
        self, nurse_id: UUID, patient_id: UUID, assigned_by: UUID
    ) -> NursePatientAssignment:
        now = datetime.now(timezone.utc)
        row = NursePatientAssignment(
            id=uuid.uuid4(),
            nurse_id=nurse_id,
            patient_id=patient_id,
            assigned_by=assigned_by,
            assigned_at=now,
        )
        self._session.add(row)
        return row

    async def list_patients_for_nurse(self, nurse_id: UUID) -> list[UUID]:
        stmt = select(NursePatientAssignment.patient_id).where(
            NursePatientAssignment.nurse_id == nurse_id,
            NursePatientAssignment.unassigned_at.is_(None),
        )
        return list((await self._session.execute(stmt)).scalars().all())

    # ── Transfers ─────────────────────────────────────────────────────────────

    async def create_transfer(
        self,
        patient_id: UUID,
        from_doctor_id: UUID,
        to_doctor_id: UUID,
        transferred_by: UUID,
        reason: str | None,
        item_ids: list[UUID],
        item_types: list[str],
    ) -> PatientTransfer:
        now = datetime.now(timezone.utc)
        transfer = PatientTransfer(
            id=uuid.uuid4(),
            patient_id=patient_id,
            from_doctor_id=from_doctor_id,
            to_doctor_id=to_doctor_id,
            reason=reason,
            status="completed",
            transferred_by=transferred_by,
            created_at=now,
        )
        self._session.add(transfer)
        await self._session.flush()  # get transfer.id

        for item_id, item_type in zip(item_ids, item_types):
            self._session.add(
                TransferItem(
                    id=uuid.uuid4(),
                    transfer_id=transfer.id,
                    item_type=item_type,
                    item_id=item_id,
                )
            )
        return transfer
