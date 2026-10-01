from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuditLogOut(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    actor_id: UUID | None
    actor_role: str | None
    action: str
    entity_type: str | None
    entity_id: UUID | None
    patient_id: UUID | None
    changes: dict | None
    created_at: datetime
