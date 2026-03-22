from pydantic import BaseModel, EmailStr, model_validator, ConfigDict
from types import NoneType
from datetime import datetime

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserChange(BaseModel):
    balance: int | None = None
    username: str | None = None
    email: EmailStr | None = None
    goal_name: str | None = None
    goal_value: int | None = None

    @model_validator(mode='after')
    def clean_model(self):
        """Удаляет поля со значениями None"""
        attrs = self.__dict__.copy()
        for i in attrs.keys():
            if isinstance(attrs[i], NoneType):
                self.__delattr__(i)
        return self


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    balance: int
    username: str
    email: EmailStr
    goal_name: str | None = None
    goal_value: int | None = None
    created_at: datetime
