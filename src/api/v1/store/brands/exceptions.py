class Errors:

    HANDLER_MESSAGE = "Handled by Brands exception handler"

    DATABASE_ERROR = "Error occurred while changing database data"

    BRAND_NOT_EXISTS = "Brand doesn't exist"

    BRAND_ALREADY_EXISTS = "Brand already exists"

    @staticmethod
    def brand_already_exists_titled(title: str):
        return "Brand %r already exists" % title

    IMAGE_SAVING_ERROR = "Error occurred while saving image"
