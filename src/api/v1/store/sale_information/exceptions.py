from typing import Any

from src.tools.errors_base import ErrorsBase


class Errors(ErrorsBase):
    CLASS = "Sale Information"
    _CLASS = "SaleInfo"

    @classmethod
    def already_exists_product_id(cls, product_id: int):
        return "%s of product id=%r already exists" % (cls.CLASS, product_id)
