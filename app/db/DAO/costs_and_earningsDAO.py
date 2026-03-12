from types import NoneType
from typing import Literal

from datetime import datetime, timezone
from aiosqlite import IntegrityError
from abc import ABC, abstractmethod
from app.db.database import get_session


class CostsAndEarningsDAO(ABC):
    @abstractmethod
    async def init_conn(self):
        pass

    @abstractmethod
    async def get_by(self, mode: Literal["OR", "AND"], **kwargs):
        pass

    @abstractmethod
    async def create(self, user_id: int, operation_type: int, value: int, comment: str | None = None):
        pass

    @abstractmethod
    async def delete(self, id: int):
        pass

    @abstractmethod
    async def update(self, id: int, **kwargs):
        pass

    @abstractmethod
    async def do_raw_sql(self, query: str, params: tuple):
        pass


class SQLiteCostsAndEarningsDAO(CostsAndEarningsDAO):
    __slots__ = ["session"]
    __allowed_columns = ["id", "user_id", "operation_type", "value", "comment", "created_at"]

    async def init_conn(self):
        self.session = await get_session()

    async def get_by(self, mode: Literal["OR", "AND"] = "AND", **kwargs) -> list:
        query = "SELECT id, user_id, operation_type, value, comment, created_at FROM costs_and_earnings"
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

    async def create(self, user_id: int, operation_type: int, value: int, comment: str | None = None):
        query = """INSERT INTO costs_and_earnings (user_id, operation_type, value, comment, created_at)
                   VALUES (?, ?, ?, ?, ?)"""

        if operation_type not in (0, 1):
            raise ValueError('operation_type should be 0 or 1')
        try:
            await self.session.execute(query, (user_id,
                                               operation_type,
                                               value,
                                               comment,
                                               datetime.now(timezone.utc)))
            await self.session.commit()
        except IntegrityError as err:
            if "FOREIGN KEY constraint failed" in str(err):
                raise ValueError('user not found')

    async def delete(self, id: int):
        query = """DELETE FROM costs_and_earnings WHERE id = ?"""

        await self.session.execute(query, (id,))
        await self.session.commit()

    async def update(self, id: int, **kwargs):
        keys = kwargs.keys()
        if not any(i in keys for i in ("operation_type", "value", "comment")):
            return

        query = "UPDATE costs_and_earnings"
        for i in list(keys):
            if i not in ("operation_type", "value", "comment") or isinstance(kwargs[i], NoneType):
                kwargs.pop(i)
            else:
                if i != "comment" and not isinstance(kwargs[i], int):
                    raise ValueError('operation_type or value should be int')
                if i == "comment" and not isinstance(kwargs[i], str):
                    raise ValueError('comment should be str')

        columns = []
        values = []
        record_id = id
        for key, item in kwargs.items():
            columns.append(key + " = ?")
            values.append(item)
        query += " SET " + ", ".join(columns) + " WHERE id = ?"
        values.append(record_id)
        await self.session.execute(query, tuple(values))
        await self.session.commit()

    async def do_raw_sql(self, query: str, params: tuple):
        cursor = await self.session.execute(query, params)
        await self.session.commit()
        return cursor
