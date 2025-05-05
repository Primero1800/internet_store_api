class ErrorsBase:
    CLASS = "Object"
    _CLASS = "object"

    @classmethod
    def HANDLER_MESSAGE(cls):
        return f"Handled by {cls.CLASS}s exception handler"

    @classmethod
    def DATABASE_ERROR(cls):
        return "Error occurred while changing database data"

    @classmethod
    def NOT_EXISTS(cls):
        return f"{cls.CLASS} doesn't exist"

    @classmethod
    def ALREADY_EXISTS(cls):
        return f"{cls.CLASS} already exists"

    @classmethod
    def NO_RIGHTS(cls):
        return "You are not authorized for this operation"
