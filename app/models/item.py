from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class ItemModel:
    name: str
    price: float
    id: int | None = None
    description: str | None = None
    created_at_utc: datetime = field(default_factory=lambda: datetime.now(UTC))
