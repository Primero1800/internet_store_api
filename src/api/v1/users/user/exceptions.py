from src.tools.exceptions import CustomException
from src.tools.errors_base import ErrorsBase


class Errors(ErrorsBase):
    CLASS = "User"
    _CLASS = "user"

    @classmethod
    def user_not_found_id(cls, id: int):
        return f"{cls.CLASS} with id={id} not found"


class NoSessionException(CustomException):
    pass
