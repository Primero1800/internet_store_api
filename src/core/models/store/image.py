from sqlalchemy.orm import Mapped

from src.core.models import Base
from src.core.models.mixins import IDIntPkMixin


class ImageBase(IDIntPkMixin, Base):
    __abstract__ = True

    file: Mapped[str]
