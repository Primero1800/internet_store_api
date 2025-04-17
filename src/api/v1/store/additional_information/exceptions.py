from typing import Any


class Errors:

    HANDLER_MESSAGE = "Handled by Additional Information exception handler"

    DATABASE_ERROR = "Error occurred while changing database data"

    NOT_EXISTS = "Additional Information of product doesn't exist"

    ALREADY_EXISTS = "Additional Information of product already exists"

    @staticmethod
    def already_exists_product_id(product_id: int):
        return "Additional information of product id=%r already exists" % product_id

    @staticmethod
    def integrity_error_detailed(exc: Any):
        return f"{Errors.DATABASE_ERROR}: {exc!r}"
