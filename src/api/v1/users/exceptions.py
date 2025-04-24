from src.tools.exceptions import CustomException

CLASS = "User"

class Errors:

    HANDLER_MESSAGE = f"Handled by {CLASS}s exception handler"

    DATABASE_ERROR = "Error occurred while changing database data"

    NOT_FOUND = f"{CLASS} not found"

    @staticmethod
    def user_not_found_id(id: int):
        return f"{CLASS} with id={id} not found"


class NoSessionException(CustomException):
    pass
