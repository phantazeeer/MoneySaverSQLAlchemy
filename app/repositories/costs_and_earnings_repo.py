from .base_repo import BasicRepository
from app.db.models import CostsAndEarnings
from sqlalchemy import select, update
from app.db.models import User
from datetime import datetime


class CostsAndEarningsRepository(BasicRepository):
    model = CostsAndEarnings

    async def add_one(self, user_id: int, operation_type: int, value: int, comment: str | None = None) -> None:
        await BasicRepository.add_one(self, user_id=user_id, operation_type=operation_type, value=value,
                                      comment=comment)
        await self.session.execute(
            update(User).values(balance=User.balance + (-1) ** int(operation_type) * value).where(User.id == user_id))

    async def update_record(self, id: int, user_id: int, operation_type: int, value: int, comment: str) -> None:
        record = await self.get_one(id=id)
        balance_change = (value - (-1) ** ((record.operation_type + operation_type) % 2) * record.value) * (-1) ** operation_type
        await self.session.execute(
            update(self.model).values(operation_type=operation_type, value=value, comment=comment).where(self.model.id == id))
        await self.session.execute(update(User).values(balance=User.balance + balance_change).where(User.id == user_id))

    async def delete_by_id(self, id: int) -> None:
        record = await self.get_one(id=id)
        await BasicRepository.delete_by_id(self, id)
        await self.session.execute(
            update(User).values(balance=User.balance - record.value * (-1) ** record.operation_type).where(
                User.id == record.user_id))

    async def get_list_by_date(self, start: datetime, end: datetime, user_id: int):
        record = await self.session.execute(select(CostsAndEarnings)
                                            .where(CostsAndEarnings.created_at >= start,
                                                   CostsAndEarnings.created_at <= end,
                                                   CostsAndEarnings.user_id == user_id)
                                            .order_by(CostsAndEarnings.created_at))
        return record.scalars().all()
