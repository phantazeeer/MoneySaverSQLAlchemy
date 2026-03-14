from types import NoneType
from typing import Annotated

from pydantic import BaseModel, EmailStr, model_validator
from datetime import datetime

class UserDTO(BaseModel):
    id: int
    balance: int
    username: str
    email: Annotated[str, EmailStr]
    password: str
    goal_value: int | None = None
    goal_name: str | None = None
    created_at: datetime

    @model_validator(mode='after')
    def goal_check(self):
        goal_name_exists = not isinstance(self.goal_name, NoneType)
        goal_value_exists = not isinstance(self.goal_value, NoneType)

        if goal_value_exists != goal_name_exists:
            raise ValueError('goal_value and goal_name should be filled')
        return self
