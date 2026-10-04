from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CattleCreate(BaseModel):
    ear_tag_code: str = Field(min_length=1, max_length=50)
    breed: str = Field(min_length=1, max_length=50)
    description: str | None = None
    initial_weight_kg: float = Field(gt=0)
    purchase_price: float = Field(gt=0)
    batch_id: int = Field(gt=0)
    notes: str | None = None


class CattleWeightUpdate(BaseModel):
    current_weight_kg: float = Field(gt=0)
    notes: str | None = None


class CattleSalePriceUpdate(BaseModel):
    sale_price: float = Field(gt=0)


class CattleWeightLogResponse(BaseModel):
    id: int
    cattle_id: int
    weight_kg: float
    notes: str | None = None
    logged_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CattleResponse(BaseModel):
    id: int
    ear_tag_code: str
    breed: str
    description: str | None = None
    initial_weight_kg: float
    current_weight_kg: float
    purchase_price: float
    sale_price: float | None = None
    batch_id: int
    created_at: datetime
    weight_logs: list[CattleWeightLogResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)