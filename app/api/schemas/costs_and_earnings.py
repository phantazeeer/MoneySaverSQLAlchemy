from pydantic import BaseModel, Field
from typing import Literal, Annotated
from datetime import datetime


class AddRecord(BaseModel):
    operation_type: Literal["0", "1"]
    value: int
    comment: Annotated[str, Field(max_length=150)] | None = None


class ChangeRecord(BaseModel):
    id: int
    operation_type: Literal["0", "1"] | None = None
    value: int | None = None
    comment: Annotated[str, Field(max_length=150)] | None = None

class Record(BaseModel):
    id: int
    user_id: int
    operation_type: bool
    value: int
    comment: Annotated[str, Field(max_length=150)] | None = None
    created_at: datetime