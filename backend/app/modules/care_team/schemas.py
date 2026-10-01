from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AssignNurseRequest(BaseModel):
    nurse_id: UUID
    patient_id: UUID


class TransferPatientRequest(BaseModel):
    to_doctor_id: UUID
    reason: str | None = None
    item_ids: list[UUID] = []       # clinical_note or nurse_instruction IDs
    item_types: list[str] = []      # parallel list: "clinical_note" | "nurse_instruction"


class AssignmentOut(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    doctor_id: UUID | None = None
    nurse_id: UUID | None = None
    patient_id: UUID
    assigned_at: datetime
    unassigned_at: datetime | None


class TransferOut(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    patient_id: UUID
    from_doctor_id: UUID
    to_doctor_id: UUID
    reason: str | None
    status: str
    transferred_by: UUID
    created_at: datetime
