from src.tools.errors_base import ErrorsBase


class Errors(ErrorsBase):

    CLASS = "Person"
    _CLASS = "person"

    @classmethod
    def already_exists_id(cls, user_id: int):
        return "%s with user_id=%s already exists" % (cls.CLASS, user_id)
