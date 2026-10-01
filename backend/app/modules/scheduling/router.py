from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, get_uow, require_roles
from app.core.permissions import CurrentUser, Role
from app.db.unit_of_work import UnitOfWork
from app.modules.scheduling.schemas import AppointmentOut, CreateAppointmentRequest, UpdateAppointmentRequest
from app.modules.scheduling.service import SchedulingService

router = APIRouter(prefix="/scheduling", tags=["scheduling"])


def _svc(uow: UnitOfWork = Depends(get_uow)) -> SchedulingService:
    return SchedulingService(uow)


@router.post("/appointments", response_model=AppointmentOut, status_code=201)
async def create_appointment(
    body: CreateAppointmentRequest,
    user: CurrentUser = Depends(require_roles(Role.DOCTOR)),
    svc: SchedulingService = Depends(_svc),
    uow: UnitOfWork = Depends(get_uow),
):
    appt = await svc.create_appointment(user, body)
    await uow.commit()
    return AppointmentOut.model_validate(appt)


@router.get("/appointments", response_model=list[AppointmentOut])
async def list_appointments(
    user: CurrentUser = Depends(get_current_user),
    svc: SchedulingService = Depends(_svc),
):
    if user.is_doctor():
        items = await svc.list_for_doctor(user)
    else:
        items = []
    return [AppointmentOut.model_validate(a) for a in items]


@router.patch("/appointments/{appt_id}", response_model=AppointmentOut)
async def update_appointment(
    appt_id: UUID,
    body: UpdateAppointmentRequest,
    user: CurrentUser = Depends(require_roles(Role.DOCTOR, Role.ADMIN)),
    svc: SchedulingService = Depends(_svc),
    uow: UnitOfWork = Depends(get_uow),
):
    appt = await svc.update_appointment(user, appt_id, body)
    await uow.commit()
    return AppointmentOut.model_validate(appt)
