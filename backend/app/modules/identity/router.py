from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_current_user, get_uow, require_roles
from app.core.permissions import CurrentUser, Role
from app.db.unit_of_work import UnitOfWork
from app.modules.identity.schemas import AssignRoleRequest, ProfileOut, ToggleActiveRequest, UpdateProfileRequest
from app.modules.identity.service import IdentityService
from app.shared.schemas import PaginatedResponse, PaginationParams

router = APIRouter(prefix="/identity", tags=["identity"])


def _svc(uow: UnitOfWork = Depends(get_uow)) -> IdentityService:
    return IdentityService(uow)


# ── Profile reads ──────────────────────────────────────────────────────────────


@router.get("/me", response_model=ProfileOut)
async def get_my_profile(
    user: CurrentUser = Depends(get_current_user),
    svc: IdentityService = Depends(_svc),
):
    """Any authenticated user can fetch their own profile."""
    return await svc.get_profile(user, user.id)


@router.get("/profiles", response_model=PaginatedResponse[ProfileOut])
async def list_profiles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: CurrentUser = Depends(require_roles(Role.ADMIN)),
    svc: IdentityService = Depends(_svc),
    uow: UnitOfWork = Depends(get_uow),
):
    """Admin: list all user profiles."""
    params = PaginationParams(page=page, page_size=page_size)
    items, total = await svc.list_profiles(user, skip=params.offset, limit=params.page_size)
    return PaginatedResponse.build(
        items=[ProfileOut.model_validate(p) for p in items],
        total=total,
        params=params,
    )


@router.get("/profiles/{profile_id}", response_model=ProfileOut)
async def get_profile(
    profile_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    svc: IdentityService = Depends(_svc),
):
    profile = await svc.get_profile(user, profile_id)
    return ProfileOut.model_validate(profile)


# ── Admin mutations ────────────────────────────────────────────────────────────


@router.patch("/profiles/{profile_id}/role", response_model=ProfileOut)
async def assign_role(
    profile_id: UUID,
    body: AssignRoleRequest,
    user: CurrentUser = Depends(require_roles(Role.ADMIN)),
    svc: IdentityService = Depends(_svc),
    uow: UnitOfWork = Depends(get_uow),
):
    profile = await svc.assign_role(user, profile_id, body.role)
    await uow.commit()
    return ProfileOut.model_validate(profile)


@router.patch("/profiles/{profile_id}/active", response_model=ProfileOut)
async def toggle_active(
    profile_id: UUID,
    body: ToggleActiveRequest,
    user: CurrentUser = Depends(require_roles(Role.ADMIN)),
    svc: IdentityService = Depends(_svc),
    uow: UnitOfWork = Depends(get_uow),
):
    profile = await svc.set_active(user, profile_id, body.is_active)
    await uow.commit()
    return ProfileOut.model_validate(profile)


# ── Self-service ───────────────────────────────────────────────────────────────


@router.patch("/profiles/{profile_id}", response_model=ProfileOut)
async def update_profile(
    profile_id: UUID,
    body: UpdateProfileRequest,
    user: CurrentUser = Depends(get_current_user),
    svc: IdentityService = Depends(_svc),
    uow: UnitOfWork = Depends(get_uow),
):
    profile = await svc.update_profile(user, profile_id, body)
    await uow.commit()
    return ProfileOut.model_validate(profile)
