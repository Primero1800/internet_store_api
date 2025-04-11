from typing import Any


class Errors:

    HANDLER_MESSAGE = "Handled by Sessions exception handler"

    SESSION_EXISTS = "Session already exists, Can't overwrite existing session."

    @staticmethod
    def session_exists_mailed(email: str):
        return f"Session already exists for {email!r}. Can't overwrite existing session."

    READ_EXISTING_SESSION_ERROR = "Can't read existing session"

    @staticmethod
    def read_existing_session_error_id(session_id: Any):
        return f"Can't read existing session: id={session_id!r}"

    DATABASE_ERROR = "Error occurred while changing database data"
