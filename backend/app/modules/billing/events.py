from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.core.events import DomainEvent


@dataclass(kw_only=True)
class InvoiceCreated(DomainEvent):
    invoice_id: UUID
