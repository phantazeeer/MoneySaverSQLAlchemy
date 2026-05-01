from .base_repo import BasicRepository
from app.db.models import CostsAndEarnings, Category
from sqlalchemy import select, update
from app.db.models import User
from app.utils.logger import get_logger
from datetime import datetime

log = get_logger(__name__)

class CostsAndEarningsRepository(BasicRepository):
    model = CostsAndEarnings

    async def add_one(self, user_id: int, operation_type: int, value: int,
                      comment: str | None = None) -> CostsAndEarnings:
        record = await BasicRepository.add_one(self, user_id=user_id, operation_type=operation_type, value=value,
                                               comment=comment)
        await self.session.execute(
            update(User).values(balance=User.balance + (-1) ** int(operation_type) * value).where(User.id == user_id))
        return record

    async def update_record(self, id: int, user_id: int, operation_type: int, value: int, comment: str,
                            category_id: int) -> None:
        record = await BasicRepository.get_one(self, id=id)
        balance_change = (value - (-1) ** ((record.operation_type + operation_type) % 2) * record.value) * (
            -1) ** operation_type
        await self.session.execute(
            update(self.model).values(operation_type=operation_type, value=value, comment=comment,
                                      category_id=category_id).where(
                self.model.id == id))
        await self.session.execute(update(User).values(balance=User.balance + balance_change).where(User.id == user_id))

    async def delete_by_id(self, id: int) -> None:
        record = await BasicRepository.get_one(self, id=id)
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

    # async def get_one_by_id(self, id: int):
    #     stmt = (select(CostsAndEarnings, Category.name)
    #             .join_from(CostsAndEarnings, Category,
    #                        Category.id == CostsAndEarnings.category_id,
    #                        isouter=True).where(CostsAndEarnings.id == id))
    #     log.error(stmt)
    #     res = (await self.session.execute(stmt)).scalars().one()
    #     log.error(1)
    #     log.error(res.__dict__)
    #     log.error(1)
    #     return res