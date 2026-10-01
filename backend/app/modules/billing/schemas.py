from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class InvoiceItemIn(BaseModel):
    category: str
    description: str
    quantity: int = 1
    unit_price: float


class CreateInvoiceRequest(BaseModel):
    patient_id: UUID
    encounter_id: UUID | None = None
    currency: str = "USD"
    due_at: datetime | None = None
    items: list[InvoiceItemIn] = []


class InvoiceItemOut(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    invoice_id: UUID
    category: str
    description: str
    quantity: int
    unit_price: float
    line_total: float


class InvoiceOut(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    invoice_number: str
    patient_id: UUID
    encounter_id: UUID | None
    status: str
    currency: str
    total: float
    issued_at: datetime | None
    due_at: datetime | None
    paid_at: datetime | None
    created_by: UUID
