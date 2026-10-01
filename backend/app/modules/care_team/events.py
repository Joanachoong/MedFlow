from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.core.events import DomainEvent


@dataclass(kw_only=True)
class PatientTransferred(DomainEvent):
    transfer_id: UUID
    from_doctor_id: UUID
    to_doctor_id: UUID


@dataclass(kw_only=True)
class NurseAssigned(DomainEvent):
    nurse_id: UUID
    assigned_by: UUID
