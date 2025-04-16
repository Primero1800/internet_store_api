from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models import (
    Base,
    Product,
    Rubric,
)
from src.core.models.mixins import IDIntPkMixin


class RubricProductAssociation(IDIntPkMixin, Base):
    __table_args__ = (
        UniqueConstraint("rubric_id", "product_id", name="idx_unique_rubric_product"),
    )

    rubric_id: Mapped[int] = mapped_column(ForeignKey(Rubric.id, ondelete="cascade"))
    product_id: Mapped[int] = mapped_column(ForeignKey(Product.id, ondelete="cascade"))
