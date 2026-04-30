from app.utils.uow import IUnitOfWork
from app.utils.logger import get_logger

log = get_logger(__name__)


class CategoryService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    async def add_category(self, name: str, user_id: int):
        try:
            async with self.uow:
                log.debug("Running 'add_category'")
                await self.uow.category.add_one(name=name, user_id=user_id)
                log.debug("Category linked to user, 'add_category' done")
        except ValueError as err:
            if "Категория с таким именем уже существует" in str(err):
                raise ValueError("Категория с таким именем уже существует")
            else:
                log.error("Error caused in add_category", exc_info=False)
                raise err

    async def get_user_categories(self, user_id: int):
        async with self.uow:
            categories = await self.uow.category.get_list_by(user_id=user_id)
            log.debug(f"get_user_categories sent: type of resp {type(categories)}")
            return categories

    async def change_category(self, category_id: int):
        pass

    async def delete_category(self, user_id: int, category_id: int):
        async with self.uow:
            category = await self.uow.category.get_one(id=category_id)
            if category.user_id != user_id:
                raise ValueError("Пользователь не владелец категории")
            else:
                await self.uow.category.delete_by_id(category_id)