from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum as SAEnum, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, SoftDeleteMixin


class Patient(Base, TimestampMixin, SoftDeleteMixin):
    """Mirrors the `patients` table."""

    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    public_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, comment="P-0001")
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), unique=True, nullable=True,
        comment="NULL until the patient gets a portal login"
    )
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    blood_type: Mapped[str | None] = mapped_column(String, nullable=True)
    allergies: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum("stable", "monitoring", "critical", name="patient_status", create_type=False),
        default="stable",
        nullable=False,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), nullable=False, comment="Doctor who registered the patient"
    )
