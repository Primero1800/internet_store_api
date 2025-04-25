from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import ForeignKey, String, DateTime, func, CheckConstraint
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.core.config import DBConfigurer
from src.core.models.mixins import (
    IDIntPkMixin,
)
from src.core.models import Base

if TYPE_CHECKING:
    from src.core.models import (
        Product,
        User,
    )


class Post(IDIntPkMixin, Base):
    __table_args__ = (
        CheckConstraint("length(name) > 2", name="check_name_min_length"),
        CheckConstraint("length(name) <= 75", name="check_name_max_length")
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey(f"{DBConfigurer.utils.camel2snake('Product')}.id", ondelete="SET NULL"),
        nullable=True,
    )

    product: Mapped['Product'] = relationship(
        "Product",
        back_populates='posts'
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(f"{DBConfigurer.utils.camel2snake('User')}.id", ondelete="CASCADE"),
        nullable=False,
    )

    user: Mapped['User'] = relationship(
        'User',
        back_populates='posts',
    )

    name: Mapped[str] = mapped_column(
        String(75),
        default='Anonymous',
        server_default='Anonymous',
    )

    review: Mapped[str] = mapped_column(
        String(1000),
        default='review',
        server_default='review',
        nullable=False
    )

    published: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        server_default=func.now(),
        nullable=False
    )

    def __str__(self):
        return f"Post(id={self.id})"

    def __repr__(self):
        return str(self)