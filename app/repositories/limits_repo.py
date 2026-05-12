from sqlalchemy import delete, insert, select
from sqlalchemy.exc import NoResultFound

from app.db.models import CategoriesLimits, UserLimits
from app.utils.logger import get_logger

from .base_repo import BasicRepository

log = get_logger(__name__)


class LimitsRepository(BasicRepository):
    model = UserLimits

    async def get_one(self, user_id: int, **kwargs):
        try:
            stmt = select(UserLimits).where(UserLimits.user_id == user_id).filter_by(**kwargs)
            return (await self.session.execute(stmt)).scalar_one()
        except NoResultFound:
            raise Exception("У пользователя нет этого лимита") from None

    async def get_list_by(self, user_id: int, **kwargs):
        try:
            stmt = select(UserLimits).where(UserLimits.user_id == user_id).filter_by(**kwargs)
            return (await self.session.execute(stmt)).scalars().all()
        except NoResultFound:
            raise Exception("У пользователя нет лимитов") from None

    async def delete_by_user(self, user_id: int):
        try:
            stmt = delete(self.model).where(self.model.user_id == user_id).returning(self.model.id)
            return (await self.session.execute(stmt)).scalars().all()
        except NoResultFound:
            raise Exception("У пользователя нет лимитов") from None

    async def delete_by_id(self, id: int):
        try:
            stmt = delete(self.model).where(self.model.id == id).returning(self.model.id)
            return (await self.session.execute(stmt)).scalar_one()
        except NoResultFound:
            raise Exception("Такого лимита не существует") from None

    async def delete_by_name_and_user(self, user_id: int, name: str):
        try:
            stmt = (
                delete(self.model)
                .where(self.model.name == name, self.model.user_id == user_id)
                .returning(self.model.id)
            )
            return (await self.session.execute(stmt)).scalar_one()
        except NoResultFound:
            raise Exception("Такого лимита не существует") from None

    async def add_one(self, categories, **kwargs):
        limit = await super().add_one(**kwargs)
        await self.session.execute(
            insert(CategoriesLimits),
            [{"limit_id": limit.id, "categ_id": i} for i in categories],
        )
