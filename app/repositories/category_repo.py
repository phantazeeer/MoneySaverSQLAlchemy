from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError, NoResultFound

from app.db.models import Category
from app.utils.logger import get_logger

from .base_repo import BasicRepository

log = get_logger(__name__)


class CategoryRepository(BasicRepository):
    model = Category

    async def add_one(self, name: str, user_id: int) -> Category:
        try:
            return await super().add_one(name=name, user_id=user_id)  # TODO:  обработать добавление для
            # несуществующего пользователя
        except IntegrityError as err:
            if "categories.name" in str(err):
                raise ValueError("Категория с таким именем уже существует") from None
            else:
                log.error("Error caused in add_one", exc_info=False)
                raise err

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
