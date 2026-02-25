from calendar import month
from typing import Literal

from fastapi import HTTPException

from app.db.database import get_session
from app.api.schemas import Record
from datetime import datetime, timezone, timedelta
from types import NoneType
import matplotlib.pyplot as plt
import io
import base64


class CostsAndEarningsService:
    async def init_session(self) -> None:
        self.conn = await get_session()

    async def add_record(self, user_id: int, operation_type: str, value: int, comment: str | None = None) -> None:
        await self.conn.execute(
            """INSERT INTO costs_and_earnings (user_id, operation_type, value, comment, created_at) VALUES (?, ?, ?, ?, ?)""",
            (user_id, operation_type, value, comment, datetime.now(timezone.utc)))
        await self.conn.execute("""UPDATE user SET balance = balance + ? WHERE id = ?""",
                                ((-1) ** int(operation_type) * value, user_id))
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

    async def user_costs_or_earnings(self, user_id: int, filter: Literal["costs", "earnings"]) -> list[Record]:
        op_type = 0 if filter == "earnings" else 1
        cursor = await self.conn.execute(
            """SELECT * FROM costs_and_earnings WHERE user_id = ? and operation_type = ?""", (user_id, op_type,))
        records = await cursor.fetchall()
        res = list()
        for record in records:
            res.append(Record(id=record[0],
                              user_id=record[1],
                              operation_type=record[2],
                              value=record[3],
                              comment=record[4],
                              created_at=record[5]))
        return res

    async def create_graphics(self, period: tuple[datetime, datetime], user_id: int):
        record = await self.conn.execute(
            """SELECT * FROM costs_and_earnings WHERE (created_at BETWEEN ? AND ?) AND user_id = ? ORDER BY created_at""",
            (period[0].replace(tzinfo=timezone.utc), period[1].replace(tzinfo=timezone.utc), user_id))
        user = await (await self.conn.execute(
            """SELECT balance FROM user WHERE id = ? """, (user_id,))).fetchone()
        records = await record.fetchall()
        if not records:
            return None

        records = [(i[0], i[1], i[2], i[3], i[4], datetime.strptime(i[5], "%Y-%m-%d %H:%M:%S.%f%z")) for i in records]
        now = datetime.now(timezone.utc)
        if now - records[0][5] < timedelta(days=30):
            x = [i[5].date().strftime("%d") for i in records]
        elif now - records[0][5] <= timedelta(days=360):
            x = [i[5].date().strftime("%d.%m") for i in records]
        else:
            x = [i[5].date().strftime("%d.%m.%Y") for i in records]

        balance = user[0]
        balance_y = []
        for i in records[::-1]:
            balance_y.append(balance - (-1) ** i[2] * i[3])
            balance -= (-1) ** i[2] * i[3]
        balance_y = balance_y[::-1]

        fig, ax = plt.subplots()
        ax.plot(x, balance_y)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close()

        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        return img_base64
