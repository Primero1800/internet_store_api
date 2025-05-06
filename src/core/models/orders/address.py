from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.config import DBConfigurer
from src.core.models import Base

if TYPE_CHECKING:
    from src.core.models import User


class Address(Base):
    __table_args__ = (
        CheckConstraint("length(address) > 5", name="check_address_min_length"),
        CheckConstraint("length(city) > 1", name="check_city_min_length"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(f"{DBConfigurer.utils.camel2snake('User')}.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    user: Mapped['User'] = relationship(
        'User',
        back_populates='address',
    )

    address: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    city: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    postcode: Mapped[str] = mapped_column(
        String(16),
        nullable=True,
    )

    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )

    phonenumber: Mapped[str] = mapped_column(
        String(20), nullable=False,
    )

    def __str__(self):
        return f"{self.__class__.__name__}(user_id={self.user_id})"

    def __repr__(self):
        return str(self)
