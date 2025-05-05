from typing import Any
from src.tools.errors_base import ErrorsBase


class Errors(ErrorsBase):
    CLASS = "Additional Information"
    _CLASS = "add_info"

    @classmethod
    def already_exists_product_id(cls, product_id: int):
        return "%s of product id=%r already exists" % (cls.CLASS, product_id)

    @classmethod
    def integrity_error_detailed(cls, exc: Any):
        return f"{cls.DATABASE_ERROR()}: {exc!r}"
