from typing import TYPE_CHECKING, Type

from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException
from src.tools.inspector import (
    ValidRelationsInspectorBase,
    ValidRelationsException,
)

from .exceptions import Errors

if TYPE_CHECKING:
    from src.core.models import (
        Product,
    )
    from src.tools.errors_base import ErrorsBase


class ValidRelationsInspector(ValidRelationsInspectorBase):
    def __init__(self, session: AsyncSession, **kwargs):
        super().__init__(session=session, **kwargs)

        if "rubric_ids" in kwargs:
            self.need_inspect.append(("rubric_ids", kwargs["rubric_ids"]))
        if "brand_id" in kwargs:
            self.need_inspect.append(("brand_id", kwargs["brand_id"]))

    async def inspect(self):
        while self.need_inspect:
            to_inspect, params = self.need_inspect.pop(0)
            try:
                if to_inspect == "rubric_ids" and params:
                    from ..rubrics.validators import inspecting_rubric_ids
                    await inspecting_rubric_ids(
                        inspector=self,
                        rubric_ids=params,
                    )
                    from ..rubrics.validators import inspecting_rubrics_exist
                    await inspecting_rubrics_exist(
                        inspector=self,
                        rubric_ids=self.result['rubric_ids'],
                    )
                if to_inspect == "brand_id" and params:
                    from ..brands.validators import inspecting_brand_exists
                    await inspecting_brand_exists(
                        inspector=self,
                        brand_id=params
                    )
            except ValidRelationsException:
                return self.error
        return self.result


async def inspecting_product_exists(
        product_id: int,
        inspector: "ValidRelationsInspectorBase",
        errors: Type["ErrorsBase"] = Errors,
):
    # Inspecting if chosen product exists
    try:
        from .repository import ProductsRepository
        repository: ProductsRepository = ProductsRepository(
            session=inspector.session,
        )
        orm_model: "Product" = await repository.get_one_complex(id=product_id, maximized=False)
        inspector.result['product_orm'] = orm_model
    except CustomException as exc:
        inspector.error = ORJSONResponse(
            status_code=exc.status_code,
            content={
                "message": errors.HANDLER_MESSAGE(),
                "detail": exc.msg,
            }
        )
        raise ValidRelationsException
