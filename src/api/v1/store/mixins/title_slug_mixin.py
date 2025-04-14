from pydantic import computed_field
from slugify import slugify


class TitleSlugMixin:
    @computed_field
    @property
    def slug(self) -> str | None:
        if hasattr(self, 'title') and self.title:
            return slugify(self.title)
        return None
