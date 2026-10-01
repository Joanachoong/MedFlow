from __future__ import annotations

import uuid
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.models import AuditLog


class AuditRepository:
    """Append-only write repository for audit_logs. Only called by AuditSubscriber."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def insert(
        self,
        actor_id: UUID | None,
        actor_role: str | None,
        action: str,
        entity_type: str | None = None,
        entity_id: UUID | None = None,
        patient_id: UUID | None = None,
        changes: dict | None = None,
    ) -> AuditLog:
        log = AuditLog(
            id=uuid.uuid4(),
            actor_id=actor_id,
            actor_role=actor_role,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            patient_id=patient_id,
            changes=changes,
            created_at=datetime.now(timezone.utc),
        )
        self._session.add(log)
        return log

    async def list_all(
        self, skip: int = 0, limit: int = 50
    ) -> tuple[list[AuditLog], int]:
        from sqlalchemy import func

        total = (
            await self._session.execute(select(func.count()).select_from(AuditLog))
        ).scalar_one()
        rows = (
            await self._session.execute(
                select(AuditLog)
                .order_by(AuditLog.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
        ).scalars().all()
        return list(rows), total

    async def list_by_patient(
        self, patient_id: UUID, skip: int = 0, limit: int = 50
    ) -> tuple[list[AuditLog], int]:
        from sqlalchemy import func

        base = select(AuditLog).where(AuditLog.patient_id == patient_id)
        total = (
            await self._session.execute(
                select(func.count()).select_from(base.subquery())
            )
        ).scalar_one()
        rows = (
            await self._session.execute(
                base.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
            )
        ).scalars().all()
        return list(rows), total
