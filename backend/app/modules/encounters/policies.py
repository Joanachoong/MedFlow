from __future__ import annotations

from app.core.errors import ForbiddenError
from app.core.permissions import CurrentUser


class EncounterPolicy:
    def can_create(self, user: CurrentUser, _=None) -> None:
        if not (user.is_doctor() or user.is_admin()):
            raise ForbiddenError("Only doctors or admins can create encounters")

    def can_discharge(self, user: CurrentUser, _=None) -> None:
        if not (user.is_doctor() or user.is_admin()):
            raise ForbiddenError("Only doctors or admins can discharge patients")

    def can_read(self, user: CurrentUser, _=None) -> None:
        pass  # access matrix handled via query filtering
