from sqlalchemy.exc import IntegrityError

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
