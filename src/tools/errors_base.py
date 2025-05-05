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

    @staticmethod
    def USER_NOT_VERIFIED():
        return "User is not verified"

    @staticmethod
    def BAD_CREDENTIALS_OR_NOT_ACTIVE():
        return "Bad credentials or user is not active"

    @staticmethod
    def INVALID_PASSWORD():
        return "Invalid password"

    @staticmethod
    def INACTIVE_USER():
        return "User is inactive"

    @staticmethod
    def INVALID_TOKEN():
        return "Invalid token"

    @staticmethod
    def INVALID_SESSION():
        return "Invalid session"
