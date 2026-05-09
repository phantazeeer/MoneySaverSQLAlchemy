from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError, NoResultFound

from app.db.models import CostsAndEarnings, User

from .base_repo import BasicRepository


class UserRepository(BasicRepository):
    model = User

    async def add_user(self, username: str, email: str, password: str):
        try:
            await self.add_one(username=username, email=email, password=password)
        except IntegrityError as err:
            if "user.email" in str(err):
                raise ValueError("Почта неуникальна") from None
            raise err

    async def get_one(self, **kwargs):
        try:
            return await super().get_one(**kwargs)
        except NoResultFound:
            params = ", ".join(f"{i}={kwargs[i]}" for i in kwargs.keys())
            raise Exception("Пользователь с %s не найден", params) from None

    async def delete_by_user(self, id: int):
        try:
            return await self.delete_by_id(id)
        except Exception:
            raise Exception("Пользователь с id=%s не найден", id) from None

    async def update_user(self, id: int, **kwargs):
        elements_to_update = kwargs.keys()
        if "email" in elements_to_update:
            stmt = select(self.model).where(self.model.email == kwargs["email"])
            if (await self.session.execute(stmt)).fetchone():
                raise ValueError("email is already used")
        await self.session.execute(update(self.model).values(**kwargs).where(self.model.id == id))

    async def get_user_costs_and_earnings(self, id: int):
        stmt_e = select(func.sum(CostsAndEarnings.value)).where(
            CostsAndEarnings.user_id == id,
            CostsAndEarnings.operation_type == 0,
        )
        stmt_c = select(func.sum(CostsAndEarnings.value)).where(
            CostsAndEarnings.user_id == id,
            CostsAndEarnings.operation_type == 1,
        )
        return (await self.session.execute(stmt_e)).scalar_one(), (await self.session.execute(stmt_c)).scalar_one()

    async def get_costs_after_timestamp(self, id: int, after: datetime):
        stmt = select(func.sum(CostsAndEarnings.value)).where(
            CostsAndEarnings.created_at > after,
            CostsAndEarnings.user_id == id,
            CostsAndEarnings.operation_type == 1,
        )
        return (await self.session.execute(stmt)).scalar_one()
