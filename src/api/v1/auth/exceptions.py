from src.tools.errors_base import ErrorsBase


class Errors(ErrorsBase):

    CLASS = "User"
    _CLASS = "auth"

    @classmethod
    def HANDLER_MESSAGE(cls):
        return f"Handled by Auth exception handler"

    @staticmethod
    def user_not_exists_mailed(email: str):
        return f"Email {email!r} isn't bound to any user"

    @staticmethod
    def user_not_verified_emailed(email: str):
        return f"User {email!r} is not verified"

    USER_ALREADY_EXISTS = "User already exists"

    @staticmethod
    def user_already_exists_emailed(email: str):
        return f"User {email!r} already exists"

    @staticmethod
    def invalid_password_reasoned(reason: str):
        return f"Invalid password: {reason}"

    @staticmethod
    def inactive_user_emailed(email: str):
        return f"User {email!r} is inactive"

    @staticmethod
    def VERIFY_USER_ALREADY_VERIFIED():
        return "User is already verified"

    @staticmethod
    def verify_user_already_verified_emailed(email: str):
        return f"User {email!r} is already verified"

    @staticmethod
    def invalid_token(token_type: str):
        return f"Invalid {token_type} token"

    @staticmethod
    def INVALID_RESET_PASSWORD_TOKEN():
        return "Invalid reset password token"
