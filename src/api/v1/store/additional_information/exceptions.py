from typing import Any

CLASS = "Additional Information"


class Errors:

    HANDLER_MESSAGE = f"Handled by {CLASS} exception handler"

    DATABASE_ERROR = "Error occurred while changing database data"

    NOT_EXISTS = f"{CLASS} of product doesn't exist"

    ALREADY_EXISTS = f"{CLASS} of product already exists"

    @staticmethod
    def already_exists_product_id(product_id: int):
        return "%s of product id=%r already exists" % (CLASS, product_id)

    @staticmethod
    def integrity_error_detailed(exc: Any):
        return f"{Errors.DATABASE_ERROR}: {exc!r}"
