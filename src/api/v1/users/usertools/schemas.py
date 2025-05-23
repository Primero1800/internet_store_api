from typing import Any

from pydantic import BaseModel, ConfigDict, computed_field

from src.tools.usertools_content import ToolsContent


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
    user: Any


class UserToolsCreate(BaseUserTools):
    recently_viewed: dict = {}
    wishlist: dict = {}
    comparison: dict = {}


class UserToolsUpdate(UserToolsCreate):
    pass
