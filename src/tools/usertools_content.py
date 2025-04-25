from dataclasses import dataclass
from datetime import datetime


@dataclass
class ToolsContent:
    product_id: int
    added: datetime

    def to_dict(self):
        return {
            str(self.product_id): self.added.isoformat()
        }

    @classmethod
    def from_dict(cls, content: dict):
        return [
            cls(
                product_id=int(key),
                added=datetime.fromisoformat(val)
            ) for key, val in content.items()
        ]

    def __str__(self):
        return f"{self.__class__.__name__}(product_id={self.product_id})"

    def __repr__(self):
        return str(self)
