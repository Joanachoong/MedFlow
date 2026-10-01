from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.core.events import DomainEvent


@dataclass(kw_only=True)
class ClinicalNoteCreated(DomainEvent):
    note_id: UUID


@dataclass(kw_only=True)
class NurseInstructionCreated(DomainEvent):
    instruction_id: UUID


@dataclass(kw_only=True)
class CareNoteCreated(DomainEvent):
    note_id: UUID


@dataclass(kw_only=True)
class RecordAccessGranted(DomainEvent):
    grant_id: UUID
    scope: str


@dataclass(kw_only=True)
class RecordAccessRevoked(DomainEvent):
    grant_id: UUID
