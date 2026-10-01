from app.core.errors import ForbiddenError, ConflictError


class NotAssignedDoctorError(ForbiddenError):
    def __init__(self):
        super().__init__("You are not the assigned doctor for this patient")


class AlreadyAssignedError(ConflictError):
    def __init__(self):
        super().__init__("This nurse is already assigned to this patient")
        self.message = "This nurse is already assigned to this patient"
