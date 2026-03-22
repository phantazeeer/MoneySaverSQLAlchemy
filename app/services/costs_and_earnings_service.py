from typing import Literal

from app.api.schemas import Record
from datetime import datetime, timezone, timedelta
from types import NoneType
import matplotlib.pyplot as plt
import io
import base64
from app.utils.uow import IUnitOfWork
from sqlalchemy.exc import NoResultFound

class CostsAndEarningsService:

    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    async def add_record(self, user_id: int, operation_type: str, value: int, comment: str | None = None) -> None:
        async with self.uow:
            await self.uow.records.add_one(user_id=user_id, operation_type=int(operation_type), value=value, comment=comment)

    async def delete_record(self, id: int, user_id: int) -> None:
        async with self.uow:
            try:
                record = await self.uow.records.get_one(id=id)
                if user_id != record.user_id:
                    raise ValueError("Пользователь не является владельцем записи")
                await self.uow.records.delete_by_id(id)
            except NoResultFound:
                raise Exception('Запись не найдена')

    async def get_records_by(self, id: int | None = None, user_id: int | None = None) -> Record | list[Record]:
        if not isinstance(id, NoneType) and not isinstance(user_id, NoneType):
            async with self.uow:
                try:
                    record = await self.uow.records.get_one(id=id)
                    if not record.user_id == user_id:
                        raise ValueError("Пользователь не является владельцем записи")
                    res = Record.model_validate(record)
                except NoResultFound:
                    raise Exception("Запись не найдена")
        elif not isinstance(user_id, NoneType):
            async with self.uow:
                try:
                    records = await self.uow.records.get_list_by(user_id=user_id)
                    res = [Record.model_validate(i) for i in records]
                except NoResultFound:
                    raise Exception("Записи не найдены")
        else:
            raise ValueError('Введите user_id или user_id и id')
        return res

    async def update_record(self, id: int, user_id: int, operation_type: int | None = None, value: int | None = None,
                            comment: str | None = None) -> None:
        async with self.uow:
            try:
                record = await self.uow.records.get_one(id=id)
                if record.user_id != user_id:
                    raise ValueError("Пользователь не является владельцем записи")
                if isinstance(operation_type, NoneType):
                    operation_type = record.operation_type
                if isinstance(value, NoneType):
                    value = record.value
                if isinstance(comment, NoneType):
                    comment = record.comment
                await self.uow.records.update_record(id, user_id, operation_type=operation_type, value=value, comment=comment)
            except NoResultFound:
                raise Exception("Запись не найдена")


    async def user_costs_or_earnings(self, user_id: int, filter: Literal["costs", "earnings"]) -> list[Record]:
        async with self.uow:
            op_type = 0 if filter == "earnings" else 1
            records = await self.uow.records.get_list_by(user_id=user_id, operation_type=op_type)
            res = [Record.model_validate(i) for i in records]
            return res

    async def create_graphics(self, period: tuple[datetime, datetime], user_id: int):
        records = await self.uow.records.get_list_by_date(start=period[0].replace(tzinfo=timezone.utc),
                                                         end=period[1].replace(tzinfo=timezone.utc),
                                                         user_id=user_id)
        balance = (await self.uow.users.get_one(id=user_id)).balance
        if not records:
             return None

        now = datetime.now(timezone.utc)
        if now - records[0].created_at < timedelta(days=30):
            x = [i.created_at.date().strftime("%d") for i in records]
        elif now - records[0].created_at <= timedelta(days=360):
            x = [i.created_at.date().strftime("%d.%m") for i in records]
        else:
            x = [i.created_at.date().strftime("%d.%m.%Y") for i in records]

        balance_y = []
        for i in records[::-1]:
            balance_y.append(balance - (-1) ** i.operation_type * i.value)
            balance -= (-1) ** i.operation_type * i.value
        balance_y = balance_y[::-1]

        fig, ax = plt.subplots()
        ax.plot(x, balance_y)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close()

        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        return img_base64
