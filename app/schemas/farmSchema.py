from pydantic import BaseModel, ConfigDict, Field


class FarmCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    location: str = Field(min_length=1, max_length=255)
    capacity_head_count: int = Field(ge=0)
    capacity_current_head_count: int = Field(default=0, ge=0)


class FarmCapacityUpdate(BaseModel):
    value: int = Field(ge=0)


class FarmDetailsUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    location: str | None = Field(default=None, min_length=1, max_length=255)


class FarmResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    location: str
    capacity_head_count: int
    capacity_current_head_count: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
