from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, get_uow, require_roles
from app.core.permissions import CurrentUser, Role
from app.db.unit_of_work import UnitOfWork
from app.modules.encounters.schemas import CreateEncounterRequest, DischargeRequest, EncounterOut
from app.modules.encounters.service import EncounterService

router = APIRouter(prefix="/encounters", tags=["encounters"])


def _svc(uow: UnitOfWork = Depends(get_uow)) -> EncounterService:
    return EncounterService(uow)


@router.post("", response_model=EncounterOut, status_code=201)
async def create_encounter(
    body: CreateEncounterRequest,
    user: CurrentUser = Depends(require_roles(Role.DOCTOR, Role.ADMIN)),
    svc: EncounterService = Depends(_svc),
    uow: UnitOfWork = Depends(get_uow),
):
    enc = await svc.create_encounter(user, body)
    await uow.commit()
    return EncounterOut.model_validate(enc)


@router.patch("/{enc_id}/discharge", response_model=EncounterOut)
async def discharge_patient(
    enc_id: UUID,
    body: DischargeRequest,
    user: CurrentUser = Depends(require_roles(Role.DOCTOR, Role.ADMIN)),
    svc: EncounterService = Depends(_svc),
    uow: UnitOfWork = Depends(get_uow),
):
    enc = await svc.discharge(user, enc_id, body)
    await uow.commit()
    return EncounterOut.model_validate(enc)


@router.get("/admissions", response_model=list[EncounterOut])
async def list_admissions(
    user: CurrentUser = Depends(require_roles(Role.ADMIN, Role.DOCTOR, Role.NURSE)),
    svc: EncounterService = Depends(_svc),
):
    items = await svc.list_active_admissions(user)
    return [EncounterOut.model_validate(e) for e in items]
