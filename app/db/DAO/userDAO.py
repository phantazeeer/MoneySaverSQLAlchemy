from datetime import datetime, timezone
from types import NoneType
from typing import Literal

from abc import ABC, abstractmethod
from sqlite3 import IntegrityError
from app.db.database import get_session


class UserDAO(ABC):
    @abstractmethod
    async def init_conn(self):
        pass

    @abstractmethod
    async def get_by(self, mode: Literal["OR", "AND"], **kwargs):
        pass

    @abstractmethod
    async def create(self, username: str, email: str, password: str):
        pass

    @abstractmethod
    async def delete(self, id: int):
        pass

    @abstractmethod
    async def update(self, id: int, **kwargs):
        pass


class SQLiteUserDAO(UserDAO):
    __slots__ = ["session"]
    __allowed_columns = ["id", "balance", "username", "email", "goal", "created_at"]

    async def init_conn(self):
        self.session = await get_session()

    async def get_by(self, mode: Literal["OR", "AND"] = "AND", **kwargs):
        query = "SELECT balance, username, email, goal, created_at FROM user"
        if mode not in ("OR", "AND"):
            raise ValueError("choose OR either AND")

        columns = []
        values = []
        if kwargs:
            for i in list(kwargs.keys()):
                if i not in self.__allowed_columns:
                    kwargs.pop(i)

            for key, item in kwargs.items():
                columns.append(key + " = ?")
                values.append(item)
            if kwargs:
                query += " WHERE " + f" {mode} ".join(columns)
        cursor = await self.session.execute(query, tuple(values))
        return await cursor.fetchall()

    async def create(self, username: str, email: str, password: str):
        query = """INSERT INTO user (username, email, password, created_at)
                   VALUES (?, ?, ?, ?)"""

        try:
            await self.session.execute(query, (username,
                                               email,
                                               password,
                                               datetime.now(timezone.utc)))
            await self.session.commit()
        except IntegrityError as err:
            if 'UNIQUE constraint failed: user.email' in str(err):
                raise ValueError("account with this email already exists")

    async def delete(self, id: int):
        query = """DELETE FROM user WHERE id = ?"""

        await self.session.execute(query, (id,))
        await self.session.commit()

    async def update(self, id: int, **kwargs):
        keys = kwargs.keys()
        if not any(i in keys for i in ("balance", "username", "email", "goal")):
            return

        query = "UPDATE user"
        for i in list(keys):
            if i not in ("balance", "username", "email", "goal") or isinstance(kwargs[i], NoneType):
                kwargs.pop(i)
            else:
                if i != "balance" and not isinstance(kwargs[i], str):
                    raise ValueError("username, email, goal should be str")
                if i == "balance" and not isinstance(kwargs[i], int):
                    raise ValueError("balance should be int")

        columns = []
        values = []
        user_id = id
        for key, item in kwargs.items():
            columns.append(key + " = ?")
            values.append(item)
        query += " SET " + ", ".join(columns) + " WHERE id = ?"
        values.append(user_id)
        await self.session.execute(query, tuple(values))
        await self.session.commit()
