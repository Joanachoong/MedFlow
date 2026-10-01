from __future__ import annotations

from uuid import UUID

from app.core.events import bus
from app.core.permissions import CurrentUser
from app.db.unit_of_work import UnitOfWork
from app.modules.patients.events import PatientCreated
from app.modules.patients.models import Patient
from app.modules.patients.policies import PatientPolicy
from app.modules.patients.repository import PatientRepository
from app.modules.patients.schemas import CreatePatientRequest, UpdatePatientRequest
from app.shared.utils import generate_public_id


class PatientService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow
        self._repo = PatientRepository(uow.session)
        self._policy = PatientPolicy()

    async def create_patient(
        self, actor: CurrentUser, body: CreatePatientRequest
    ) -> Patient:
        self._policy.can_create(actor)
        seq = await self._repo.next_sequence()
        public_id = generate_public_id("P", seq)
        patient = await self._repo.create(
            created_by=actor.id,
            public_id=public_id,
            full_name=body.full_name,
            date_of_birth=body.date_of_birth,
            phone=body.phone,
            blood_type=body.blood_type,
            allergies=body.allergies,
        )
        await bus.publish(
            PatientCreated(
                actor_id=actor.id,
                patient_id=patient.id,
                session=self._uow.session,
                patient_id_new=patient.id,
            )
        )
        return patient

    async def get_patient(
        self,
        actor: CurrentUser,
        patient_id: UUID,
        is_assigned: bool = False,
        is_care_team: bool = False,
    ) -> Patient:
        patient = await self._repo.get_by_id(patient_id)
        self._policy.can_read(actor, patient, is_assigned=is_assigned, is_care_team=is_care_team)
        return patient

    async def get_my_patient_record(self, actor: CurrentUser) -> Patient:
        """For patient portal — fetch the patient row linked to the logged-in user."""
        patient = await self._repo.get_by_user_id(actor.id)
        if patient is None:
            from app.core.errors import NotFoundError
            raise NotFoundError("Patient record for this user")
        return patient

    async def update_patient(
        self,
        actor: CurrentUser,
        patient_id: UUID,
        body: UpdatePatientRequest,
        is_assigned: bool = False,
    ) -> Patient:
        patient = await self._repo.get_by_id(patient_id)
        self._policy.can_update(actor, patient, is_assigned=is_assigned)
        return await self._repo.update(
            patient_id,
            full_name=body.full_name,
            date_of_birth=body.date_of_birth,
            phone=body.phone,
            blood_type=body.blood_type,
            allergies=body.allergies,
            status=body.status,
        )

    async def list_my_patients(
        self, actor: CurrentUser, skip: int = 0, limit: int = 20
    ) -> tuple[list[Patient], int]:
        """Doctor: list patients they registered."""
        return await self._repo.list_by_doctor(actor.id, skip=skip, limit=limit)
