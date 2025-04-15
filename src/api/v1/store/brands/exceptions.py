class Errors:

    HANDLER_MESSAGE = "Handled by Brands exception handler"

    DATABASE_ERROR = "Error occurred while changing database data"

    NOT_EXISTS = "Brand doesn't exist"

    ALREADY_EXISTS = "Brand already exists"

    @staticmethod
    def already_exists_titled(title: str):
        return "Brand %r already exists" % title

    IMAGE_SAVING_ERROR = "Error occurred while saving image"
