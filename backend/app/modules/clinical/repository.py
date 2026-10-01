from __future__ import annotations

import uuid
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.modules.clinical.models import (
    CareNote,
    ClinicalNote,
    NurseInstruction,
    RecordAccessGrant,
)


class ClinicalRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Clinical Notes ────────────────────────────────────────────────────────

    async def create_clinical_note(self, patient_id: UUID, doctor_id: UUID, **fields) -> ClinicalNote:
        note = ClinicalNote(id=uuid.uuid4(), patient_id=patient_id, doctor_id=doctor_id, **fields)
        self._session.add(note)
        await self._session.flush()
        await self._session.refresh(note)
        return note

    async def get_clinical_note(self, note_id: UUID) -> ClinicalNote:
        note = await self._session.get(ClinicalNote, note_id)
        if note is None or note.is_deleted:
            raise NotFoundError("ClinicalNote", str(note_id))
        return note

    async def list_clinical_notes_for_patient(self, patient_id: UUID) -> list[ClinicalNote]:
        stmt = select(ClinicalNote).where(
            ClinicalNote.patient_id == patient_id,
            ClinicalNote.deleted_at.is_(None),
        ).order_by(ClinicalNote.created_at.desc())
        return list((await self._session.execute(stmt)).scalars().all())

    # ── Nurse Instructions ────────────────────────────────────────────────────

    async def create_nurse_instruction(self, patient_id: UUID, doctor_id: UUID, body: str, priority: str) -> NurseInstruction:
        instr = NurseInstruction(
            id=uuid.uuid4(), patient_id=patient_id, doctor_id=doctor_id, body=body, priority=priority
        )
        self._session.add(instr)
        await self._session.flush()
        await self._session.refresh(instr)
        return instr

    async def get_nurse_instruction(self, instr_id: UUID) -> NurseInstruction:
        instr = await self._session.get(NurseInstruction, instr_id)
        if instr is None or instr.is_deleted:
            raise NotFoundError("NurseInstruction", str(instr_id))
        return instr

    async def list_nurse_instructions_for_patient(self, patient_id: UUID) -> list[NurseInstruction]:
        stmt = select(NurseInstruction).where(
            NurseInstruction.patient_id == patient_id,
            NurseInstruction.deleted_at.is_(None),
        ).order_by(NurseInstruction.priority, NurseInstruction.created_at.desc())
        return list((await self._session.execute(stmt)).scalars().all())

    # ── Care Notes ────────────────────────────────────────────────────────────

    async def create_care_note(self, patient_id: UUID, nurse_id: UUID, vitals: dict | None, observation: str | None) -> CareNote:
        note = CareNote(
            id=uuid.uuid4(), patient_id=patient_id, nurse_id=nurse_id,
            vitals=vitals, observation=observation,
        )
        self._session.add(note)
        await self._session.flush()
        await self._session.refresh(note)
        return note

    async def get_care_note(self, note_id: UUID) -> CareNote:
        note = await self._session.get(CareNote, note_id)
        if note is None or note.is_deleted:
            raise NotFoundError("CareNote", str(note_id))
        return note

    async def soft_delete_care_note(self, note: CareNote) -> None:
        note.deleted_at = datetime.now(timezone.utc)
        self._session.add(note)

    async def list_care_notes_for_patient(self, patient_id: UUID) -> list[CareNote]:
        stmt = select(CareNote).where(
            CareNote.patient_id == patient_id,
            CareNote.deleted_at.is_(None),
        ).order_by(CareNote.created_at.desc())
        return list((await self._session.execute(stmt)).scalars().all())

    # ── Record Access Grants ──────────────────────────────────────────────────

    async def create_grant(self, patient_id: UUID, granted_by: UUID, scope: str) -> RecordAccessGrant:
        now = datetime.now(timezone.utc)
        grant = RecordAccessGrant(
            id=uuid.uuid4(), patient_id=patient_id, granted_by=granted_by,
            scope=scope, granted_at=now,
        )
        self._session.add(grant)
        await self._session.flush()
        return grant

    async def get_active_grant(self, patient_id: UUID, scope: str = "medical_record") -> RecordAccessGrant | None:
        stmt = select(RecordAccessGrant).where(
            RecordAccessGrant.patient_id == patient_id,
            RecordAccessGrant.scope == scope,
            RecordAccessGrant.revoked_at.is_(None),
        )
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def revoke_grant(self, grant: RecordAccessGrant, revoked_by: UUID) -> None:
        grant.revoked_at = datetime.now(timezone.utc)
        grant.revoked_by = revoked_by
        self._session.add(grant)
