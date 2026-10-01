from __future__ import annotations

from app.core.errors import ForbiddenError
from app.core.permissions import CurrentUser, Policy, Role


class IdentityPolicy(Policy):
    """
    Authorization rules for the identity module.
    NO database calls — service fetches any needed data first.
    """

    def authorize(self, user: CurrentUser, action: str, resource=None) -> None:
        method = getattr(self, f"can_{action}", None)
        if method:
            method(user, resource)

    # ── Admin-only operations ─────────────────────────────────────────────────

    def can_assign_role(self, user: CurrentUser, _=None) -> None:
        if not user.is_admin():
            raise ForbiddenError("Only admins can assign roles")

    def can_toggle_active(self, user: CurrentUser, _=None) -> None:
        if not user.is_admin():
            raise ForbiddenError("Only admins can activate or deactivate accounts")

    def can_list_profiles(self, user: CurrentUser, _=None) -> None:
        if not user.is_admin():
            raise ForbiddenError("Only admins can list all profiles")

    # ── Self or admin ─────────────────────────────────────────────────────────

    def can_read_profile(self, user: CurrentUser, target_profile_id=None) -> None:
        """A user can always read their own profile; admins can read any."""
        if user.is_admin():
            return
        if target_profile_id and str(user.id) != str(target_profile_id):
            raise ForbiddenError("You can only view your own profile")

    def can_update_profile(self, user: CurrentUser, target_profile_id=None) -> None:
        if user.is_admin():
            return
        if target_profile_id and str(user.id) != str(target_profile_id):
            raise ForbiddenError("You can only update your own profile")
