from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.config import DBConfigurer
from src.core.models import Base

if TYPE_CHECKING:
    from src.core.models import (
        Product,
    )


class SaleInformation(Base):
    __table_args__ = (
        CheckConstraint("sold_count >= 0", name="check_sold_count_min_value"),
        CheckConstraint("viewed_count >= 0", name="check_viewed_count_min_value"),
        CheckConstraint("voted_count >= 0", name="check_voted_count_min_value"),
        CheckConstraint("rating >= 0", name="check_rating_min_value"),
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey(f"{DBConfigurer.utils.camel2snake('Product')}.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    product: Mapped['Product'] = relationship(
        'Product',
        back_populates='sale_info',
    )

    sold_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default='0',
    )

    voted_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default='0',
    )

    viewed_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default='0',
    )

    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        default=None,
        server_default=None,
    )

    def __str__(self):
        return f"SaleInformation(product_id={self.product_id})"

    def __repr__(self):
        return str(self)
