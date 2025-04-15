class Errors:

    HANDLER_MESSAGE = "Handled by Rubrics exception handler"

    DATABASE_ERROR = "Error occurred while changing database data"

    BRAND_NOT_EXISTS = "Rubric doesn't exist"

    BRAND_ALREADY_EXISTS = "Rubric already exists"

    @staticmethod
    def rubric_already_exists_titled(title: str):
        return "Rubric %r already exists" % title

    IMAGE_SAVING_ERROR = "Error occurred while saving image"
