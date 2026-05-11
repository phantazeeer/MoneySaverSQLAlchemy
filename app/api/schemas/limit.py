from datetime import date, datetime
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.api.schemas.category import Category


class Limit(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    value: Annotated[int, Field(gt=0)]
    period: Literal["day", "week", "month"] | None = None
    start: datetime
    end: datetime
    categories: list[Category]
    user_id: int

    @classmethod
    def get_from_orm(cls, orm_model) -> "Limit":
        return cls(
            id=orm_model.id,
            name=orm_model.name,
            value=orm_model.value,
            period=orm_model.period,
            start=orm_model.start,
            end=orm_model.end,
            categories=[Category.model_validate(el.category) for el in orm_model.categlimits],
            user_id=orm_model.user_id,
        )


class AvailablePeriods(str, Enum):
    day = "day"
    week = "week"
    month = "month"
    once = "once"


class CreateLimit(BaseModel):
    name: str
    value: Annotated[int, Field(gt=0)]
    period: AvailablePeriods
    start: date
    end: date
    categories: list[str]
