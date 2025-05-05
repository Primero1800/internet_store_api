import logging
from fastapi import status
from typing import Sequence, TYPE_CHECKING, Union

from sqlalchemy import select, Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.models import UserTools
from src.tools.exceptions import CustomException
from .exceptions import Errors

if TYPE_CHECKING:
    from src.tools.usertools_content import ToolsContent
    from .filters import (
        UserToolsFilter,
    )
    from .schemas import (
        UserToolsCreate,
        UserToolsUpdate,
    )

CLASS = "UserTools"


class UserToolsRepository:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_one(
            self,
            user_id: int
    ):
        orm_model = await self.session.get(UserTools, user_id)
        if not orm_model:
            text_error = f"user_id={user_id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

    async def get_one_complex(
            self,
            user_id: int = None,
            maximized: bool = True,
            relations: list = []
    ):
        stmt = select(UserTools).where(UserTools.user_id == user_id)
        if maximized or "user" in relations:
            stmt = stmt.options(
                joinedload(UserTools.user),
            )
        result: Result = await self.session.execute(stmt)
        orm_model: UserTools | None = result.unique().scalar_one_or_none()

        if not orm_model:
            text_error = f"user_id={user_id}"
            raise CustomException(
                msg=f"{CLASS} with {text_error} not found"
            )
        return orm_model

    async def get_all(
            self,
            filter_model: "UserToolsFilter",
    ) -> Sequence:

        query_filter = filter_model.filter(select(UserTools))
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.order_by(UserTools.user_id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_all_full(
            self,
            filter_model: "UserToolsFilter",
    ) -> Sequence:

        query_filter = filter_model.filter(select(UserTools))
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.options(
            joinedload(UserTools.user)
        ).order_by(UserTools.user_id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_orm_model_from_schema(
            self,
            instance: Union["UserToolsCreate", "UserToolsUpdate"]
    ):
        orm_model: UserTools = UserTools(**instance.model_dump())
        return orm_model

    async def create_one(
            self,
            orm_model: UserTools
    ):
        try:
            self.session.add(orm_model)
            await self.session.commit()
            await self.session.refresh(orm_model)
            self.logger.info("%s %r was successfully created" % (CLASS, orm_model))
        except IntegrityError as error:
            self.logger.error(f"Error while orm_model creating", exc_info=error)
            raise CustomException(
                msg=Errors.ALREADY_EXISTS()
            )

    async def delete_one(
            self,
            orm_model: UserTools,
    ) -> None:
        try:
            self.logger.info(f"Deleting %r from database" % orm_model)
            await self.session.delete(orm_model)
            await self.session.commit()
        except IntegrityError as exc:
            self.logger.error("Error while deleting data from database", exc_info=exc)
            raise CustomException(
                msg="Error while deleting %r from database" % orm_model
            )

    async def edit_one(
            self,
            instance:  "UserToolsUpdate",
            orm_model: UserTools,
            is_partial: bool = False
    ):

        for key, val in instance.model_dump(
                exclude_unset=is_partial,
                exclude_none=is_partial,
        ).items():
            setattr(orm_model, key, val)

        self.logger.warning(f"Editing %r in database" % orm_model)
        try:
            await self.session.commit()
            await self.session.refresh(orm_model)
            self.logger.info("%r %r was successfully edited" % (CLASS, orm_model))
        except IntegrityError as exc:
            self.logger.error("Error occurred while editing data in database", exc_info=exc)
            raise CustomException(
                msg=Errors.already_exists_user_id(instance.user_id)
            )

    async def add_to_dict(
            self,
            usertools: UserTools,
            content: "ToolsContent",
            add_to: str = 'rv'
    ):
        if add_to == 'w':
            usertools.wishlist = await self.operate_dict(
                content=content,
                operation_dict=usertools.wishlist,
                max_length=usertools.max_length_w,
                verb='wishlist'
            )
        elif add_to == 'c':
            usertools.comparison = await self.operate_dict(
                content=content,
                operation_dict=usertools.comparison,
                max_length=usertools.max_length_c,
                verb="comparison_list"
            )
        else: # add_to == 'rv
            usertools.recently_viewed = await self.operate_dict(
                content=content,
                operation_dict=usertools.recently_viewed,
                max_length=usertools.max_length_rv
            )

        try:
            await self.session.commit()
            await self.session.refresh(usertools)
        except IntegrityError as exc:
            self.logger.error("Error occurred while editing data in database", exc_info=exc)
            raise CustomException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                msg=Errors.DATABASE_ERROR()
            )
        return usertools

    async def operate_dict(
            self,
            content: "ToolsContent",
            operation_dict: dict,
            max_length: int,
            verb: str = 'recently viewed'
    ):
        operation_dict.update(content.to_dict())
        operation_dict = dict(sorted(operation_dict.items(), key=lambda item: item[1]))

        length = len(operation_dict)
        if length > max_length:
            first_key = next(iter(operation_dict))
            item_to_remove = {first_key: operation_dict.pop(first_key)}
            self.logger.info("Removed from %s: %r" % (verb, item_to_remove))
        return operation_dict

    async def del_from_dict(
            self,
            usertools: UserTools,
            product_id: int,
            del_from: str = 'rv'
    ):
        product_id = str(product_id)
        if del_from == 'w':
            item_to_remove = usertools.wishlist.pop(product_id, None)
            verb = "wishlist"
        elif del_from == 'c':
            item_to_remove = usertools.comparison.pop(product_id, None)
            verb = "comparison list"
        else: # add_to == 'rv
            item_to_remove = usertools.recently_viewed.pop(product_id, None)
            verb = "recently viewed"

        if item_to_remove:
            self.logger.warning("Removing %s from %s" % (item_to_remove, verb))
        else:
            self.logger.error("Item with product_id=%s doesn't exists in %s" % (product_id, verb))
            raise CustomException(
                msg="Item with product_id=%s doesn't exists in %s" % (product_id, verb)
            )

        try:
            await self.session.commit()
            await self.session.refresh(usertools)
        except IntegrityError as exc:
            self.logger.error("Error occurred while editing data in database", exc_info=exc)
            raise CustomException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                msg=Errors.DATABASE_ERROR()
            )
        return usertools

    async def clear_dict(
            self,
            usertools: UserTools,
            del_from: str = 'rv'
    ):
        if del_from == 'w':
            usertools.wishlist.clear()
            verb = "wishlist"
        elif del_from == 'c':
            usertools.comparison.clear()
            verb = "comparison list"
        else:  # add_to == 'rv
            usertools.recently_viewed.clear()
            verb = "recently viewed"

        self.logger.warning("Clearing %s" % verb)

        try:
            await self.session.commit()
            await self.session.refresh(usertools)
        except IntegrityError as exc:
            self.logger.error("Error occurred while editing data in database", exc_info=exc)
            raise CustomException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                msg=Errors.DATABASE_ERROR()
            )
        return usertools
