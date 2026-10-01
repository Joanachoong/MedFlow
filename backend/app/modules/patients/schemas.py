from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class CreatePatientRequest(BaseModel):
    full_name: str
    date_of_birth: date | None = None
    phone: str | None = None
    blood_type: str | None = None
    allergies: str | None = None


class UpdatePatientRequest(BaseModel):
    full_name: str | None = None
    date_of_birth: date | None = None
    phone: str | None = None
    blood_type: str | None = None
    allergies: str | None = None
    status: str | None = None


class PatientOut(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    public_id: str
    full_name: str
    date_of_birth: date | None
    phone: str | None
    blood_type: str | None
    allergies: str | None
    status: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime | None
