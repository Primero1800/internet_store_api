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

    SETTING_NOT_EXISTING_SESSION = "User have no session yet"

    @staticmethod
    def setting_not_existing_session_emailed(email: str):
        return f"User {email!r} have no existing session yet"

    UPDATING_NOT_EXISTS_SESSION = "Session doesn't exist. Can't update session."

    DATABASE_ERROR = "Error occurred while changing database data"
