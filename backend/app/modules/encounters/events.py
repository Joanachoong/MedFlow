from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.core.events import DomainEvent


@dataclass(kw_only=True)
class PatientAdmitted(DomainEvent):
    encounter_id: UUID


@dataclass(kw_only=True)
class PatientDischarged(DomainEvent):
    encounter_id: UUID
