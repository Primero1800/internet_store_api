from typing import Any

from src.tools.errors_base import ErrorsBase


class Errors(ErrorsBase):
    CLASS = "UserTools"
    _CLASS = "user_tools"

    @classmethod
    def already_exists_user_id(cls, user_id: int):
        return "%s of user id=%r already exists" % (cls.CLASS, user_id)
