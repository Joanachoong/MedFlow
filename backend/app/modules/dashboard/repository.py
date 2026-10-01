from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.models import AuditLog
from app.modules.billing.models import Invoice
from app.modules.care_team.models import DoctorPatientAssignment, NursePatientAssignment
from app.modules.clinical.models import ClinicalNote, NurseInstruction
from app.modules.encounters.models import Encounter
from app.modules.identity.models import Profile
from app.modules.patients.models import Patient
from app.modules.scheduling.models import Appointment


class DashboardRepository:
    """
    Read-model repository for the dashboard module.
    Queries span multiple module tables. This is intentional: the dashboard
    is a cross-cutting read concern that lives in its own module with its own
    repository rather than scattered across other modules' services.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Admin ─────────────────────────────────────────────────────────────────

    async def admitted_now_count(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(Encounter).where(
                Encounter.encounter_type == "admission",
                Encounter.ended_at.is_(None),
            )
        )
        return result.scalar_one()

    async def visits_today_count(self) -> int:
        from sqlalchemy import cast, Date
        today = datetime.now(timezone.utc).date()
        result = await self._session.execute(
            select(func.count()).select_from(Encounter).where(
                Encounter.encounter_type == "visit",
                func.date(Encounter.started_at) == today,
            )
        )
        return result.scalar_one()

    async def appointments_today_count(self) -> int:
        from sqlalchemy import cast, Date
        today = datetime.now(timezone.utc).date()
        result = await self._session.execute(
            select(func.count()).select_from(Appointment).where(
                func.date(Appointment.starts_at) == today,
            )
        )
        return result.scalar_one()

    async def active_users_by_role(self) -> dict[str, int]:
        rows = await self._session.execute(
            select(Profile.role, func.count().label("cnt"))
            .where(Profile.is_active == True, Profile.deleted_at.is_(None))
            .group_by(Profile.role)
        )
        return {row.role: row.cnt for row in rows}

    async def critical_patient_count(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(Patient).where(
                Patient.status == "critical",
                Patient.deleted_at.is_(None),
            )
        )
        return result.scalar_one()

    async def latest_audit_events(self, limit: int = 10) -> list[AuditLog]:
        rows = await self._session.execute(
            select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        )
        return list(rows.scalars().all())

    # ── Doctor ────────────────────────────────────────────────────────────────

    async def doctor_assigned_patients(self, doctor_id: UUID) -> list[Patient]:
        stmt = (
            select(Patient)
            .join(DoctorPatientAssignment, DoctorPatientAssignment.patient_id == Patient.id)
            .where(
                DoctorPatientAssignment.doctor_id == doctor_id,
                DoctorPatientAssignment.unassigned_at.is_(None),
                Patient.deleted_at.is_(None),
            )
        )
        return list((await self._session.execute(stmt)).scalars().all())

    async def doctor_todays_appointments(self, doctor_id: UUID) -> list[Appointment]:
        today = datetime.now(timezone.utc).date()
        stmt = select(Appointment).where(
            Appointment.doctor_id == doctor_id,
            func.date(Appointment.starts_at) == today,
        ).order_by(Appointment.starts_at)
        return list((await self._session.execute(stmt)).scalars().all())

    async def doctor_recent_notes(self, doctor_id: UUID, limit: int = 5) -> list[ClinicalNote]:
        stmt = (
            select(ClinicalNote)
            .where(ClinicalNote.doctor_id == doctor_id, ClinicalNote.deleted_at.is_(None))
            .order_by(ClinicalNote.created_at.desc())
            .limit(limit)
        )
        return list((await self._session.execute(stmt)).scalars().all())

    # ── Nurse ─────────────────────────────────────────────────────────────────

    async def nurse_care_team_patients(self, nurse_id: UUID) -> list[Patient]:
        stmt = (
            select(Patient)
            .join(NursePatientAssignment, NursePatientAssignment.patient_id == Patient.id)
            .where(
                NursePatientAssignment.nurse_id == nurse_id,
                NursePatientAssignment.unassigned_at.is_(None),
                Patient.deleted_at.is_(None),
            )
            .order_by(Patient.status)  # critical sorts first alphabetically but see note below
        )
        return list((await self._session.execute(stmt)).scalars().all())

    async def nurse_new_instructions(self, nurse_id: UUID) -> list[NurseInstruction]:
        # Instructions for patients on nurse's care team, ordered by priority
        patient_ids_stmt = select(NursePatientAssignment.patient_id).where(
            NursePatientAssignment.nurse_id == nurse_id,
            NursePatientAssignment.unassigned_at.is_(None),
        )
        stmt = (
            select(NurseInstruction)
            .where(
                NurseInstruction.patient_id.in_(patient_ids_stmt),
                NurseInstruction.deleted_at.is_(None),
            )
            .order_by(NurseInstruction.priority, NurseInstruction.created_at.desc())
            .limit(20)
        )
        return list((await self._session.execute(stmt)).scalars().all())

    # ── Patient ───────────────────────────────────────────────────────────────

    async def patient_upcoming_appointments(self, patient_id: UUID) -> list[Appointment]:
        now = datetime.now(timezone.utc)
        stmt = (
            select(Appointment)
            .where(Appointment.patient_id == patient_id, Appointment.starts_at >= now)
            .order_by(Appointment.starts_at)
            .limit(5)
        )
        return list((await self._session.execute(stmt)).scalars().all())

    async def patient_outstanding_invoices(self, patient_id: UUID) -> list[Invoice]:
        stmt = (
            select(Invoice)
            .where(
                Invoice.patient_id == patient_id,
                Invoice.status.in_(["issued", "draft"]),
            )
            .order_by(Invoice.due_at)
        )
        return list((await self._session.execute(stmt)).scalars().all())
