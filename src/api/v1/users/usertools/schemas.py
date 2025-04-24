from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, computed_field

from src.tools.usertools_content import ToolsContent

if TYPE_CHECKING:
    from src.api.v1.store.products.schemas import (
        ProductShort,
    )


class BaseUserTools(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int


class UserToolsShort(BaseUserTools):
    recently_viewed: list[ToolsContent]
    wishlist: list[ToolsContent]
    comparison: list[ToolsContent]

    @computed_field
    @property
    def count_rv(self) -> int | None:
        if hasattr(self, 'recently_viewed') and isinstance(self.recently_viewed, list):
            return len(self.recently_viewed)
        return None

    @computed_field
    @property
    def count_c(self) -> int | None:
        if hasattr(self, 'comparison') and isinstance(self.comparison, list):
            return len(self.comparison)
        return None

    @computed_field
    @property
    def count_w(self) -> int | None:
        if hasattr(self, 'wishlist') and isinstance(self.wishlist, list):
            return len(self.wishlist)
        return None


class UserToolsRead(UserToolsShort):
    recently_viewed: list["ProductShort"]
    wishlist: list["ProductShort"]
    comparison: list["ProductShort"]


class UserToolsCreate(BaseUserTools):
    pass


class UserToolsUpdate(BaseUserTools):
    pass
