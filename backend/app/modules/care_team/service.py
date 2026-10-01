from __future__ import annotations

from uuid import UUID

from app.core.events import bus
from app.core.permissions import CurrentUser
from app.db.unit_of_work import UnitOfWork
from app.modules.care_team.events import NurseAssigned, PatientTransferred
from app.modules.care_team.exceptions import AlreadyAssignedError
from app.modules.care_team.models import NursePatientAssignment, PatientTransfer
from app.modules.care_team.policies import CareTeamPolicy
from app.modules.care_team.repository import CareTeamRepository
from app.modules.care_team.schemas import AssignNurseRequest, TransferPatientRequest


class CareTeamService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow
        self._repo = CareTeamRepository(uow.session)
        self._policy = CareTeamPolicy()

    async def assign_nurse(
        self, actor: CurrentUser, body: AssignNurseRequest
    ) -> NursePatientAssignment:
        self._policy.can_assign_nurse(actor)
        already = await self._repo.is_nurse_on_care_team(body.nurse_id, body.patient_id)
        if already:
            raise AlreadyAssignedError()
        assignment = await self._repo.create_nurse_assignment(
            nurse_id=body.nurse_id,
            patient_id=body.patient_id,
            assigned_by=actor.id,
        )
        await bus.publish(
            NurseAssigned(
                actor_id=actor.id,
                patient_id=body.patient_id,
                session=self._uow.session,
                nurse_id=body.nurse_id,
                assigned_by=actor.id,
            )
        )
        return assignment

    async def transfer_patient(
        self, actor: CurrentUser, patient_id: UUID, body: TransferPatientRequest
    ) -> PatientTransfer:
        # 1. Fetch active assignment — service does the DB call, policy does the check
        active_assignment = await self._repo.get_active_doctor_assignment(patient_id)
        self._policy.can_transfer(actor, active_assignment)

        # 2. Close old assignment, open new one, create transfer record
        await self._repo.close_doctor_assignment(patient_id)
        transfer = await self._repo.create_transfer(
            patient_id=patient_id,
            from_doctor_id=actor.id,
            to_doctor_id=body.to_doctor_id,
            transferred_by=actor.id,
            reason=body.reason,
            item_ids=body.item_ids,
            item_types=body.item_types,
        )
        await self._repo.create_doctor_assignment(
            doctor_id=body.to_doctor_id,
            patient_id=patient_id,
            transfer_id=transfer.id,
        )

        # 3. Publish event — audit subscriber writes in same TX
        await bus.publish(
            PatientTransferred(
                actor_id=actor.id,
                patient_id=patient_id,
                session=self._uow.session,
                transfer_id=transfer.id,
                from_doctor_id=actor.id,
                to_doctor_id=body.to_doctor_id,
            )
        )
        return transfer

    async def is_doctor_assigned(self, doctor_id: UUID, patient_id: UUID) -> bool:
        return await self._repo.is_doctor_assigned(doctor_id, patient_id)

    async def is_nurse_on_care_team(self, nurse_id: UUID, patient_id: UUID) -> bool:
        return await self._repo.is_nurse_on_care_team(nurse_id, patient_id)
