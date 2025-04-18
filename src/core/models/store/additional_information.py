from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, DECIMAL, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.config import DBConfigurer
from src.core.models import Base

if TYPE_CHECKING:
    from src.core.models import (
        Product,
    )


class AdditionalInformation(Base):
    __table_args__ = (
        CheckConstraint("weight > 0", name="check_weight_min_value"),
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey(f"{DBConfigurer.utils.camel2snake('Product')}.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    product: Mapped['Product'] = relationship(
        'Product',
        back_populates='add_info',
    )

    weight: Mapped[Decimal] = mapped_column(
        DECIMAL(8, 2),
        nullable=True,
        default=None,
        server_default=None,
    )

    size: Mapped[str] = mapped_column(
        String,
        nullable=True,
        default=None,
        server_default=None
    )

    guarantee: Mapped[str] = mapped_column(
        String,
        nullable=True,
        default=None,
        server_default=None
    )

    def __str__(self):
        return f"AdditionalInformation(product_id={self.product_id})"

    def __repr__(self):
        return str(self)
