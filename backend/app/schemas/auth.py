"""
Auth schemas for the existing login/auth.py module.
"""
from __future__ import annotations

from pydantic import BaseModel, EmailStr


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "patient"
    phone: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProfileOut(BaseModel):
    id: str
    full_name: str
    email: str
    role: str
    public_id: str | None = None
    phone: str | None = None
    created_at: str


class AuthResponse(BaseModel):
    access_token: str
    profile: ProfileOut
