from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.core.events import DomainEvent
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(kw_only=True)
class RoleAssigned(DomainEvent):
    target_user_id: UUID
    new_role: str


@dataclass(kw_only=True)
class AccountDeactivated(DomainEvent):
    target_user_id: UUID


@dataclass(kw_only=True)
class AccountActivated(DomainEvent):
    target_user_id: UUID
