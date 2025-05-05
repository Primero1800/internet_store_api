from src.tools.errors_base import ErrorsBase


class Errors(ErrorsBase):
    CLASS = "Vote"
    _CLASS = "vote"

    @classmethod
    def already_exists_titled(cls, user_id: int, product_id: int):
        return "%s user_id=%s and product_id=%s already exists" % (cls.CLASS, user_id, product_id)
