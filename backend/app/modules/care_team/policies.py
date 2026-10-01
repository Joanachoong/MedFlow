from __future__ import annotations

from app.core.errors import ForbiddenError
from app.core.permissions import CurrentUser, Policy, Role
from app.modules.care_team.models import DoctorPatientAssignment


class CareTeamPolicy(Policy):
    """
    Authorization rules for assignments and transfers.
    NO database calls.
    """

    def authorize(self, user: CurrentUser, action: str, resource=None) -> None:
        method = getattr(self, f"can_{action}", None)
        if method:
            method(user, resource)

    def can_assign_nurse(self, user: CurrentUser, _=None) -> None:
        if not (user.is_doctor() or user.is_admin()):
            raise ForbiddenError("Only doctors or admins can assign nurses to patients")

    def can_transfer(
        self,
        user: CurrentUser,
        assignment: DoctorPatientAssignment | None,
    ) -> None:
        """Only the currently assigned doctor can transfer a patient."""
        if not user.is_doctor():
            raise ForbiddenError("Only doctors can transfer patients")
        if assignment is None or str(assignment.doctor_id) != str(user.id):
            raise ForbiddenError("You can only transfer patients currently assigned to you")

    def can_view_assignments(self, user: CurrentUser, _=None) -> None:
        if user.is_patient():
            raise ForbiddenError("Patients cannot view assignment records")
