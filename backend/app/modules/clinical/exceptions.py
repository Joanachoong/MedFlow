from app.core.errors import ForbiddenError


class NoActiveGrantError(ForbiddenError):
    def __init__(self):
        super().__init__("No active record access grant for this patient")


class NotCareTeamMemberError(ForbiddenError):
    def __init__(self):
        super().__init__("You are not on the care team for this patient")
