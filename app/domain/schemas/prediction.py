from datetime import datetime

from pydantic import BaseModel, Field


class PredictionCreate(BaseModel):
    sku_id: str = Field(min_length=3, max_length=64)
    price: float = Field(gt=0)
    discount: float = Field(ge=0, le=1)
    inventory: int = Field(ge=0)
    category: str = Field(min_length=2, max_length=64)
    city: str = Field(min_length=2, max_length=64)
    channel: str = Field(min_length=2, max_length=64)
    horizon_days: int = Field(default=30, ge=1, le=90)


class PredictionOut(BaseModel):
    message: str
    id: int | None = None
    sku_id: str
    predicted_demand: float
    model_version: str
    cache_hit: bool
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
