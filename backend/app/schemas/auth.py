from pydantic import BaseModel
from typing import Literal

UserRole = Literal["patient", "doctor", "nurse", "admin"]

class SignUpRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: UserRole
    phone: str | None = None

class LoginRequest(BaseModel):
    email: str
    password: str

class ProfileOut(BaseModel):
    id: str
    full_name: str
    email: str
    role: UserRole
    public_id: str | None
    phone: str | None
    created_at: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    profile: ProfileOut
