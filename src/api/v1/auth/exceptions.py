class Errors:

    HANDLER_MESSAGE = "Handled by Auth exception handler"

    DATABASE_ERROR = "Error occurred while changing database data"

    USER_NOT_EXISTS = "User doesn't exist"

    @staticmethod
    def user_not_exists_mailed(email: str):
        return f"Email {email!r} isn't bound to any user"

    BAD_CREDENTIALS_OR_NOT_ACTIVE = "Bad credentials or user is not active"

    USER_NOT_VERIFIED = "User is not verified"

    @staticmethod
    def user_not_verified_emailed(email: str):
        return f"User {email!r} is not verified"

    USER_ALREADY_EXISTS = "User already exists"

    @staticmethod
    def user_already_exists_emailed(email: str):
        return f"User {email!r} already exists"

    INVALID_PASSWORD = "Invalid password"

    @staticmethod
    def invalid_password_reasoned(reason: str):
        return f"Invalid password: {reason}"

    INACTIVE_USER = "User is inactive"

    @staticmethod
    def inactive_user_emailed(email: str):
        return f"User {email!r} is inactive"

    VERIFY_USER_ALREADY_VERIFIED = "User is already verified"

    @staticmethod
    def verify_user_already_verified_emailed(email: str):
        return f"User {email!r} is already verified"

    VERIFY_USER_BAD_TOKEN = "Invalid token"

    INVALID_RESET_PASSWORD_TOKEN = "Invalid reset password token"



