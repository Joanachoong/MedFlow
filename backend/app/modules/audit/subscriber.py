from __future__ import annotations

from app.core.events import DomainEvent
from app.modules.audit.repository import AuditRepository

# Import every event type that should be audited.
# Add new imports here as new modules are built.
from app.modules.identity.events import AccountActivated, AccountDeactivated, RoleAssigned


class AuditSubscriber:
    """
    Listens to domain events from all modules and writes audit_logs rows
    in the SAME session (and therefore the same DB transaction) as the
    originating business change.

    The `subscribe_all` helper on EventBus auto-discovers handle_* methods
    and maps them to the annotated event type.
    """

    # ── identity ──────────────────────────────────────────────────────────────

    async def handle_role_assigned(self, event: RoleAssigned) -> None:
        repo = AuditRepository(event.session)
        await repo.insert(
            actor_id=event.actor_id,
            actor_role=None,
            action="role.assign",
            entity_type="profile",
            entity_id=event.target_user_id,
            changes={"new_role": event.new_role},
        )

    async def handle_account_deactivated(self, event: AccountDeactivated) -> None:
        repo = AuditRepository(event.session)
        await repo.insert(
            actor_id=event.actor_id,
            actor_role=None,
            action="account.deactivate",
            entity_type="profile",
            entity_id=event.target_user_id,
        )

    async def handle_account_activated(self, event: AccountActivated) -> None:
        repo = AuditRepository(event.session)
        await repo.insert(
            actor_id=event.actor_id,
            actor_role=None,
            action="account.activate",
            entity_type="profile",
            entity_id=event.target_user_id,
        )

    # ── care_team (imported lazily to avoid circular imports at module load) ──

    async def _handle_generic(
        self, event: DomainEvent, action: str, entity_type: str, entity_id=None, changes: dict | None = None
    ) -> None:
        repo = AuditRepository(event.session)
        await repo.insert(
            actor_id=event.actor_id,
            actor_role=None,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            patient_id=event.patient_id,
            changes=changes,
        )
