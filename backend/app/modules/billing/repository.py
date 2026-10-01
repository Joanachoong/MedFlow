from __future__ import annotations

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.modules.billing.models import Invoice, InvoiceItem
from app.modules.billing.schemas import InvoiceItemIn


class BillingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_invoice(
        self,
        patient_id: UUID,
        created_by: UUID,
        invoice_number: str,
        items: list[InvoiceItemIn],
        **fields,
    ) -> Invoice:
        total = sum(i.unit_price * i.quantity for i in items)
        inv = Invoice(
            id=uuid.uuid4(),
            invoice_number=invoice_number,
            patient_id=patient_id,
            created_by=created_by,
            total=total,
            **fields,
        )
        self._session.add(inv)
        await self._session.flush()

        for item in items:
            self._session.add(InvoiceItem(
                id=uuid.uuid4(),
                invoice_id=inv.id,
                category=item.category,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                line_total=item.unit_price * item.quantity,
            ))
        await self._session.refresh(inv)
        return inv

    async def get_by_id(self, inv_id: UUID) -> Invoice:
        result = await self._session.get(Invoice, inv_id)
        if result is None:
            raise NotFoundError("Invoice", str(inv_id))
        return result

    async def list_for_patient(self, patient_id: UUID) -> list[Invoice]:
        stmt = select(Invoice).where(Invoice.patient_id == patient_id).order_by(Invoice.id.desc())
        return list((await self._session.execute(stmt)).scalars().all())

    async def next_invoice_number(self) -> str:
        from sqlalchemy import func
        count = (await self._session.execute(select(func.count()).select_from(Invoice))).scalar_one()
        return f"INV-{(count + 1):05d}"
