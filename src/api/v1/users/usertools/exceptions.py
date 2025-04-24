from typing import Any

CLASS = "User Tools"


class Errors:

    HANDLER_MESSAGE = f"Handled by {CLASS} exception handler"

    DATABASE_ERROR = "Error occurred while changing database data"

    NOT_EXISTS = f"{CLASS} of user doesn't exist"

    ALREADY_EXISTS = f"{CLASS} of user already exists"

    @staticmethod
    def already_exists_user_id(user_id: int):
        return "%s of user id=%r already exists" % (CLASS, user_id)

    @staticmethod
    def integrity_error_detailed(exc: Any):
        return f"{Errors.DATABASE_ERROR}: {exc!r}"
