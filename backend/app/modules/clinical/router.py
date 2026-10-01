from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, get_uow, require_roles
from app.core.permissions import CurrentUser, Role
from app.db.unit_of_work import UnitOfWork
from app.modules.care_team.service import CareTeamService
from app.modules.clinical.schemas import (
    CareNoteOut,
    ClinicalNoteOut,
    CreateCareNoteRequest,
    CreateClinicalNoteRequest,
    CreateNurseInstructionRequest,
    GrantRecordAccessRequest,
    NurseInstructionOut,
    RecordAccessGrantOut,
    UpdateCareNoteRequest,
)
from app.modules.clinical.service import ClinicalService

router = APIRouter(prefix="/clinical", tags=["clinical"])


def _svc(uow: UnitOfWork = Depends(get_uow)) -> ClinicalService:
    care_team_svc = CareTeamService(uow)
    return ClinicalService(uow, care_team_svc=care_team_svc)


# ── Clinical Notes ─────────────────────────────────────────────────────────────

@router.post("/notes", response_model=ClinicalNoteOut, status_code=201)
async def create_clinical_note(
    body: CreateClinicalNoteRequest,
    user: CurrentUser = Depends(require_roles(Role.DOCTOR)),
    svc: ClinicalService = Depends(_svc),
    uow: UnitOfWork = Depends(get_uow),
):
    note = await svc.create_clinical_note(user, body)
    await uow.commit()
    return ClinicalNoteOut.model_validate(note)


@router.get("/notes/patient/{patient_id}", response_model=list[ClinicalNoteOut])
async def list_clinical_notes(
    patient_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    svc: ClinicalService = Depends(_svc),
):
    notes = await svc.list_clinical_notes(user, patient_id)
    return [ClinicalNoteOut.model_validate(n) for n in notes]


# ── Nurse Instructions ─────────────────────────────────────────────────────────

@router.post("/nurse-instructions", response_model=NurseInstructionOut, status_code=201)
async def create_nurse_instruction(
    body: CreateNurseInstructionRequest,
    user: CurrentUser = Depends(require_roles(Role.DOCTOR)),
    svc: ClinicalService = Depends(_svc),
    uow: UnitOfWork = Depends(get_uow),
):
    instr = await svc.create_nurse_instruction(user, body)
    await uow.commit()
    return NurseInstructionOut.model_validate(instr)


@router.get("/nurse-instructions/patient/{patient_id}", response_model=list[NurseInstructionOut])
async def list_nurse_instructions(
    patient_id: UUID,
    user: CurrentUser = Depends(require_roles(Role.DOCTOR, Role.NURSE)),
    svc: ClinicalService = Depends(_svc),
):
    instrs = await svc.list_nurse_instructions(user, patient_id)
    return [NurseInstructionOut.model_validate(i) for i in instrs]


# ── Care Notes ─────────────────────────────────────────────────────────────────

@router.post("/care-notes", response_model=CareNoteOut, status_code=201)
async def create_care_note(
    body: CreateCareNoteRequest,
    user: CurrentUser = Depends(require_roles(Role.NURSE)),
    svc: ClinicalService = Depends(_svc),
    uow: UnitOfWork = Depends(get_uow),
):
    note = await svc.create_care_note(user, body)
    await uow.commit()
    return CareNoteOut.model_validate(note)


@router.patch("/care-notes/{note_id}", response_model=CareNoteOut)
async def update_care_note(
    note_id: UUID,
    body: UpdateCareNoteRequest,
    user: CurrentUser = Depends(require_roles(Role.NURSE)),
    svc: ClinicalService = Depends(_svc),
    uow: UnitOfWork = Depends(get_uow),
):
    note = await svc.update_care_note(user, note_id, body)
    await uow.commit()
    return CareNoteOut.model_validate(note)


@router.delete("/care-notes/{note_id}", status_code=204)
async def delete_care_note(
    note_id: UUID,
    user: CurrentUser = Depends(require_roles(Role.NURSE)),
    svc: ClinicalService = Depends(_svc),
    uow: UnitOfWork = Depends(get_uow),
):
    await svc.delete_care_note(user, note_id)
    await uow.commit()


@router.get("/care-notes/patient/{patient_id}", response_model=list[CareNoteOut])
async def list_care_notes(
    patient_id: UUID,
    user: CurrentUser = Depends(require_roles(Role.NURSE, Role.DOCTOR)),
    svc: ClinicalService = Depends(_svc),
):
    notes = await svc.list_care_notes(user, patient_id)
    return [CareNoteOut.model_validate(n) for n in notes]


# ── Record Access Grants ───────────────────────────────────────────────────────

@router.post("/access-grants", response_model=RecordAccessGrantOut, status_code=201)
async def grant_access(
    body: GrantRecordAccessRequest,
    user: CurrentUser = Depends(require_roles(Role.DOCTOR)),
    svc: ClinicalService = Depends(_svc),
    uow: UnitOfWork = Depends(get_uow),
):
    grant = await svc.grant_access(user, body)
    await uow.commit()
    return RecordAccessGrantOut.model_validate(grant)


@router.delete("/access-grants/patient/{patient_id}", status_code=204)
async def revoke_access(
    patient_id: UUID,
    user: CurrentUser = Depends(require_roles(Role.DOCTOR)),
    svc: ClinicalService = Depends(_svc),
    uow: UnitOfWork = Depends(get_uow),
):
    await svc.revoke_access(user, patient_id)
    await uow.commit()
