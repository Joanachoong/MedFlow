from app.core.errors import ForbiddenError, NotFoundError


class ProfileNotFoundError(NotFoundError):
    def __init__(self, profile_id: str):
        super().__init__("Profile", profile_id)


class CannotDeactivateSelfError(ForbiddenError):
    def __init__(self):
        super().__init__("You cannot deactivate your own account")
