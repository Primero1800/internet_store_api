from typing import TYPE_CHECKING
from fastapi import status

from src.tools.exceptions import CustomException
from .schemas import ProductRead, ProductShort
from ..brands.schemas import BrandShort
from ..rubrics.schemas import RubricShort

if TYPE_CHECKING:
    from src.core.models import Product


async def get_schema_from_orm(
    orm_model: "Product",
    maximized: bool = False,
) -> ProductRead:

    # BRUTE FORCE VARIANT

    short_schema: ProductShort = await get_short_schema_from_orm(orm_model=orm_model)

    rubrics_shorts = []
    from ..rubrics.utils import get_short_schema_from_orm as get_short_rubric_schema_from_orm
    for rubric in orm_model.rubrics:
        rubrics_shorts.append(await get_short_rubric_schema_from_orm(rubric))

    from ..brands.utils import get_short_schema_from_orm as get_short_brand_schema_from_orm
    brand_short = await get_short_brand_schema_from_orm(orm_model.brand)

    images = [image.file for image in orm_model.images]

    return ProductRead(
        **orm_model.to_dict(),

        rubrics=rubrics_shorts,
        brand=brand_short,
        image_file=await get_main_image_file(orm_model),
        images=images,
    )


async def get_short_schema_from_orm(
    orm_model: "Product"
) -> ProductShort:

    # BRUTE FORCE VARIANT
    return ProductShort(
        **orm_model.to_dict(),
        image_file=await get_main_image_file(orm_model),
    )


async def get_main_image_file(orm_model: "Product"):
    return orm_model.images[0].file if orm_model.images and hasattr(orm_model.images[0], "file") else ''


async def temporary_fragment(ids: str | list):
    try:
        if isinstance(ids, list) and ids:
            ids = ids[0]
        if isinstance(ids, str):
            ids = ids.split(',')
        return set([int(el.strip()) for el in ids] if ids else [])
    except ValueError:
        raise CustomException(
            status_code=status.HTTP_400_BAD_REQUEST,
            msg="Parameter 'rubric_ids' must contains only valid integers"
        )
