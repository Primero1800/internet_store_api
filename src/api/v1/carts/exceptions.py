CLASS = "Cart"
_CLASS = "cart"

class Errors:

    HANDLER_MESSAGE = f"Handled by {CLASS}s exception handler"

    DATABASE_ERROR = "Error occurred while changing database data"

    NOT_EXISTS = f"{CLASS} doesn't exist"

    ALREADY_EXISTS = f"{CLASS} already exists"

    NO_RIGHTS = "You are not authorized for this operation"

    @staticmethod
    def already_exists_id(user_id: int):
        return f"{CLASS} with user_id={user_id} already exists"
