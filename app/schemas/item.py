from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, examples=["Teclado Mecánico"])
    description: str | None = Field(default=None, max_length=500)
    price: float = Field(..., gt=0, description="El precio debe ser mayor a 0")

    model_config = ConfigDict(str_strip_whitespace=True)


class ItemCreate(ItemBase):
    """Schema de entrada para crear un Item."""


class ItemResponse(ItemBase):
    """Schema de salida expuesto en la API."""

    id: int
    created_at_utc: datetime

    model_config = ConfigDict(from_attributes=True)
