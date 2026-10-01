from app.core.errors import NotFoundError


class PatientNotFoundError(NotFoundError):
    def __init__(self, patient_id: str):
        super().__init__("Patient", patient_id)
