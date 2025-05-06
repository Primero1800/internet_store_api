from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, DECIMAL, JSON, DateTime, func, Integer
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.config import DBConfigurer
from src.core.models import Base
from src.core.models.mixins import IDIntPkMixin
from src.tools.moveto_choices import MoveToChoices
from src.tools.payment_conditions_choices import PaymentChoices
from src.tools.status_choices import StatusChoices

if TYPE_CHECKING:
    from src.core.models import User


class Order(IDIntPkMixin, Base):

    user_id: Mapped[int] = mapped_column(
        ForeignKey(f"{DBConfigurer.utils.camel2snake('User')}.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    user: Mapped['User'] = relationship(
        'User',
        back_populates='orders',
    )

    phonenumber: Mapped[str] = mapped_column(
        String(20), nullable=False,
    )

    total_price: Mapped[Decimal] = mapped_column(
        DECIMAL(8, 2)
    )

    order_content: Mapped[list] = mapped_column(
        MutableList.as_mutable(JSON),
        nullable=False,
    )

    person_content: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSON),
        nullable=False,
    )

    address_content: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSON),
        nullable=False,
    )

    time_placed: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        server_default=func.now(),
        nullable=False
    )

    time_delivered: Mapped[datetime] = mapped_column(
        DateTime,
        default=None,
        server_default=None,
        nullable=True
    )

    move_to: Mapped[MoveToChoices] = mapped_column(
        Integer,
        default=MoveToChoices.TO_CUSTOMER_ADDRESS.value
    )

    payment_conditions: Mapped[PaymentChoices] = mapped_column(
        Integer,
        default=PaymentChoices.P_WAITS.value
    )

    status: Mapped[StatusChoices] = mapped_column(
        Integer,
        default=StatusChoices.S_ORDERED.value
    )

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.user_id}, phonenumber={self.phonenumber!r})"

    def __repr__(self):
        return str(self)
