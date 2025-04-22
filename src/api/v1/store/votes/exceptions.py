class Errors:

    HANDLER_MESSAGE = "Handled by Votes exception handler"

    DATABASE_ERROR = "Error occurred while changing database data"

    NOT_EXISTS = "Vote doesn't exist"

    ALREADY_EXISTS = "Vote already exists"

    @staticmethod
    def already_exists_titled(user_id: int, product_id: int):
        return "Vote user_id=%s and product_id=%s already exists" % (user_id, product_id)
