from sqlalchemy import String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column


class Title3FieldMixin:
    title: Mapped[str] = mapped_column(String(100), unique=True, )

    __table_args__ = (
        CheckConstraint("length(title) >= 3", name="check_title_min_length"),
    )
