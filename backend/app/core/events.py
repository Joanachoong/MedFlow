from __future__ import annotations

import asyncio
import logging
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

E = TypeVar("E", bound="DomainEvent")


@dataclass(kw_only=True)
class DomainEvent(ABC):
    """
    Base class for every domain event published by a module's service layer.

    All fields are keyword-only (kw_only=True) so subclasses can freely add
    their own required fields without triggering the "non-default argument
    follows default argument" error.

    The `session` field carries the current request's DB session so the
    audit subscriber writes the audit log row in the SAME transaction as
    the business change.
    """

    actor_id: UUID
    patient_id: UUID | None
    session: AsyncSession  # shared with the service's UoW
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class EventBus:
    """
    Lightweight, in-process synchronous/asynchronous event bus.

    Usage
    -----
    # subscribe (done once at startup)
    bus.subscribe(PatientTransferred, audit_subscriber.handle_patient_transferred)

    # publish (called by service.py after the DB write, before commit)
    await bus.publish(PatientTransferred(actor_id=..., patient_id=..., session=uow.session))
    """

    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable]] = {}

    def subscribe(self, event_type: type[E], handler: Callable[[E], None]) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def subscribe_all(self, subscriber: object) -> None:
        """
        Auto-register all methods named handle_<event_type_lower> on a subscriber.
        The method must have a type annotation named `event` pointing to the event class.
        """
        for attr_name in dir(subscriber):
            if not attr_name.startswith("handle_"):
                continue
            method = getattr(subscriber, attr_name)
            if not callable(method):
                continue
            hints = getattr(method, "__annotations__", {})
            event_type = hints.get("event")
            if event_type is not None:
                self.subscribe(event_type, method)

    async def publish(self, event: DomainEvent) -> None:
        handlers = self._handlers.get(type(event), [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception:
                logger.exception(
                    "Event handler %s failed for %s",
                    handler.__qualname__,
                    type(event).__name__,
                )


# Module-level singleton — imported by services and registered at startup.
bus = EventBus()
