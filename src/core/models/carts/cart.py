from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, CheckConstraint, DateTime, func, DECIMAL, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.config import DBConfigurer
from src.core.models import Base
from src.core.models.mixins import IDIntPkMixin

if TYPE_CHECKING:
    from src.core.models import (
        User,
        Product,
    )


class Cart(Base):
    user_id: Mapped[int] = mapped_column(
        ForeignKey(f"{DBConfigurer.utils.camel2snake('User')}.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    user: Mapped['User'] = relationship(
        'User',
        back_populates='cart',
    )

    created: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        server_default=func.now(),
        nullable=False
    )

    cart_items: Mapped[list['CartItem']] = relationship(
        'CartItem',
        back_populates='cart',
        cascade="all, delete"
    )

    def __str__(self):
        return f"{self.__class__.__name__}(user_id={self.user_id})"

    def __repr__(self):
        return str(self)


class CartItem(IDIntPkMixin, Base):
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_quantity_min_value"),
        UniqueConstraint('product_id', 'cart_id', name='cart_product')
    )

    cart_id: Mapped[int] = mapped_column(
        ForeignKey(f"{DBConfigurer.utils.camel2snake('Cart')}.user_id", ondelete="CASCADE"),
        nullable=False,
    )

    cart: Mapped['Cart'] = relationship(
        'Cart',
        back_populates='cart_items',
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey(f"{DBConfigurer.utils.camel2snake('Product')}.id", ondelete="CASCADE"),
        nullable=False,
    )

    product: Mapped['Product'] = relationship(
        'Product',
        back_populates='cart_items'
    )

    price: Mapped[Decimal] = mapped_column(
        DECIMAL(8, 2)
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default='1',
    )

    def __str__(self):
        return f"{self.__class__.__name__}(cart_id={self.cart_id}, product_id={self.product_id})"

    def __repr__(self):
        return str(self)
