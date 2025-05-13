from typing import TYPE_CHECKING, Union
from fastapi import status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.exceptions import CustomException
from .schemas import ProductRead, ProductShort

if TYPE_CHECKING:
    from src.core.models import Product


async def get_schema_from_orm(
        orm_model: "Product",
        maximized: bool = True,
        relations: list | None = None,
):

    # BRUTE FORCE VARIANT

    if maximized or (relations and "add_info" in relations):
        from ..additional_information.utils import get_short_schema_from_orm as get_short_add_info_schema_from_orm
        if relations and "add_info" in relations:
            if not orm_model.add_info:
                return None
            return await get_short_add_info_schema_from_orm(orm_model.add_info)

    if maximized or (relations and "sale_info" in relations):
        from ..sale_information.utils import get_short_schema_from_orm as get_short_sale_info_schema_from_orm
        if relations and "sale_info" in relations:
            if not orm_model.sale_info:
                return None
            return await get_short_sale_info_schema_from_orm(orm_model.sale_info)

    if maximized or (relations and "votes" in relations):
        vote_shorts = []
        from ..votes.utils import get_short_schema_from_orm as get_short_vote_schema_from_orm
        for vote in orm_model.votes:
            vote_shorts.append(await get_short_vote_schema_from_orm(vote))
        if relations and "votes" in relations:
            return sorted(vote_shorts, key=lambda x: x.id)

    if maximized or (relations and "posts" in relations):
        post_shorts = []
        from ...posts.post.utils import get_short_schema_from_orm as get_short_post_schema_from_orm
        for post in orm_model.posts:
            post_shorts.append(await get_short_post_schema_from_orm(post))
        if relations and "posts" in relations:
            return sorted(post_shorts, key=lambda x: x.id)

    rubrics_shorts = []
    from ..rubrics.utils import get_short_schema_from_orm as get_short_rubric_schema_from_orm
    for rubric in orm_model.rubrics:
        rubrics_shorts.append(await get_short_rubric_schema_from_orm(rubric))

    from ..brands.utils import get_short_schema_from_orm as get_short_brand_schema_from_orm
    brand_short = await get_short_brand_schema_from_orm(orm_model.brand)

    images = [image.file for image in orm_model.images]

    return ProductRead(
        **orm_model.to_dict(),

        rubrics=sorted(rubrics_shorts, key=lambda x: x.id),
        brand=brand_short,
        image_file=await get_main_image_file(orm_model),
        images=images,
    )


async def get_short_schema_from_orm(
    orm_model: Union["Product", dict]
) -> ProductShort | None:

    # BRUTE FORCE VARIANT
    if not orm_model:
        return None

    if isinstance(orm_model, dict):     # inspecting if user is session dictionary
        dict_to_push = orm_model
        image_file = orm_model.pop('image_file')
    else:
        dict_to_push = orm_model.to_dict()
        image_file = await get_main_image_file(orm_model)

    return ProductShort(
        **dict_to_push,
        image_file=image_file
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


async def change_quantity(
        id: int,
        reserved_quantity: int,
        session: AsyncSession,
):
    from .service import ProductsService
    service: ProductsService = ProductsService(
        session=session,
    )
    orm_model: "Product" = await service.get_one(
        id=id,
        to_schema=False
    )
    if isinstance(orm_model, ORJSONResponse):
        return orm_model

    new_quantity = orm_model.quantity - reserved_quantity
    result = await service.edit_one(
        orm_model=orm_model,
        quantity=new_quantity,
        return_none=True,
        is_partial=True,
    )
    if isinstance(result, ORJSONResponse):
        return result
