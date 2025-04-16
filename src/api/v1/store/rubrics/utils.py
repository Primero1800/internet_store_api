from typing import TYPE_CHECKING

from .schemas import RubricRead, RubricShort

if TYPE_CHECKING:
    from src.core.models import Rubric


async def get_schema_from_orm(
    orm_model: "Rubric",
    maximized: bool = False,
) -> RubricRead:

    # BRUTE FORCE VARIANT

    short_schema: RubricShort = await get_short_schema_from_orm(orm_model=orm_model)

    products_shorts = []
    from ..products.utils import get_short_schema_from_orm as get_short_product_schema_from_orm
    for product in orm_model.products:
        products_shorts.append(await get_short_product_schema_from_orm(product))

    return RubricRead(
        **short_schema.model_dump(),
        description=orm_model.description,
        products=products_shorts
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
