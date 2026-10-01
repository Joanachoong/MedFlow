from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateAppointmentRequest(BaseModel):
    patient_id: UUID
    starts_at: datetime
    ends_at: datetime
    reason: str | None = None


class UpdateAppointmentRequest(BaseModel):
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    status: str | None = None
    reason: str | None = None


class AppointmentOut(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    starts_at: datetime
    ends_at: datetime
    status: str
    reason: str | None
    created_by: UUID
    created_at: datetime
