from __future__ import annotations

from abc import ABC, abstractmethod
from enum import StrEnum
from dataclasses import dataclass
from uuid import UUID
from typing import Any


class Role(StrEnum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    NURSE = "nurse"
    ADMIN = "admin"
    # head_nurse added later via ALTER TYPE — placeholder so code stays stable
    # HEAD_NURSE = "head_nurse"


@dataclass(frozen=True)
class CurrentUser:
    """Immutable representation of the authenticated user for the lifetime of a request."""

    id: UUID
    role: Role
    email: str
    is_active: bool = True

    def has_role(self, *roles: Role) -> bool:
        return self.role in roles

    def is_doctor(self) -> bool:
        return self.role == Role.DOCTOR

    def is_nurse(self) -> bool:
        return self.role == Role.NURSE

    def is_admin(self) -> bool:
        return self.role == Role.ADMIN

    def is_patient(self) -> bool:
        return self.role == Role.PATIENT


class Policy(ABC):
    """
    Base class for all authorization policies.

    Rules:
    - Policies NEVER touch the database or call repositories.
    - If a permission check needs DB data, the service fetches it first and
      passes the result into the policy method.
    - Methods either return None (allowed) or raise ForbiddenError.
    """

    @abstractmethod
    def authorize(self, user: CurrentUser, action: str, resource: Any = None) -> None:
        """Raise ForbiddenError if not permitted. Do nothing if allowed."""
        ...
