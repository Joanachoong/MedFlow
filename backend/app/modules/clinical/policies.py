from __future__ import annotations

from app.core.errors import ForbiddenError
from app.core.permissions import CurrentUser, Policy, Role
from app.modules.clinical.models import CareNote, ClinicalNote, RecordAccessGrant


class ClinicalPolicy(Policy):
    """
    Authorization for all clinical resources.
    Service fetches assignment/grant data; policy only inspects it.
    """

    def authorize(self, user: CurrentUser, action: str, resource=None) -> None:
        method = getattr(self, f"can_{action}", None)
        if method:
            method(user, resource)

    # ── Clinical Notes ────────────────────────────────────────────────────────

    def can_create_clinical_note(self, user: CurrentUser, _=None) -> None:
        if not user.is_doctor():
            raise ForbiddenError("Only doctors can create clinical notes")

    def can_read_clinical_note(
        self,
        user: CurrentUser,
        note: ClinicalNote,
        is_assigned_doctor: bool = False,
        is_transferred: bool = False,
        has_active_grant: bool = False,
    ) -> None:
        if user.is_doctor() and (is_assigned_doctor or is_transferred or str(note.doctor_id) == str(user.id)):
            return
        if user.is_nurse() and is_assigned_doctor:  # nurse on care team sees doctor notes
            return
        if user.is_patient() and has_active_grant and str(note.patient_id):
            return
        raise ForbiddenError("You do not have access to this clinical note")

    # ── Nurse Instructions ────────────────────────────────────────────────────

    def can_create_nurse_instruction(self, user: CurrentUser, _=None) -> None:
        if not user.is_doctor():
            raise ForbiddenError("Only doctors can create nurse instructions")

    def can_read_nurse_instruction(
        self, user: CurrentUser, is_care_team_nurse: bool = False, is_author: bool = False
    ) -> None:
        if user.is_doctor() and is_author:
            return
        if user.is_nurse() and is_care_team_nurse:
            return
        raise ForbiddenError("You do not have access to this nurse instruction")

    # ── Care Notes ────────────────────────────────────────────────────────────

    def can_create_care_note(self, user: CurrentUser, is_care_team: bool = False) -> None:
        if not user.is_nurse():
            raise ForbiddenError("Only nurses can create care notes")
        if not is_care_team:
            raise ForbiddenError("You are not on the care team for this patient")

    def can_update_care_note(self, user: CurrentUser, note: CareNote) -> None:
        if not user.is_nurse():
            raise ForbiddenError("Only nurses can update care notes")
        if str(note.nurse_id) != str(user.id):
            raise ForbiddenError("You can only update your own care notes")

    def can_delete_care_note(self, user: CurrentUser, note: CareNote) -> None:
        self.can_update_care_note(user, note)

    # ── Record Access Grants ──────────────────────────────────────────────────

    def can_grant_record_access(self, user: CurrentUser, is_assigned: bool = False) -> None:
        if not user.is_doctor():
            raise ForbiddenError("Only doctors can grant record access")
        if not is_assigned:
            raise ForbiddenError("You can only grant access for your own patients")

    def can_revoke_record_access(self, user: CurrentUser, grant: RecordAccessGrant) -> None:
        if not user.is_doctor():
            raise ForbiddenError("Only doctors can revoke record access")
        if str(grant.granted_by) != str(user.id):
            raise ForbiddenError("You can only revoke grants you created")
