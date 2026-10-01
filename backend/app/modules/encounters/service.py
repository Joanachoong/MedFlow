from __future__ import annotations

from uuid import UUID

from app.core.events import bus
from app.core.permissions import CurrentUser
from app.db.unit_of_work import UnitOfWork
from app.modules.encounters.events import PatientAdmitted, PatientDischarged
from app.modules.encounters.models import Encounter
from app.modules.encounters.policies import EncounterPolicy
from app.modules.encounters.repository import EncounterRepository
from app.modules.encounters.schemas import CreateEncounterRequest, DischargeRequest


class EncounterService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow
        self._repo = EncounterRepository(uow.session)
        self._policy = EncounterPolicy()

    async def create_encounter(self, actor: CurrentUser, body: CreateEncounterRequest) -> Encounter:
        self._policy.can_create(actor)
        enc = await self._repo.create(
            patient_id=body.patient_id,
            attending_doctor_id=actor.id,
            appointment_id=body.appointment_id,
            encounter_type=body.encounter_type,
            reason=body.reason,
            ward=body.ward,
            started_at=body.started_at,
            created_by=actor.id,
        )
        await bus.publish(PatientAdmitted(
            actor_id=actor.id, patient_id=body.patient_id,
            session=self._uow.session, encounter_id=enc.id,
        ))
        return enc

    async def discharge(self, actor: CurrentUser, enc_id: UUID, body: DischargeRequest) -> Encounter:
        self._policy.can_discharge(actor)
        enc = await self._repo.discharge(enc_id, body.ended_at)
        await bus.publish(PatientDischarged(
            actor_id=actor.id, patient_id=enc.patient_id,
            session=self._uow.session, encounter_id=enc_id,
        ))
        return enc

    async def list_active_admissions(self, actor: CurrentUser) -> list[Encounter]:
        return await self._repo.list_active_admissions()
