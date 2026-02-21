from pydantic import BaseModel
from typing import Literal


class AddRecord(BaseModel):
    operation_type: Literal[0, 1]
    value: int
    comment: str | None = None


class ChangeRecord(BaseModel):
    id: int
    operation_type: Literal[0, 1] | None = None
    value: int | None = None
    comment: str | None = None
