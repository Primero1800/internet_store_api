from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.inspector import (
    ValidRelationsInspectorBase,
    ValidRelationsException,
)


class ValidRelationsInspector(ValidRelationsInspectorBase):
    def __init__(self, session: AsyncSession, **kwargs):
        super().__init__(session=session, **kwargs)

        if "user_id" in kwargs:
            self.need_inspect.append(("user_id", kwargs['user_id']))

    async def inspect(self):
        while self.need_inspect:
            to_inspect, params = self.need_inspect.pop(0)
            try:
                if to_inspect == "user_id" and isinstance(params, int):
                    from ...users.user.validators import inspecting_user_exists
                    await inspecting_user_exists(
                        inspector=self,
                        user_id=params,
                    )
            except ValidRelationsException:
                return self.error
        return self.result
