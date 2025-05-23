from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, DateTime, func, CheckConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models import Base
from src.core.models.mixins import (
    IDIntPkMixin,
)
from src.core.config.database_config import DBConfigurer
from src.tools.stars_choices import StarsChoices

if TYPE_CHECKING:
    from src.core.models import (
        Product,
        User,
    )


class Vote(IDIntPkMixin, Base):
    __table_args__ = (
        CheckConstraint("length(name) > 2", name="check_name_min_length"),
        UniqueConstraint('product_id', 'user_id', name='product_user')
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey(f"{DBConfigurer.utils.camel2snake('Product')}.id", ondelete="CASCADE"),
        nullable=False,
        unique=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(f"{DBConfigurer.utils.camel2snake('User')}.id", ondelete="SET NULL"),
        nullable=True,
        unique=False,
    )

    name: Mapped[str] = mapped_column(String(50), unique=False)
    review: Mapped[str] = mapped_column(
        String(1000),
        unique=False,
        nullable=True,
        default=None,
        server_default=None
    )

    published: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        server_default=func.now(),
        nullable=False
    )
    stars: Mapped[StarsChoices] = mapped_column(
        Integer,
        default=StarsChoices.S5.value
    )

    product: Mapped['Product'] = relationship(
        'Product',
        back_populates='votes',
    )

    user: Mapped['User'] = relationship(
        'User',
        back_populates='votes',
    )
