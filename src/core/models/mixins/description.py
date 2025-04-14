from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class DescriptionMixin:
    description: Mapped[str] = mapped_column(String(500), unique=False, nullable=False, default='')
