from typing import Literal

from pydantic import BaseModel, ConfigDict


class Limit(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    value: int
    period: Literal["day", "week", "month"]
    user_id: int
