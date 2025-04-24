from typing import TYPE_CHECKING


from ...store.products.utils import get_short_schema_from_orm as get_short_product_schema_from_orm

from .schemas import (
    UserToolsShort,
    UserToolsRead,
)

if TYPE_CHECKING:
    from src.core.models import (
        UserTools,
    )


CLASS = "UserTools"


async def get_short_schema_from_orm(
    orm_model: "UserTools"
) -> UserToolsShort:

    # BRUTE FORCE VARIANT
    return UserToolsShort(
        **orm_model.to_dict(),
    )