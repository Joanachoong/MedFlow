from fastapi import APIRouter

from app.modules.audit.router import router as audit_router
from app.modules.billing.router import router as billing_router
from app.modules.care_team.router import router as care_team_router
from app.modules.clinical.router import router as clinical_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.encounters.router import router as encounters_router
from app.modules.identity.router import router as identity_router
from app.modules.patients.router import router as patients_router
from app.modules.scheduling.router import router as scheduling_router

# Auth router (existing, kept intact)
from app.login.auth import router as auth_router

api_router = APIRouter()

# Auth (pre-existing)
api_router.include_router(auth_router)

# Modular monolith feature modules
api_router.include_router(identity_router)
api_router.include_router(patients_router)
api_router.include_router(care_team_router)
api_router.include_router(clinical_router)
api_router.include_router(scheduling_router)
api_router.include_router(encounters_router)
api_router.include_router(billing_router)
api_router.include_router(audit_router)
api_router.include_router(dashboard_router)
