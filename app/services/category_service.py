from sqlalchemy.exc import NoResultFound

from app.api.schemas import Category
from app.utils.logger import get_logger
from app.utils.uow import IUnitOfWork

log = get_logger(__name__)


class CategoryService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    async def add_category(self, name: str, user_id: int):
        try:
            async with self.uow:
                log.debug("Running 'add_category'")
                await self.uow.categories.add_one(name=name, user_id=user_id)
                log.debug("Category linked to user, 'add_category' done")
        except ValueError as err:
            if "Категория с таким именем уже существует" in str(err):
                raise ValueError("Категория с таким именем уже существует") from None
            else:
                log.error("Error caused in add_category", exc_info=False)
                raise err

    async def get_user_categories(self, user_id: int):
        async with self.uow:
            categories = await self.uow.categories.get_list_by(user_id=user_id)
            return [Category.model_validate(categ) for categ in categories]

    async def get_categories_by(self, category: int | str, user_id: int):
        async with self.uow:
            if isinstance(category, int):
                return Category.model_validate(await self.uow.categories.get_one(id=category, user_id=user_id))
            elif isinstance(category, str):
                return Category.model_validate(await self.uow.categories.get_one(name=category, user_id=user_id))

    async def delete_category(self, user_id: int, category_id: int | str):
        try:
            async with self.uow:
                if isinstance(category_id, str):
                    category = await self.uow.categories.get_one(user_id=user_id, name=category_id)
                    await self.uow.session.delete(category)
                elif isinstance(category_id, int):
                    category = await self.uow.categories.get_one(user_id=user_id, id=category_id)
                    await self.uow.session.delete(category)
        except NoResultFound:
            raise ValueError("Запись не найдена") from None
