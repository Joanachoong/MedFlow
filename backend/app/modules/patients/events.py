from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.core.events import DomainEvent


@dataclass(kw_only=True)
class PatientCreated(DomainEvent):
    patient_id_new: UUID  # named differently from base patient_id to avoid confusion
