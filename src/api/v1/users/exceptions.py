from src.tools.exceptions import CustomException


class Errors:

    HANDLER_MESSAGE = "Handled by Users exception handler"

    DATABASE_ERROR = "Error occurred while changing database data"


class NoSessionException(CustomException):
    pass
