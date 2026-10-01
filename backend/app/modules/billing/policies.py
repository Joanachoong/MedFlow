from __future__ import annotations

from app.core.errors import ForbiddenError
from app.core.permissions import CurrentUser


class BillingPolicy:
    def can_create_invoice(self, user: CurrentUser) -> None:
        if not user.is_admin():
            raise ForbiddenError("Only admins can create invoices")

    def can_read_invoice(self, user: CurrentUser, patient_id=None) -> None:
        if user.is_admin():
            return
        if user.is_patient() and patient_id:
            return  # patient reads own invoices
        raise ForbiddenError("Access denied to this invoice")

    def can_update_invoice(self, user: CurrentUser) -> None:
        if not user.is_admin():
            raise ForbiddenError("Only admins can update invoices")
