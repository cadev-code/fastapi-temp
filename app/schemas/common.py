from datetime import UTC, datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    environment: str
    timestamp_utc: datetime = Field(default_factory=lambda: datetime.now(UTC))
