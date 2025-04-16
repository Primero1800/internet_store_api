from datetime import datetime
from decimal import Decimal
from typing import List, TYPE_CHECKING

from sqlalchemy import ForeignKey, DECIMAL, Boolean, Integer, DateTime, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.config.database_config import DBConfigurerInitializer
from src.core.models import Base
from src.core.models.mixins import (
    IDIntPkMixin, Title3FieldMixin, DescriptionMixin,
)
from src.core.models.store.image import ImageBase
from src.core.config.database_config import DBConfigurer
from src.tools.discount_choices import DiscountChoices

if TYPE_CHECKING:
    from src.core.models import (
        Rubric,
        Brand,
    )


class Product(IDIntPkMixin, Title3FieldMixin, DescriptionMixin, Base):

    __table_args__ = Title3FieldMixin.__table_args__ + (
        CheckConstraint("start_price > 0", name="check_start_price_min_length"),
        CheckConstraint("quantity >= 0", name="check_quantity_min_length"),
    )

    slug: Mapped[str]

    start_price: Mapped[Decimal] = mapped_column(
        DECIMAL(8, 2)
    )
    discount: Mapped[DiscountChoices] = mapped_column(
        Integer,
        default=DiscountChoices.D0.value
    )
    price: Mapped[Decimal] = mapped_column(
        DECIMAL(8, 2),
    )
    available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default='true'
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default='1',
    )
    published: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        server_default=func.now(),
        nullable=False
    )

    images: Mapped[List['ProductImage']] = relationship(
        'ProductImage',
        back_populates="product",
        cascade="all, delete",
    )

    rubrics: Mapped[list['Rubric']] = relationship(
        secondary=DBConfigurerInitializer.utils.camel2snake('RubricProductAssociation'),
        back_populates="products",
        # cascade="all, delete",
    )

    brand_id: Mapped[int] = mapped_column(
        ForeignKey(f"{DBConfigurer.utils.camel2snake('Brand')}.id", ondelete="CASCADE"),
        nullable=False,
        unique=False,
    )

    brand: Mapped['Brand'] = relationship(
        'Brand',
        back_populates='products',
    )

    def __str__(self):
        return f"Product(id={self.id}, title={self.title})"

    def __repr__(self):
        return str(self)


class ProductImage(ImageBase):
    product_id: Mapped[int] = mapped_column(
        ForeignKey(Product.id, ondelete="CASCADE"),
        nullable=False,
        unique=False,
    )

    product: Mapped[Product] = relationship(
        Product,
        back_populates='images'
    )

    def __str__(self):
        return f"ProductImage(product_id={self.product_id})"

    def __repr__(self):
        return str(self)
