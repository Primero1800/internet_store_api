from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.core.config.database_config import DBConfigurerInitializer
from src.core.models.mixins import (
    IDIntPkMixin, DescriptionMixin, Title3FieldMixin,
)
from src.core.models.store.image import ImageBase
from src.core.models import Base

if TYPE_CHECKING:
    from src.core.models import Product


class Rubric(IDIntPkMixin, Title3FieldMixin, DescriptionMixin, Base):
    slug: Mapped[str]
    image: Mapped['RubricImage'] = relationship(
        "RubricImage",
        back_populates="rubric",
        cascade="all, delete",
    )

    products: Mapped[list['Product']] = relationship(
        secondary=DBConfigurerInitializer.utils.camel2snake('RubricProductAssociation'),
        back_populates="rubrics",
        # overlaps="orders_details",
    )

    def __str__(self):
        return f"Rubric(id={self.id}, title={self.title})"

    def __repr__(self):
        return str(self)


class RubricImage(ImageBase):
    rubric_id: Mapped[int] = mapped_column(
            ForeignKey(Rubric.id, ondelete="CASCADE"),
            nullable=False,
            unique=True,
        )

    rubric: Mapped[Rubric] = relationship(Rubric, back_populates='image')

    def __str__(self):
        return f"RubricImage(rubric_id={self.rubric_id})"

    def __repr__(self):
        return str(self)