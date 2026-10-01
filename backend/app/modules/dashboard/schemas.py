from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


# ── Patient dashboard ──────────────────────────────────────────────────────────

class PatientDashboard(BaseModel):
    upcoming_appointments: list[dict]
    outstanding_invoices: list[dict]
    has_record_access: bool


# ── Doctor dashboard ───────────────────────────────────────────────────────────

class DoctorDashboard(BaseModel):
    assigned_patients: list[dict]
    todays_appointments: list[dict]
    recent_notes: list[dict]


# ── Nurse dashboard ────────────────────────────────────────────────────────────

class NurseDashboard(BaseModel):
    care_team_patients: list[dict]   # ordered critical first
    new_nurse_instructions: list[dict]


# ── Admin dashboard ────────────────────────────────────────────────────────────

class AdminDashboard(BaseModel):
    admitted_now: int
    visits_today: int
    appointments_today: int
    active_users_by_role: dict[str, int]
    critical_patient_count: int
    latest_audit_events: list[dict]
