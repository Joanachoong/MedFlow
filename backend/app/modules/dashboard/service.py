from __future__ import annotations

from uuid import UUID

from app.core.errors import ForbiddenError
from app.core.permissions import CurrentUser
from app.db.unit_of_work import UnitOfWork
from app.modules.dashboard.repository import DashboardRepository
from app.modules.dashboard.schemas import AdminDashboard, DoctorDashboard, NurseDashboard, PatientDashboard


class DashboardService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._repo = DashboardRepository(uow.session)

    async def get_dashboard(self, actor: CurrentUser, patient_record_id: UUID | None = None):
        if actor.is_admin():
            return await self._admin_dashboard()
        if actor.is_doctor():
            return await self._doctor_dashboard(actor.id)
        if actor.is_nurse():
            return await self._nurse_dashboard(actor.id)
        if actor.is_patient() and patient_record_id:
            return await self._patient_dashboard(patient_record_id)
        raise ForbiddenError("Cannot determine dashboard for this user")

    async def _admin_dashboard(self) -> AdminDashboard:
        return AdminDashboard(
            admitted_now=await self._repo.admitted_now_count(),
            visits_today=await self._repo.visits_today_count(),
            appointments_today=await self._repo.appointments_today_count(),
            active_users_by_role=await self._repo.active_users_by_role(),
            critical_patient_count=await self._repo.critical_patient_count(),
            latest_audit_events=[
                {"id": str(e.id), "action": e.action, "created_at": str(e.created_at)}
                for e in await self._repo.latest_audit_events()
            ],
        )

    async def _doctor_dashboard(self, doctor_id: UUID) -> DoctorDashboard:
        patients = await self._repo.doctor_assigned_patients(doctor_id)
        appts = await self._repo.doctor_todays_appointments(doctor_id)
        notes = await self._repo.doctor_recent_notes(doctor_id)
        return DoctorDashboard(
            assigned_patients=[{"id": str(p.id), "name": p.full_name, "status": p.status} for p in patients],
            todays_appointments=[{"id": str(a.id), "starts_at": str(a.starts_at), "patient_id": str(a.patient_id)} for a in appts],
            recent_notes=[{"id": str(n.id), "patient_id": str(n.patient_id), "created_at": str(n.created_at)} for n in notes],
        )

    async def _nurse_dashboard(self, nurse_id: UUID) -> NurseDashboard:
        patients = await self._repo.nurse_care_team_patients(nurse_id)
        instructions = await self._repo.nurse_new_instructions(nurse_id)
        # Sort critical first
        sorted_patients = sorted(
            patients,
            key=lambda p: {"critical": 0, "monitoring": 1, "stable": 2}.get(p.status, 3)
        )
        return NurseDashboard(
            care_team_patients=[{"id": str(p.id), "name": p.full_name, "status": p.status} for p in sorted_patients],
            new_nurse_instructions=[{"id": str(i.id), "body": i.body, "priority": i.priority} for i in instructions],
        )

    async def _patient_dashboard(self, patient_id: UUID) -> PatientDashboard:
        appts = await self._repo.patient_upcoming_appointments(patient_id)
        invoices = await self._repo.patient_outstanding_invoices(patient_id)
        return PatientDashboard(
            upcoming_appointments=[{"id": str(a.id), "starts_at": str(a.starts_at)} for a in appts],
            outstanding_invoices=[{"id": str(i.id), "total": float(i.total), "status": i.status} for i in invoices],
            has_record_access=True,  # checked separately via clinical service
        )
