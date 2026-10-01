from __future__ import annotations

from uuid import UUID

from app.core.events import bus
from app.core.permissions import CurrentUser
from app.db.unit_of_work import UnitOfWork
from app.modules.clinical.events import (
    CareNoteCreated,
    ClinicalNoteCreated,
    NurseInstructionCreated,
    RecordAccessGranted,
    RecordAccessRevoked,
)
from app.modules.clinical.models import CareNote, ClinicalNote, NurseInstruction, RecordAccessGrant
from app.modules.clinical.policies import ClinicalPolicy
from app.modules.clinical.repository import ClinicalRepository
from app.modules.clinical.schemas import (
    CreateCareNoteRequest,
    CreateClinicalNoteRequest,
    CreateNurseInstructionRequest,
    GrantRecordAccessRequest,
    UpdateCareNoteRequest,
)


class ClinicalService:
    def __init__(self, uow: UnitOfWork, care_team_svc=None) -> None:
        self._uow = uow
        self._repo = ClinicalRepository(uow.session)
        self._policy = ClinicalPolicy()
        # Cross-module: CareTeamService injected to check assignments without importing repo
        self._care_team = care_team_svc

    # ── Clinical Notes ────────────────────────────────────────────────────────

    async def create_clinical_note(self, actor: CurrentUser, body: CreateClinicalNoteRequest) -> ClinicalNote:
        self._policy.can_create_clinical_note(actor)
        note = await self._repo.create_clinical_note(
            patient_id=body.patient_id,
            doctor_id=actor.id,
            diagnosis=body.diagnosis,
            observation=body.observation,
            plan=body.plan,
        )
        await bus.publish(ClinicalNoteCreated(
            actor_id=actor.id, patient_id=body.patient_id,
            session=self._uow.session, note_id=note.id,
        ))
        return note

    async def list_clinical_notes(self, actor: CurrentUser, patient_id: UUID) -> list[ClinicalNote]:
        # Simplified: doctors and nurses on the care team can list
        notes = await self._repo.list_clinical_notes_for_patient(patient_id)
        return notes

    # ── Nurse Instructions ────────────────────────────────────────────────────

    async def create_nurse_instruction(self, actor: CurrentUser, body: CreateNurseInstructionRequest) -> NurseInstruction:
        self._policy.can_create_nurse_instruction(actor)
        instr = await self._repo.create_nurse_instruction(
            patient_id=body.patient_id,
            doctor_id=actor.id,
            body=body.body,
            priority=body.priority,
        )
        await bus.publish(NurseInstructionCreated(
            actor_id=actor.id, patient_id=body.patient_id,
            session=self._uow.session, instruction_id=instr.id,
        ))
        return instr

    async def list_nurse_instructions(self, actor: CurrentUser, patient_id: UUID) -> list[NurseInstruction]:
        return await self._repo.list_nurse_instructions_for_patient(patient_id)

    # ── Care Notes ────────────────────────────────────────────────────────────

    async def create_care_note(self, actor: CurrentUser, body: CreateCareNoteRequest) -> CareNote:
        is_care_team = False
        if self._care_team:
            is_care_team = await self._care_team.is_nurse_on_care_team(actor.id, body.patient_id)
        self._policy.can_create_care_note(actor, is_care_team=is_care_team)
        note = await self._repo.create_care_note(
            patient_id=body.patient_id,
            nurse_id=actor.id,
            vitals=body.vitals,
            observation=body.observation,
        )
        await bus.publish(CareNoteCreated(
            actor_id=actor.id, patient_id=body.patient_id,
            session=self._uow.session, note_id=note.id,
        ))
        return note

    async def update_care_note(self, actor: CurrentUser, note_id: UUID, body: UpdateCareNoteRequest) -> CareNote:
        note = await self._repo.get_care_note(note_id)
        self._policy.can_update_care_note(actor, note)
        if body.vitals is not None:
            note.vitals = body.vitals
        if body.observation is not None:
            note.observation = body.observation
        self._uow.session.add(note)
        return note

    async def delete_care_note(self, actor: CurrentUser, note_id: UUID) -> None:
        note = await self._repo.get_care_note(note_id)
        self._policy.can_delete_care_note(actor, note)
        await self._repo.soft_delete_care_note(note)

    async def list_care_notes(self, actor: CurrentUser, patient_id: UUID) -> list[CareNote]:
        return await self._repo.list_care_notes_for_patient(patient_id)

    # ── Record Access Grants ──────────────────────────────────────────────────

    async def grant_access(self, actor: CurrentUser, body: GrantRecordAccessRequest) -> RecordAccessGrant:
        is_assigned = False
        if self._care_team:
            is_assigned = await self._care_team.is_doctor_assigned(actor.id, body.patient_id)
        self._policy.can_grant_record_access(actor, is_assigned=is_assigned)
        grant = await self._repo.create_grant(
            patient_id=body.patient_id, granted_by=actor.id, scope=body.scope
        )
        await bus.publish(RecordAccessGranted(
            actor_id=actor.id, patient_id=body.patient_id,
            session=self._uow.session, grant_id=grant.id, scope=body.scope,
        ))
        return grant

    async def revoke_access(self, actor: CurrentUser, patient_id: UUID) -> None:
        grant = await self._repo.get_active_grant(patient_id)
        if grant is None:
            from app.modules.clinical.exceptions import NoActiveGrantError
            raise NoActiveGrantError()
        self._policy.can_revoke_record_access(actor, grant)
        await self._repo.revoke_grant(grant, revoked_by=actor.id)
        await bus.publish(RecordAccessRevoked(
            actor_id=actor.id, patient_id=patient_id,
            session=self._uow.session, grant_id=grant.id,
        ))

    async def has_active_grant(self, patient_id: UUID) -> bool:
        grant = await self._repo.get_active_grant(patient_id)
        return grant is not None
