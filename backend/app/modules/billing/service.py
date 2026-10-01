from __future__ import annotations

from uuid import UUID

from app.core.events import bus
from app.core.permissions import CurrentUser
from app.db.unit_of_work import UnitOfWork
from app.modules.billing.events import InvoiceCreated
from app.modules.billing.models import Invoice
from app.modules.billing.policies import BillingPolicy
from app.modules.billing.repository import BillingRepository
from app.modules.billing.schemas import CreateInvoiceRequest


class BillingService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow
        self._repo = BillingRepository(uow.session)
        self._policy = BillingPolicy()

    async def create_invoice(self, actor: CurrentUser, body: CreateInvoiceRequest) -> Invoice:
        self._policy.can_create_invoice(actor)
        inv_number = await self._repo.next_invoice_number()
        inv = await self._repo.create_invoice(
            patient_id=body.patient_id,
            created_by=actor.id,
            invoice_number=inv_number,
            encounter_id=body.encounter_id,
            currency=body.currency,
            due_at=body.due_at,
            items=body.items,
        )
        await bus.publish(InvoiceCreated(
            actor_id=actor.id, patient_id=body.patient_id,
            session=self._uow.session, invoice_id=inv.id,
        ))
        return inv

    async def get_invoice(self, actor: CurrentUser, inv_id: UUID) -> Invoice:
        inv = await self._repo.get_by_id(inv_id)
        self._policy.can_read_invoice(actor, inv.patient_id)
        return inv

    async def list_patient_invoices(self, actor: CurrentUser, patient_id: UUID) -> list[Invoice]:
        self._policy.can_read_invoice(actor, patient_id)
        return await self._repo.list_for_patient(patient_id)
