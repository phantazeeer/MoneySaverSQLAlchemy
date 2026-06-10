import base64
import io
from datetime import datetime, timedelta, timezone
from types import NoneType
from typing import Literal

import matplotlib.pyplot as plt
from sqlalchemy.exc import NoResultFound

from app.api.schemas import Record
from app.utils.logger import get_logger
from app.utils.uow import IUnitOfWork

log = get_logger(__name__)


class CostsAndEarningsService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    async def add_record(
        self,
        user_id: int,
        operation_type: str,
        value: int,
        comment: str | None = None,
        category: str | None = None,
    ) -> None:
        try:
            async with self.uow:
                record_id = (
                    await self.uow.records.add_one(
                        user_id=user_id,
                        operation_type=int(operation_type),
                        value=value,
                        comment=comment,
                    )
                ).id
                if category:
                    try:
                        db_category = (await self.uow.categories.get_one(name=category, user_id=user_id)).name
                    except NoResultFound:
                        db_category = (await self.uow.categories.add_one(user_id=user_id, name=category)).name
            if category:
                await self.update_record(id=record_id, user_id=user_id, category=db_category)
        except Exception:
            log.exception(
                "Exception in add_record with user_id=%s, operation_type=%s, value=%s, comment=%s, category=%s",
                user_id,
                operation_type,
                value,
                comment,
                category,
                exc_info=False,
            )
            raise

    async def delete_record(self, id: int, user_id: int) -> None:
        try:
            async with self.uow:
                record = await self.uow.records.get_one(id=id)
                if user_id != record.user_id:
                    raise ValueError("Пользователь не является владельцем записи") from None
                await self.uow.records.delete_by_id(id)
        except NoResultFound:
            raise Exception("Запись не найдена") from None
        except ValueError as err:
            if str(err) == "Пользователь не является владельцем записи":
                raise
        except Exception:
            log.exception("Exception in delete_record with user_id=%s, record=%s", user_id, id, exc_info=False)
            raise

    async def get_records_by(self, id: int | None = None, user_id: int | None = None) -> Record | list[Record]:
        if not isinstance(id, NoneType) and not isinstance(user_id, NoneType):
            async with self.uow:
                try:
                    record = await self.uow.records.get_one(id=id)
                    if not record.user_id == user_id:
                        raise ValueError("Пользователь не является владельцем записи") from None
                    if record.category_id:
                        category_name = (await self.uow.categories.get_one(id=record.category_id)).name
                    else:
                        category_name = None
                    res = {
                        "id": record.id,
                        "user_id": record.user_id,
                        "operation_type": record.operation_type,
                        "value": record.value,
                        "comment": record.comment,
                        "category": category_name,
                        "created_at": record.created_at,
                    }
                    res = Record.model_validate(res)
                except NoResultFound:
                    raise Exception("Запись не найдена") from None
                except Exception as err:
                    if str(err) == "Пользователь не является владельцем записи":
                        raise
                    else:
                        log.exception("Exception in get_records_by with id=%s, user_id=%s", id, user_id, exc_info=False)
                        raise
        elif not isinstance(user_id, NoneType):
            async with self.uow:
                try:
                    records = await self.uow.records.get_list_by(user_id=user_id)
                    res = []
                    for record in records:
                        if record.category_id:
                            category_name = (await self.uow.categories.get_one(id=record.category_id)).name
                        else:
                            category_name = None
                        res.append(
                            {
                                "id": record.id,
                                "user_id": record.user_id,
                                "operation_type": record.operation_type,
                                "value": record.value,
                                "comment": record.comment,
                                "category": category_name,
                                "created_at": record.created_at,
                            },
                        )
                    res = [Record.model_validate(i) for i in res]
                except NoResultFound:
                    raise Exception("Записи не найдены") from None
                except Exception:
                    log.exception("Exception in get_records_by with user_id=%s", user_id, exc_info=False)
                    raise
        else:
            raise ValueError("Введите user_id или user_id и id") from None
        return res

    async def update_record(
        self,
        id: int,
        user_id: int,
        operation_type=None,
        value: int | None = None,
        comment: str | None = None,
        category: str | None = None,
    ) -> None:
        async with self.uow:
            try:
                record = await self.uow.records.get_one(id=id)
                if not isinstance(category, NoneType):
                    try:
                        category_id = (await self.uow.categories.get_one(name=category, user_id=user_id)).id
                    except NoResultFound:
                        category_id = (await self.uow.categories.add_one(user_id=user_id, name=category)).id
                else:
                    category_id = None
                if record.user_id != user_id:
                    raise ValueError("Пользователь не является владельцем записи") from None
                if isinstance(operation_type, NoneType):
                    operation_type = record.operation_type
                if isinstance(value, NoneType):
                    value = record.value
                if isinstance(comment, NoneType):
                    comment = record.comment
                await self.uow.records.update_record(
                    id,
                    user_id,
                    operation_type=operation_type,
                    value=value,
                    comment=comment,
                    category_id=category_id,
                )
            except NoResultFound:
                raise Exception("Запись не найдена") from None
            except Exception as err:
                if str(err) == "Пользователь не является владельцем записи":
                    raise
                log.exception(
                    "Exception in get_records_by with "
                    "id=%s, user_id=%s, operation_type=%s, value=%s, comment=%s, category=%s",
                    id,
                    user_id,
                    operation_type,
                    value,
                    comment,
                    category,
                    exc_info=False,
                )
                raise

    async def user_costs_or_earnings(self, user_id: int, filter: Literal["costs", "earnings"]) -> list[Record]:
        try:
            async with self.uow:
                op_type = 0 if filter == "earnings" else 1
                records = (await self.uow.records.get_list_by(user_id=user_id, operation_type=op_type)).all()
                res = []
                for record in records:
                    if record.category_id:
                        category_name = (await self.uow.categories.get_one(id=record.category_id)).name
                    else:
                        category_name = None
                    res.append(
                        {
                            "id": record.id,
                            "user_id": record.user_id,
                            "operation_type": record.operation_type,
                            "value": record.value,
                            "comment": record.comment,
                            "category": category_name,
                            "created_at": record.created_at,
                        },
                    )
                res = [Record.model_validate(i) for i in res]
                return res
        except Exception:
            log.exception(
                "Exception in user_costs_or_earnings with user_id=%s, filter=%s",
                user_id,
                filter,
                exc_info=False,
            )
            raise

    async def create_graphics(self, period: tuple[datetime, datetime], user_id: int):
        try:
            async with self.uow:
                db_records = await self.uow.records.get_list_by_date(
                    start=period[0],
                    end=period[1],
                    user_id=user_id,
                )
                res = []
                for record in db_records:
                    if record.category_id:
                        category_name = (await self.uow.categories.get_one(id=record.category_id)).name
                    else:
                        category_name = None
                    res.append(
                        {
                            "id": record.id,
                            "user_id": record.user_id,
                            "operation_type": record.operation_type,
                            "value": record.value,
                            "comment": record.comment,
                            "category": category_name,
                            "created_at": record.created_at,
                        },
                    )
                records = [Record.model_validate(i) for i in res]
                balance = (await self.uow.users.get_one(id=user_id)).balance
                if not records:
                    return None

            now = datetime.now(timezone.utc)
            if records[0].created_at.tzinfo is None:
                now = now.replace(tzinfo=None)

            delta = now - records[0].created_at
            if delta < timedelta(days=30):
                x = [i.created_at.date().strftime("%d") for i in records]
            elif delta <= timedelta(days=360):
                x = [i.created_at.date().strftime("%d.%m") for i in records]
            else:
                x = [i.created_at.date().strftime("%d.%m.%Y") for i in records]

            balance_y = []
            for i in records[::-1]:
                balance_y.append(balance - (-1) ** i.operation_type * i.value)
                balance -= (-1) ** i.operation_type * i.value
            balance_y = balance_y[::-1]

            _, ax = plt.subplots()
            ax.plot(x, balance_y)
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
            plt.close()

            buf.seek(0)
            img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            return img_base64
        except Exception:
            log.exception("Exception in create_graphics with user_id=%s, period=%s", user_id, period, exc_info=False)
            raise
