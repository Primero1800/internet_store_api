from datetime import datetime
from typing import TYPE_CHECKING

from pydantic.dataclasses import dataclass
from sqlalchemy import ForeignKey, Integer, CheckConstraint, JSON
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.config import DBConfigurer
from src.core.models import Base


if TYPE_CHECKING:
    from src.core.models import (
        User,
    )


@dataclass
class ToolsContent:
    product_id: int
    added: datetime


class UserTools(Base):
    __table_args__ = (
        CheckConstraint("max_length_rv > 0", name="check_rv_min_value"),
        CheckConstraint("max_length_c > 0", name="check_c_min_value"),
        CheckConstraint("max_length_w > 0", name="check_w_min_value"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(f"{DBConfigurer.utils.camel2snake('User')}.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    user: Mapped['User'] = relationship(
        'User',
        back_populates='usertools',
    )

    max_length_rv: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=8,
        server_default='8',
    )

    max_length_w: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=8,
        server_default='8',
    )

    max_length_c: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=4,
        server_default='4',
    )

    recently_viewed: Mapped[list[ToolsContent]] = mapped_column(
        MutableList.as_mutable(JSON),
        nullable=False,
    )

    wishlist: Mapped[list[ToolsContent]] = mapped_column(
        MutableList.as_mutable(JSON),
        nullable=False,
    )

    comparison: Mapped[list[ToolsContent]] = mapped_column(
        MutableList.as_mutable(JSON),
        nullable=False,
    )

    def __str__(self):
        return f"UserTools(user_id={self.user_id})"

    def __repr__(self):
        return str(self)
