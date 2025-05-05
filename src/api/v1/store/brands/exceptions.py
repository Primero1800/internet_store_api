from src.tools.errors_base import ErrorsBase

class Errors(ErrorsBase):
    CLASS = "Brand"
    _CLASS = "brand"

    @classmethod
    def already_exists_titled(cls, title: str):
        return "%s %r already exists" % (cls.CLASS, title)
