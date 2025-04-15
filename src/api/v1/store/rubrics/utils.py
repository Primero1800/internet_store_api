from typing import TYPE_CHECKING

from .schemas import RubricRead, RubricShort
from ..products.schemas import ProductShort

if TYPE_CHECKING:
    from src.core.models import Rubric


async def get_schema_from_orm(
    orm_model: "Rubric",
    maximized: bool = False,
) -> RubricRead:

    # BRUTE FORCE VARIANT

    short_schema: RubricShort = await get_short_schema_from_orm(orm_model=orm_model)

    products = []
    for product in orm_model.products:
        image_file = product.images[0].file if product.images else ''
        product: ProductShort = ProductShort(**product.to_dict(), image_file=image_file)
        products.append(product)

    return RubricRead(
        **short_schema.model_dump(),
        description=orm_model.description,
        products=products
    )


async def get_short_schema_from_orm(
    orm_model: "Rubric"
) -> RubricShort:
    image_file = orm_model.image.file if hasattr(orm_model.image, "file") else ''

    # BRUTE FORCE VARIANT
    return RubricShort(
        **orm_model.to_dict(),
        image_file=image_file,
    )
