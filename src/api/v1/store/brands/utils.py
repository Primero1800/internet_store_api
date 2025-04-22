from typing import TYPE_CHECKING

from .schemas import BrandRead, BrandShort

if TYPE_CHECKING:
    from src.core.models import Brand


async def get_schema_from_orm(
        orm_model: "Brand",
        maximized: bool = True,
        relations: list | None = [],
):

    # BRUTE FORCE VARIANT

    short_schema: BrandShort = await get_short_schema_from_orm(orm_model=orm_model)

    products_shorts = []
    if maximized or 'products' in relations:
        from ..products.utils import get_short_schema_from_orm as get_short_product_schema_from_orm
        for product in orm_model.products:
            products_shorts.append(await get_short_product_schema_from_orm(product))
    if 'products' in relations:
        return sorted(products_shorts, key= lambda x: x.id)

    return BrandRead(
        **short_schema.model_dump(),
        description=orm_model.description,
        products=products_shorts
    )


async def get_short_schema_from_orm(
    orm_model: "Brand"
) -> BrandShort:
    image_file = orm_model.image.file if hasattr(orm_model.image, "file") else ''

    # BRUTE FORCE VARIANT
    return BrandShort(
        **orm_model.to_dict(),
        image_file=image_file,
    )