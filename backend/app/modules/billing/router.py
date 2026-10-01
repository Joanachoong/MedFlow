from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, get_uow, require_roles
from app.core.permissions import CurrentUser, Role
from app.db.unit_of_work import UnitOfWork
from app.modules.billing.schemas import CreateInvoiceRequest, InvoiceOut
from app.modules.billing.service import BillingService

router = APIRouter(prefix="/billing", tags=["billing"])


def _svc(uow: UnitOfWork = Depends(get_uow)) -> BillingService:
    return BillingService(uow)


@router.post("/invoices", response_model=InvoiceOut, status_code=201)
async def create_invoice(
    body: CreateInvoiceRequest,
    user: CurrentUser = Depends(require_roles(Role.ADMIN)),
    svc: BillingService = Depends(_svc),
    uow: UnitOfWork = Depends(get_uow),
):
    inv = await svc.create_invoice(user, body)
    await uow.commit()
    return InvoiceOut.model_validate(inv)


@router.get("/invoices/{inv_id}", response_model=InvoiceOut)
async def get_invoice(
    inv_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    svc: BillingService = Depends(_svc),
):
    inv = await svc.get_invoice(user, inv_id)
    return InvoiceOut.model_validate(inv)


@router.get("/invoices/patient/{patient_id}", response_model=list[InvoiceOut])
async def list_patient_invoices(
    patient_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    svc: BillingService = Depends(_svc),
):
    items = await svc.list_patient_invoices(user, patient_id)
    return [InvoiceOut.model_validate(i) for i in items]
