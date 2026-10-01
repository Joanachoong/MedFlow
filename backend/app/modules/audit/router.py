from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_uow, require_roles
from app.core.permissions import CurrentUser, Role
from app.db.unit_of_work import UnitOfWork
from app.modules.audit.repository import AuditRepository
from app.modules.audit.schemas import AuditLogOut
from app.shared.schemas import PaginatedResponse, PaginationParams

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs", response_model=PaginatedResponse[AuditLogOut])
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user: CurrentUser = Depends(require_roles(Role.ADMIN)),
    uow: UnitOfWork = Depends(get_uow),
):
    """Admin: full audit log (most recent first)."""
    params = PaginationParams(page=page, page_size=page_size)
    repo = AuditRepository(uow.session)
    items, total = await repo.list_all(skip=params.offset, limit=params.page_size)
    return PaginatedResponse.build(
        items=[AuditLogOut.model_validate(i) for i in items],
        total=total,
        params=params,
    )


@router.get("/logs/patient/{patient_id}", response_model=PaginatedResponse[AuditLogOut])
async def list_audit_logs_for_patient(
    patient_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user: CurrentUser = Depends(require_roles(Role.ADMIN)),
    uow: UnitOfWork = Depends(get_uow),
):
    """Admin: per-patient audit timeline."""
    params = PaginationParams(page=page, page_size=page_size)
    repo = AuditRepository(uow.session)
    items, total = await repo.list_by_patient(
        patient_id, skip=params.offset, limit=params.page_size
    )
    return PaginatedResponse.build(
        items=[AuditLogOut.model_validate(i) for i in items],
        total=total,
        params=params,
    )
