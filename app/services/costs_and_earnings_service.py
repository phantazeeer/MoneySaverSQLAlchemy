from typing import Literal

from fastapi import HTTPException

from app.db.database import get_session
from app.api.schemas import Record
from datetime import datetime, timezone, timedelta
from types import NoneType
import matplotlib.pyplot as plt
import io
import base64
from app.db.DAO import UserDAO, CostsAndEarningsDAO as CEDAO


class CostsAndEarningsService:

    async def init_session(self, userdao: UserDAO, cedao: CEDAO) -> None:
        self.userdao = userdao
        await self.userdao.init_conn()
        self.cedao = cedao
        await self.cedao.init_conn()

    async def add_record(self, user_id: int, operation_type: str, value: int, comment: str | None = None) -> None:
        await self.cedao.create(user_id=user_id, operation_type=int(operation_type), value=value)
        await self.userdao.do_raw_sql("""UPDATE user SET balance = balance + ? WHERE id = ?""",
                                      ((-1) ** int(operation_type) * value, user_id))

    async def delete_record(self, id: int, user_id: int) -> None:
        records = await self.cedao.get_by(id=id, mode="AND")
        if not records:
            raise HTTPException(404, "Такой записи нет")
        record = records[0]
        if not record[1] == user_id:
            raise HTTPException(400, "Пользователь не является владельцем маршрута")
        user = (await self.userdao.get_by(mode="AND", id=user_id))[0]
        await self.userdao.do_raw_sql("""UPDATE user SET balance = balance - ? WHERE id = ?""",
                                      ((-1) ** record[2] * record[3], user[0]))
        await self.cedao.delete(id=id)

    async def get_records_by(self, id: int | None = None, user_id: int | None = None) -> Record | list[Record]:
        if not isinstance(id, NoneType) and not isinstance(user_id, NoneType):
            records = await self.cedao.get_by(id=id, mode="AND")
            if not records:
                raise HTTPException(404, "Такой записи нет")
            record = records[0]
            if not record[1] == user_id:
                raise HTTPException(400, "Пользователь не владелец записи")
            res = Record(id=record[0],
                         user_id=record[1],
                         operation_type=record[2],
                         value=record[3],
                         comment=record[4],
                         created_at=record[5])
        elif not isinstance(user_id, NoneType):
            records = await self.cedao.get_by(mode="AND", user_id=user_id)
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
        records = await self.cedao.get_by(mode="AND", id=id)
        if not records:
            raise HTTPException(404, "Такой записи нет")
        record = records[0]
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
            user = (await self.userdao.get_by(mode="AND", id=record[1]))[0]
            await self.userdao.do_raw_sql("""UPDATE user SET balance = balance + ? WHERE id = ?""",
                                          (balance_change, user[0]))
        await self.cedao.update(id=id, operation_type=operation_type, value=value, comment=comment)

    async def user_costs_or_earnings(self, user_id: int, filter: Literal["costs", "earnings"]) -> list[Record]:
        op_type = 0 if filter == "earnings" else 1
        records = await self.cedao.get_by(mode="AND", user_id=user_id, operation_type=op_type)
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
        record = await self.cedao.do_raw_sql(
            """SELECT * FROM costs_and_earnings WHERE (created_at BETWEEN ? AND ?) AND user_id = ? ORDER BY created_at""",
            (period[0].replace(tzinfo=timezone.utc), period[1].replace(tzinfo=timezone.utc), user_id))
        balance = (await self.userdao.get_by(mode="AND", id=user_id))[0][0]
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
