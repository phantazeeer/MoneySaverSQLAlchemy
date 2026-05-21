from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class AddRecord(BaseModel):
    operation_type: Literal["0", "1"]
    value: int
    comment: Annotated[str, Field(max_length=150)] | None = None
    category: str | None = None


class ChangeRecord(BaseModel):
    operation_type: Literal["0", "1"] | None = None
    value: int | None = None
    comment: Annotated[str, Field(max_length=150)] | None = None
    category: str | None = None


class Record(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    operation_type: bool
    value: int
    comment: Annotated[str, Field(max_length=150)] | None = None
    category: str | None = None
    created_at: datetime
