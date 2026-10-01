from __future__ import annotations

from app.core.errors import ForbiddenError
from app.core.permissions import CurrentUser, Policy
from app.modules.scheduling.models import Appointment


class SchedulingPolicy(Policy):
    def authorize(self, user, action, resource=None):
        method = getattr(self, f"can_{action}", None)
        if method:
            method(user, resource)

    def can_create(self, user: CurrentUser, _=None) -> None:
        if not user.is_doctor():
            raise ForbiddenError("Only doctors can schedule appointments")

    def can_update(self, user: CurrentUser, appt: Appointment) -> None:
        if user.is_doctor() and str(appt.doctor_id) == str(user.id):
            return
        if user.is_admin():
            return
        raise ForbiddenError("You can only update your own appointments")

    def can_read(self, user: CurrentUser, appt: Appointment) -> None:
        if user.is_admin():
            return
        if user.is_doctor() and str(appt.doctor_id) == str(user.id):
            return
        if user.is_patient() and str(appt.patient_id):
            return
        raise ForbiddenError("Access denied to this appointment")
