from __future__ import annotations

from uuid import UUID

from app.core.events import bus
from app.core.permissions import CurrentUser
from app.db.unit_of_work import UnitOfWork
from app.modules.scheduling.events import AppointmentCreated
from app.modules.scheduling.models import Appointment
from app.modules.scheduling.policies import SchedulingPolicy
from app.modules.scheduling.repository import SchedulingRepository
from app.modules.scheduling.schemas import CreateAppointmentRequest, UpdateAppointmentRequest


class SchedulingService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow
        self._repo = SchedulingRepository(uow.session)
        self._policy = SchedulingPolicy()

    async def create_appointment(self, actor: CurrentUser, body: CreateAppointmentRequest) -> Appointment:
        self._policy.can_create(actor)
        appt = await self._repo.create(
            patient_id=body.patient_id,
            doctor_id=actor.id,
            created_by=actor.id,
            starts_at=body.starts_at,
            ends_at=body.ends_at,
            reason=body.reason,
        )
        await bus.publish(AppointmentCreated(
            actor_id=actor.id, patient_id=body.patient_id,
            session=self._uow.session, appointment_id=appt.id,
        ))
        return appt

    async def list_for_doctor(self, actor: CurrentUser) -> list[Appointment]:
        return await self._repo.list_for_doctor(actor.id)

    async def list_for_patient(self, actor: CurrentUser) -> list[Appointment]:
        # Patient portal: returns their own appointments
        # patient.user_id == actor.id — need patient_id from patients module
        # Simplified for MVP: caller passes patient_id
        return []

    async def list_for_patient_id(self, patient_id: UUID) -> list[Appointment]:
        return await self._repo.list_for_patient(patient_id)

    async def update_appointment(self, actor: CurrentUser, appt_id: UUID, body: UpdateAppointmentRequest) -> Appointment:
        appt = await self._repo.get_by_id(appt_id)
        self._policy.can_update(actor, appt)
        return await self._repo.update(appt_id, starts_at=body.starts_at, ends_at=body.ends_at, status=body.status, reason=body.reason)
