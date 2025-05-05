from typing import Any

from src.tools.errors_base import ErrorsBase


class Errors(ErrorsBase):

    CLASS = "Session"
    _CLASS = "session"

    @classmethod
    def COOKIE_NO_SESSION(cls):
        return f"No {cls.CLASS} cookie attached to request"

    @classmethod
    def COOKIE_SESSION_INVALID_SIGNATURE(cls):
        return f"{cls.CLASS} cookie has invalid signature"

    @classmethod
    def SESSION_EXISTS(cls):
        return f"{cls.CLASS} already exists, Can't overwrite existing {cls._CLASS}."

    @staticmethod
    def session_exists_mailed(email: str):
        return f"Session already exists for {email!r}. Can't overwrite existing session."

    @classmethod
    def READ_EXISTING_SESSION_ERROR(cls):
        return f"Can't read existing {cls._CLASS}"

    @classmethod
    def read_existing_session_error_id(cls, session_id: Any):
        return f"Can't read existing {cls._CLASS}: id={session_id!r}"

    @classmethod
    def SETTING_NOT_EXISTING_SESSION(cls):
        return f"User have no {cls._CLASS} yet"

    @classmethod
    def setting_not_existing_session_emailed(cls, email: str):
        return f"User {email!r} have no existing {cls._CLASS} yet"

    @classmethod
    def UPDATING_NOT_EXISTS_SESSION(cls):
        return f"{cls.CLASS} doesn't exist. Can't update or clear {cls._CLASS}."
