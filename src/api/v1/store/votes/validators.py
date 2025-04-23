from typing import TYPE_CHECKING

from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException

from .exceptions import Errors
from ..products.repository import ProductsRepository

if TYPE_CHECKING:
    from src.core.models import (
        Product,
    )


class ValidRelationsException(Exception):
    pass


class ValidRelationsInspector:
    def __init__(self, session: AsyncSession, **kwargs):
        self.session = session
        self.need_inspect = []
        self.result = {}
        self.error = None

        if "product_id" in kwargs:
            self.need_inspect.append(("product_id", kwargs["product_id"]))

    async def inspect(self):
        while self.need_inspect:
            to_inspect, params = self.need_inspect.pop(0)
            try:
                if to_inspect == "product_id" and isinstance(params, int):
                    await self.expecting_product_exists(product_id=params)
            except ValidRelationsException:
                return self.error
        return self.result

    async def expecting_product_exists(self, product_id: int):
        # Expecting if chosen brand_id existing
        try:
            product_repository: ProductsRepository = ProductsRepository(
                session=self.session
            )
            product_orm: "Product" = await product_repository.get_one(id=product_id)
            self.result['product_orm'] = product_orm
        except CustomException as exc:
            self.error = ORJSONResponse(
                status_code=exc.status_code,
                content={
                    "message": Errors.HANDLER_MESSAGE,
                    "detail": exc.msg,
                }
            )
            raise ValidRelationsException
