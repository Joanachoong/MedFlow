from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, get_uow, require_roles
from app.core.permissions import CurrentUser, Role
from app.db.unit_of_work import UnitOfWork
from app.modules.care_team.schemas import (
    AssignNurseRequest,
    AssignmentOut,
    TransferOut,
    TransferPatientRequest,
)
from app.modules.care_team.service import CareTeamService

router = APIRouter(prefix="/care-team", tags=["care_team"])


def _svc(uow: UnitOfWork = Depends(get_uow)) -> CareTeamService:
    return CareTeamService(uow)


@router.post("/nurses/assign", response_model=AssignmentOut, status_code=201)
async def assign_nurse(
    body: AssignNurseRequest,
    user: CurrentUser = Depends(require_roles(Role.DOCTOR, Role.ADMIN)),
    svc: CareTeamService = Depends(_svc),
    uow: UnitOfWork = Depends(get_uow),
):
    assignment = await svc.assign_nurse(user, body)
    await uow.commit()
    return AssignmentOut(
        id=assignment.id,
        nurse_id=assignment.nurse_id,
        patient_id=assignment.patient_id,
        assigned_at=assignment.assigned_at,
        unassigned_at=assignment.unassigned_at,
    )


@router.post("/patients/{patient_id}/transfer", response_model=TransferOut, status_code=201)
async def transfer_patient(
    patient_id: UUID,
    body: TransferPatientRequest,
    user: CurrentUser = Depends(require_roles(Role.DOCTOR)),
    svc: CareTeamService = Depends(_svc),
    uow: UnitOfWork = Depends(get_uow),
):
    transfer = await svc.transfer_patient(user, patient_id, body)
    await uow.commit()
    return TransferOut.model_validate(transfer)
