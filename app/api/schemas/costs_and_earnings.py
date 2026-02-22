from pydantic import BaseModel
from typing import Literal
from datetime import datetime


class AddRecord(BaseModel):
    operation_type: Literal[0, 1]
    value: int
    comment: str | None = None


class ChangeRecord(BaseModel):
    id: int
    operation_type: Literal[0, 1] | None = None
    value: int | None = None
    comment: str | None = None

class Record(BaseModel):
    id: int
    user_id: int
    operation_type: bool
    value: int
    comment: str | None = None
    created_at: datetime