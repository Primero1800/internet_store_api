class Errors:

    HANDLER_MESSAGE = "Handled by Products exception handler"

    DATABASE_ERROR = "Error occurred while changing database data"

    NOT_EXISTS = "Product doesn't exist"

    ALREADY_EXISTS = "Product already exists"

    @staticmethod
    def already_exists_titled(title: str):
        return "Product %r already exists" % title

    IMAGE_SAVING_ERROR = "Error occurred while saving image"
