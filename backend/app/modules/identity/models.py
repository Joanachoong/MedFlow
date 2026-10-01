from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, SoftDeleteMixin, TimestampMixin


class Profile(Base, TimestampMixin, SoftDeleteMixin):
    """
    Mirrors the `profiles` table.
    One row per Supabase auth.users entry.
    Supabase triggers set public_id automatically via a DB trigger.
    """

    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, comment="FK → auth.users.id"
    )
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    role: Mapped[str] = mapped_column(
        SAEnum(
            "patient", "doctor", "nurse", "admin",
            name="user_role",
            create_type=False,   # type already exists in the DB
        ),
        nullable=False,
    )
    public_id: Mapped[str | None] = mapped_column(
        String, unique=True, nullable=True,
        comment="D-0001, N-0001, A-0001. NULL for patient accounts"
    )
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
