from datetime import datetime

from fastapi_users.db import(
    SQLAlchemyBaseUserTable,
)
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship,
)

from src.core.models import Base
from src.core.models.mixins import IDIntPkMixin


class User(Base, IDIntPkMixin, SQLAlchemyBaseUserTable[int]):
    firstname: Mapped[str] = mapped_column(
        String(50),
        default='John',
        server_default='John',
        nullable=True,
    )

    lastname: Mapped[str] = mapped_column(
        String(50),
        default='Doe',
        server_default='Doe',
        nullable=True,
    )

    data_joined: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        server_default=func.now(),
        nullable=False
    )

    last_login: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
    )


    # session: Mapped['Session'] = relationship(
    #     "Session",
    #     back_populates="user",
    #     cascade="all, delete",
    # )

    def __str__(self):
        return (f"{self.__class__.__name__}("
                f"id={self.id}, "
                f"email={self.email})")

    def __repr__(self):
        return str(self)