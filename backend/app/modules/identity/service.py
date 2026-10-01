from __future__ import annotations

from uuid import UUID

from app.core.events import bus
from app.core.permissions import CurrentUser
from app.db.unit_of_work import UnitOfWork
from app.modules.identity.events import AccountActivated, AccountDeactivated, RoleAssigned
from app.modules.identity.exceptions import CannotDeactivateSelfError
from app.modules.identity.models import Profile
from app.modules.identity.policies import IdentityPolicy
from app.modules.identity.repository import IdentityRepository
from app.modules.identity.schemas import UpdateProfileRequest


class IdentityService:
    """
    Orchestrates identity use cases.

    Flow for every method:
      1. policy check (raises ForbiddenError if denied) — NO DB
      2. repository call (DB read/write)
      3. publish domain event (before commit so audit is in same TX)
      4. caller commits via uow
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow
        self._repo = IdentityRepository(uow.session)
        self._policy = IdentityPolicy()

    # ── Reads ─────────────────────────────────────────────────────────────────

    async def get_profile(self, actor: CurrentUser, profile_id: UUID) -> Profile:
        self._policy.can_read_profile(actor, profile_id)
        return await self._repo.get_by_id(profile_id)

    async def list_profiles(
        self, actor: CurrentUser, skip: int = 0, limit: int = 20
    ) -> tuple[list[Profile], int]:
        self._policy.can_list_profiles(actor)
        return await self._repo.list_all(skip=skip, limit=limit)

    # ── Admin mutations ───────────────────────────────────────────────────────

    async def assign_role(
        self, actor: CurrentUser, target_id: UUID, new_role: str
    ) -> Profile:
        self._policy.can_assign_role(actor)
        profile = await self._repo.set_role(target_id, new_role)
        await bus.publish(
            RoleAssigned(
                actor_id=actor.id,
                patient_id=None,
                session=self._uow.session,
                target_user_id=target_id,
                new_role=new_role,
            )
        )
        return profile

    async def set_active(
        self, actor: CurrentUser, target_id: UUID, is_active: bool
    ) -> Profile:
        self._policy.can_toggle_active(actor)
        if str(actor.id) == str(target_id):
            raise CannotDeactivateSelfError()
        profile = await self._repo.set_active(target_id, is_active)
        event_cls = AccountActivated if is_active else AccountDeactivated
        await bus.publish(
            event_cls(
                actor_id=actor.id,
                patient_id=None,
                session=self._uow.session,
                target_user_id=target_id,
            )
        )
        return profile

    # ── Self-service ──────────────────────────────────────────────────────────

    async def update_profile(
        self, actor: CurrentUser, target_id: UUID, body: UpdateProfileRequest
    ) -> Profile:
        self._policy.can_update_profile(actor, target_id)
        return await self._repo.update(
            target_id,
            full_name=body.full_name,
            phone=body.phone,
        )
