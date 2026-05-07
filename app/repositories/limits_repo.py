from sqlalchemy import delete, update
from sqlalchemy.exc import NoResultFound

from app.db.models import UserLimits
from app.utils.logger import get_logger

from .base_repo import BasicRepository

log = get_logger(__name__)


class LimitsRepository(BasicRepository):
    model = UserLimits

    async def get_one(self, **kwargs):
        try:
            return await super().get_one(**kwargs)
        except NoResultFound:
            raise Exception("У пользователя нет лимита") from None

    async def delete_by_user(self, user_id: int):
        try:
            stmt = delete(self.model).where(self.model.user_id == user_id).returning(self.model.id)
            return (await self.session.execute(stmt)).scalar_one()
        except NoResultFound:
            raise Exception("У пользователя нет лимита") from None

    async def update_limit(self, user_id: int, period: str, value: int):
        try:
            stmt = (
                update(self.model)
                .values(period=period, value=value)
                .where(self.model.user_id == user_id)
                .returning(self.model)
            )
            return (await self.session.execute(stmt)).scalar_one()
        except NoResultFound:
            raise Exception("У пользователя нет лимита") from None
