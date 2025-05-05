from src.tools.errors_base import ErrorsBase


class Errors(ErrorsBase):
    CLASS = "Rubric"
    _CLASS = "rubric"

    @classmethod
    def already_exists_titled(cls, title: str):
        return "%s %r already exists" % (cls.CLASS, title)
