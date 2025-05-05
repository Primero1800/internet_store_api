from src.tools.errors_base import ErrorsBase


class Errors(ErrorsBase):
    CLASS = "Cart"
    _CLASS = "cart"

    @classmethod
    def already_exists_id(cls, user_id: int):
        return f"{cls.CLASS} with user_id={user_id} already exists"

    @classmethod
    def item_already_exists_id(cls, cart_id: int, product_id: int):
        return f"{cls.CLASS}Item with cart_id={cart_id}  and product_id={product_id} already exists"

    @classmethod
    def item_not_exists_id(cls, cart_id: int | None, product_id: int):
        return f"Product with id={product_id} doesn't exists in {cls.CLASS} with user_id={cart_id}"
