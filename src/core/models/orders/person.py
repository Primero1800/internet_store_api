from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.config import DBConfigurer
from src.core.models import Base

if TYPE_CHECKING:
    from src.core.models import User


class Person(Base):
    __table_args__ = (
        CheckConstraint("length(firstname) > 1", name="check_name_min_length"),
        CheckConstraint("length(company_name) > 1", name="check_company_name_min_length"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(f"{DBConfigurer.utils.camel2snake('User')}.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    user: Mapped['User'] = relationship(
        'User',
        back_populates='person',
    )

    firstname: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    lastname: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        default=None,
        server_default=None,
    )

    company_name: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        default=None,
        server_default=None,
    )

    def __str__(self):
        return f"{self.__class__.__name__}(user_id={self.user_id})"

    def __repr__(self):
        return str(self)
