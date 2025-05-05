from src.tools.errors_base import ErrorsBase


class Errors(ErrorsBase):

    CLASS = "Product"
    _CLASS = "product"

    @classmethod
    def already_exists_titled(cls, title: str):
        return "%s %r already exists" % (cls.CLASS, title)
