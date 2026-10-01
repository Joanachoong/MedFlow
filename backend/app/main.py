from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.events import bus
from app.core.logging import configure_logging
from app.api.v1.router import api_router
from app.modules.audit.subscriber import AuditSubscriber


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────────
    configure_logging()

    # Register all domain event → audit log handlers
    audit_sub = AuditSubscriber()
    bus.subscribe_all(audit_sub)

    # Wire care_team events into audit subscriber
    from app.modules.care_team.events import PatientTransferred, NurseAssigned
    from app.modules.clinical.events import (
        ClinicalNoteCreated, NurseInstructionCreated, CareNoteCreated,
        RecordAccessGranted, RecordAccessRevoked,
    )
    from app.modules.patients.events import PatientCreated
    from app.modules.encounters.events import PatientAdmitted, PatientDischarged
    from app.modules.billing.events import InvoiceCreated
    from app.modules.scheduling.events import AppointmentCreated

    async def _audit_generic(event, action: str):
        from app.modules.audit.repository import AuditRepository
        repo = AuditRepository(event.session)
        await repo.insert(
            actor_id=event.actor_id,
            actor_role=None,
            action=action,
            patient_id=event.patient_id,
        )

    bus.subscribe(PatientTransferred, lambda e: _audit_generic(e, "patient.transfer"))
    bus.subscribe(NurseAssigned, lambda e: _audit_generic(e, "nurse.assign"))
    bus.subscribe(PatientCreated, lambda e: _audit_generic(e, "patient.create"))
    bus.subscribe(ClinicalNoteCreated, lambda e: _audit_generic(e, "clinical_note.create"))
    bus.subscribe(NurseInstructionCreated, lambda e: _audit_generic(e, "nurse_instruction.create"))
    bus.subscribe(CareNoteCreated, lambda e: _audit_generic(e, "care_note.create"))
    bus.subscribe(RecordAccessGranted, lambda e: _audit_generic(e, "record_access.grant"))
    bus.subscribe(RecordAccessRevoked, lambda e: _audit_generic(e, "record_access.revoke"))
    bus.subscribe(PatientAdmitted, lambda e: _audit_generic(e, "patient.admit"))
    bus.subscribe(PatientDischarged, lambda e: _audit_generic(e, "patient.discharge"))
    bus.subscribe(InvoiceCreated, lambda e: _audit_generic(e, "invoice.create"))
    bus.subscribe(AppointmentCreated, lambda e: _audit_generic(e, "appointment.create"))

    yield
    # ── Shutdown ─────────────────────────────────────────────────────────────
    # Nothing to clean up for now.


def create_app() -> FastAPI:
    app = FastAPI(
        title="MedFlow API",
        version="1.0.0",
        description="Modular monolith backend for MedFlow hospital management.",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health", tags=["health"])
    def health():
        return {"status": "ok", "project": "MedFlow"}

    return app


app = create_app()