from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


# ── Clinical Notes ────────────────────────────────────────────────────────────

class CreateClinicalNoteRequest(BaseModel):
    patient_id: UUID
    diagnosis: str | None = None
    observation: str | None = None
    plan: str | None = None


class ClinicalNoteOut(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    diagnosis: str | None
    observation: str | None
    plan: str | None
    created_at: datetime
    updated_at: datetime | None


# ── Nurse Instructions ────────────────────────────────────────────────────────

class CreateNurseInstructionRequest(BaseModel):
    patient_id: UUID
    body: str
    priority: str = "routine"


class NurseInstructionOut(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    body: str
    priority: str
    created_at: datetime


# ── Care Notes ────────────────────────────────────────────────────────────────

class CreateCareNoteRequest(BaseModel):
    patient_id: UUID
    vitals: dict | None = None
    observation: str | None = None


class UpdateCareNoteRequest(BaseModel):
    vitals: dict | None = None
    observation: str | None = None


class CareNoteOut(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    patient_id: UUID
    nurse_id: UUID
    vitals: dict | None
    observation: str | None
    created_at: datetime


# ── Record Access Grants ──────────────────────────────────────────────────────

class GrantRecordAccessRequest(BaseModel):
    patient_id: UUID
    scope: str = "medical_record"


class RecordAccessGrantOut(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    patient_id: UUID
    scope: str
    granted_by: UUID
    granted_at: datetime
    revoked_at: datetime | None
