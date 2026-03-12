from types import NoneType
from typing import Annotated

from pydantic import BaseModel, EmailStr, model_validator
from datetime import datetime

class UserDTO(BaseModel):
    id: int
    balance: int
    username: str
    email: Annotated[str, EmailStr]
    goal: str | None = None
    goal_value: int | None = None
    goal_name: str | None = None
    created_at: datetime

    @model_validator(mode='after')
    def goal_check(self):
        goal_name_exists = not isinstance(self.goal_name, NoneType)
        goal_value_exists = not isinstance(self.goal_value, NoneType)
        goal_exists = not isinstance(self.goal, NoneType)

        if not goal_exists and not goal_value_exists and not goal_name_exists:
            raise ValueError('goal should be filled')
        if goal_exists:
            if self.goal.count("#") != 1:
                raise ValueError('incorrect goal')
            self.goal_name, gv = self.goal.split("#")
            gv = "0" + gv
            if not gv.isdigit():
                raise ValueError('goal_value should be integer')
            self.goal_value = int(gv)
        elif not goal_name_exists or not goal_value_exists:
            raise ValueError('goal or goal_name and goal_value should be filled')
        else:
            self.goal = self.goal_name + "#" + str(self.goal_value)
        return self
