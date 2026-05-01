from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Annotated
from datetime import datetime


class Category(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    user_id: int