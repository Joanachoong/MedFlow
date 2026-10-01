from __future__ import annotations

from app.core.errors import ForbiddenError
from app.core.permissions import CurrentUser, Policy, Role
from app.modules.patients.models import Patient


class PatientPolicy(Policy):
    """
    Authorization rules for patient records.
    NO database calls — the service fetches any needed assignment data
    before calling these methods.
    """

    def authorize(self, user: CurrentUser, action: str, resource=None) -> None:
        method = getattr(self, f"can_{action}", None)
        if method:
            method(user, resource)

    def can_create(self, user: CurrentUser, _=None) -> None:
        if not user.is_doctor():
            raise ForbiddenError("Only doctors can register patients")

    def can_read(
        self,
        user: CurrentUser,
        patient: Patient,
        is_assigned: bool = False,
        is_care_team: bool = False,
    ) -> None:
        if user.is_admin():
            return
        if user.is_doctor() and (is_assigned or str(patient.created_by) == str(user.id)):
            return
        if user.is_nurse() and is_care_team:
            return
        if user.is_patient() and str(patient.user_id) == str(user.id):
            return
        raise ForbiddenError("You do not have access to this patient record")

    def can_update(self, user: CurrentUser, patient: Patient, is_assigned: bool = False) -> None:
        if user.is_doctor() and (is_assigned or str(patient.created_by) == str(user.id)):
            return
        raise ForbiddenError("Only the assigned doctor can update this patient record")

    def can_list(self, user: CurrentUser, _=None) -> None:
        # Each role gets a filtered list — listing itself is always allowed;
        # filtering happens in the repository query.
        pass
