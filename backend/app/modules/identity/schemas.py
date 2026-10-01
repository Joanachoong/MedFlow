from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


# ── Requests ──────────────────────────────────────────────────────────────────


class AssignRoleRequest(BaseModel):
    role: str  # validated by policies against allowed values


class ToggleActiveRequest(BaseModel):
    is_active: bool


class UpdateProfileRequest(BaseModel):
    full_name: str | None = None
    phone: str | None = None


# ── Responses ─────────────────────────────────────────────────────────────────


class ProfileOut(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    full_name: str
    email: str
    role: str
    public_id: str | None
    phone: str | None
    is_active: bool
    created_at: datetime
    deleted_at: datetime | None
