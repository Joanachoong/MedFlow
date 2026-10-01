from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_current_user, get_uow, require_roles
from app.core.permissions import CurrentUser, Role
from app.db.unit_of_work import UnitOfWork
from app.modules.patients.schemas import CreatePatientRequest, PatientOut, UpdatePatientRequest
from app.modules.patients.service import PatientService
from app.shared.schemas import PaginatedResponse, PaginationParams

router = APIRouter(prefix="/patients", tags=["patients"])


def _svc(uow: UnitOfWork = Depends(get_uow)) -> PatientService:
    return PatientService(uow)


@router.post("", response_model=PatientOut, status_code=201)
async def create_patient(
    body: CreatePatientRequest,
    user: CurrentUser = Depends(require_roles(Role.DOCTOR)),
    svc: PatientService = Depends(_svc),
    uow: UnitOfWork = Depends(get_uow),
):
    patient = await svc.create_patient(user, body)
    await uow.commit()
    return PatientOut.model_validate(patient)


@router.get("/me", response_model=PatientOut)
async def get_my_record(
    user: CurrentUser = Depends(require_roles(Role.PATIENT)),
    svc: PatientService = Depends(_svc),
):
    """Patient portal: fetch own medical record."""
    patient = await svc.get_my_patient_record(user)
    return PatientOut.model_validate(patient)


@router.get("", response_model=PaginatedResponse[PatientOut])
async def list_my_patients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: CurrentUser = Depends(require_roles(Role.DOCTOR)),
    svc: PatientService = Depends(_svc),
):
    params = PaginationParams(page=page, page_size=page_size)
    items, total = await svc.list_my_patients(user, skip=params.offset, limit=params.page_size)
    return PaginatedResponse.build(
        items=[PatientOut.model_validate(p) for p in items],
        total=total,
        params=params,
    )


@router.get("/{patient_id}", response_model=PatientOut)
async def get_patient(
    patient_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    svc: PatientService = Depends(_svc),
):
    # Assignment check happens inside the service for MVP (simplified)
    patient = await svc.get_patient(user, patient_id)
    return PatientOut.model_validate(patient)


@router.patch("/{patient_id}", response_model=PatientOut)
async def update_patient(
    patient_id: UUID,
    body: UpdatePatientRequest,
    user: CurrentUser = Depends(require_roles(Role.DOCTOR)),
    svc: PatientService = Depends(_svc),
    uow: UnitOfWork = Depends(get_uow),
):
    patient = await svc.update_patient(user, patient_id, body)
    await uow.commit()
    return PatientOut.model_validate(patient)
