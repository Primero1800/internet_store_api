from dataclasses import dataclass
from datetime import datetime


@dataclass
class ToolsContent:
    product_id: int
    added: datetime
