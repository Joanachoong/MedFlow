from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


# ── Base ─────────────────────────────────────────────────────────────────────


class MedFlowError(Exception):
    """Root exception for all domain and infrastructure errors."""

    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str = "An unexpected error occurred"):
        self.message = message
        super().__init__(message)


# ── 4xx ──────────────────────────────────────────────────────────────────────


class UnauthorizedError(MedFlowError):
    status_code = 401
    code = "unauthorized"

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message)


class ForbiddenError(MedFlowError):
    status_code = 403
    code = "forbidden"

    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(message)


class InactiveAccountError(ForbiddenError):
    code = "account_inactive"

    def __init__(self) -> None:
        super().__init__("This account has been deactivated")


class NotFoundError(MedFlowError):
    status_code = 404
    code = "not_found"

    def __init__(self, resource: str = "Resource", id: str | None = None):
        msg = f"{resource} not found" if not id else f"{resource} '{id}' not found"
        super().__init__(msg)


class ConflictError(MedFlowError):
    status_code = 409
    code = "conflict"


class DomainValidationError(MedFlowError):
    status_code = 422
    code = "validation_error"


# ── Handlers ─────────────────────────────────────────────────────────────────


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(MedFlowError)
    async def medflow_handler(request: Request, exc: MedFlowError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.code, "message": exc.message},
        )

    @app.exception_handler(Exception)
    async def generic_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"error": "internal_error", "message": "An unexpected error occurred"},
        )
