from src.tools.exceptions import CustomException
from src.tools.errors_base import ErrorsBase


class Errors(ErrorsBase):
    CLASS = "User"
    _CLASS = "user"

    @classmethod
    def user_not_found_id(cls, id: int):
        return f"{cls.CLASS} with id={id} not found"

    @classmethod
    def already_exists_email(cls, email: str):
        return f"{cls.CLASS} with email={email} already exists"


class NoSessionException(CustomException):
    pass
