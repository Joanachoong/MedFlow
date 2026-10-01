from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateEncounterRequest(BaseModel):
    patient_id: UUID
    encounter_type: str  # "admission" | "visit"
    reason: str | None = None
    ward: str | None = None
    appointment_id: UUID | None = None
    started_at: datetime


class DischargeRequest(BaseModel):
    ended_at: datetime


class EncounterOut(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    patient_id: UUID
    attending_doctor_id: UUID
    appointment_id: UUID | None
    encounter_type: str
    reason: str | None
    ward: str | None
    started_at: datetime
    ended_at: datetime | None
    created_by: UUID
