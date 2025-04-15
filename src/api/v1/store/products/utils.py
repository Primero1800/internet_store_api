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

    rubrics = []
    for rubric in orm_model.rubrics:
        image_file = rubric.image.file if rubric.image else ''
        rubric: RubricShort = RubricShort(**rubric.to_dict(), image_file=image_file)
        rubrics.append(rubric)

    brand_image_file = orm_model.brand.image.file if orm_model.brand.image else ''
    brand: BrandShort = BrandShort(
        **orm_model.brand.to_dict(),
        image_file=brand_image_file,
    )

    images = [image.file for image in orm_model.images]

    return ProductRead(
        **short_schema.model_dump(),
        description=orm_model.description,
        rubrics=rubrics,
        brand=brand,
        images=images,
    )


async def get_short_schema_from_orm(
    orm_model: "Product"
) -> ProductShort:
    image_file = orm_model.images[0].file if orm_model.images and hasattr(orm_model.images[0], "file") else ''

    # BRUTE FORCE VARIANT
    return ProductShort(
        **orm_model.to_dict(),
        image_file=image_file,
    )


async def temporary_fragment(ids: str):
    try:
        return [int(el.strip()) for el in ids.split(',')] if ids else []
    except ValueError:
        raise CustomException(
            status_code=status.HTTP_400_BAD_REQUEST,
            msg="Parameter 'rubric_ids' must contains only integers, differed by comma"
        )
