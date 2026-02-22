from fastapi import HTTPException

from app.db.database import get_session
from app.api.schemas import Record
from datetime import datetime, timezone
from types import NoneType


class CostsAndEarningsService:
    async def init_session(self) -> None:
        self.conn = await get_session()

    async def add_record(self, user_id: int, operation_type: int, value: int, comment: str | None = None) -> None:
        await self.conn.execute(
            """INSERT INTO costs_and_earnings (user_id, operation_type, value, comment, created_at) VALUES (?, ?, ?, ?, ?)""",
            (user_id, operation_type, value, comment, datetime.now(timezone.utc)))
        await self.conn.execute("""UPDATE user SET balance = balance + ? WHERE id = ?""",
                                ((-1) ** operation_type * value, user_id))
        await self.conn.commit()

    async def delete_record(self, id: int, user_id: int) -> None:
        record = await (await self.conn.execute("""SELECT * FROM costs_and_earnings WHERE id = ?""", (id,))).fetchone()
        if isinstance(record, NoneType):
            raise HTTPException(404, "Такой записи нет")
        if not record[1] == user_id:
            raise HTTPException(400, "Пользователь не является владельцем маршрута")
        user = await (await self.conn.execute("""SELECT * FROM user WHERE id = ?""", (record[1],))).fetchone()
        await self.conn.execute("""UPDATE user SET balance = balance - ? WHERE id = ?""",
                                ((-1) ** record[2] * record[3], user[0]))
        await self.conn.execute("""DELETE FROM costs_and_earnings WHERE id = ?""", (id,))
        await self.conn.commit()

    async def get_records_by(self, id: int | None = None, user_id: int | None = None) -> Record | list[Record]:
        if not isinstance(id, NoneType) and not isinstance(user_id, NoneType):
            cursor = await self.conn.execute("""SELECT * FROM costs_and_earnings WHERE id = ?""", (id,))
            record = await cursor.fetchone()
            if isinstance(record, NoneType):
                raise HTTPException(404, "Такой записи нет")
            if not record[1] == user_id:
                raise HTTPException(400, "Пользователь не владелец записи")
            res = Record(id=record[0],
                         user_id=record[1],
                         operation_type=record[2],
                         value=record[3],
                         comment=record[4],
                         created_at=record[5])
        elif not isinstance(user_id, NoneType):
            cursor = await self.conn.execute("""SELECT * FROM costs_and_earnings WHERE user_id = ?""", (user_id,))
            records = await cursor.fetchall()
            res = list()
            for record in records:
                res.append(Record(id=record[0],
                                  user_id=record[1],
                                  operation_type=record[2],
                                  value=record[3],
                                  comment=record[4],
                                  created_at=record[5]))
        else:
            raise HTTPException(400, 'incorrect using get_records_by')
        return res

    async def update_record(self, id: int, user_id: int, operation_type: int | None = None, value: int | None = None,
                            comment: str | None = None) -> None:
        record = await (await self.conn.execute("""SELECT * FROM costs_and_earnings WHERE id = ?""", (id,))).fetchone()
        if isinstance(record, NoneType):
            raise HTTPException(404, "Такой записи нет")
        if not record[1] == user_id:
            raise HTTPException(400, "Пользователь не владелец записи")
        if isinstance(operation_type, NoneType):
            operation_type = record[2]
        if isinstance(value, NoneType):
            value = record[3]
        if isinstance(comment, NoneType):
            comment = record[4]
        if not (operation_type == record[2] and value == record[3]):
            if operation_type == record[2]:
                balance_change = (value - record[3]) * (-1) ** operation_type
            else:
                balance_change = (value + record[3]) * (-1) ** operation_type
            user = await (await self.conn.execute("""SELECT * FROM user WHERE id = ?""", (record[1],))).fetchone()
            await self.conn.execute("""UPDATE user SET balance = balance + ? WHERE id = ?""",
                                    (balance_change, user[0]))
        await self.conn.execute(
            """UPDATE costs_and_earnings SET operation_type = ?, value = ?, comment = ? WHERE id = ?""",
            (operation_type, value, comment, id))
        await self.conn.commit()
