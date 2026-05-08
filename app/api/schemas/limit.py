from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class Limit(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    value: int
    period: Literal["day", "week", "month"]
    user_id: int


class ChangeLimit(BaseModel):
    period: Literal["day", "week", "month"]
    value: Annotated[int, Field(gt=0)]
