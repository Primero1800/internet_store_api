class Errors:

    HANDLER_MESSAGE = "Handled by Rubrics exception handler"

    DATABASE_ERROR = "Error occurred while changing database data"

    NOT_EXISTS = "Rubric doesn't exist"

    ALREADY_EXISTS = "Rubric already exists"

    @staticmethod
    def already_exists_titled(title: str):
        return "Rubric %r already exists" % title

    IMAGE_SAVING_ERROR = "Error occurred while saving image"
