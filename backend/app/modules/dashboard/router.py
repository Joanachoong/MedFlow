from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_current_user, get_uow
from app.core.permissions import CurrentUser
from app.db.unit_of_work import UnitOfWork
from app.modules.dashboard.service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
async def get_dashboard(
    patient_id: UUID | None = Query(None, description="Required for patient role"),
    user: CurrentUser = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    """
    Role-aware dashboard endpoint. Returns different payloads per role.
    Patient role requires passing patient_id (their own patient record ID).
    """
    svc = DashboardService(uow)
    return await svc.get_dashboard(user, patient_record_id=patient_id)
