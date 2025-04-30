CLASS = "Cart"
_CLASS = "cart"

class Errors:

    HANDLER_MESSAGE = f"Handled by {CLASS}s exception handler"

    DATABASE_ERROR = "Error occurred while changing database data"

    NOT_EXISTS = f"{CLASS} doesn't exist"

    ALREADY_EXISTS = f"{CLASS} already exists"

    NO_RIGHTS = "You are not authorized for this operation"

    @staticmethod
    def already_exists_id(user_id: int):
        return f"{CLASS} with user_id={user_id} already exists"

    @staticmethod
    def item_already_exists_id(cart_id: int, product_id: int):
        return f"{CLASS}Item with cart_id={cart_id}  and product_id={product_id} already exists"

    @staticmethod
    def item_not_exists_id(cart_id: int, product_id: int):
        return f"Product with id={product_id} doesn't exists in {CLASS} with user_id={cart_id}"
