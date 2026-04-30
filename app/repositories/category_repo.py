from .base_repo import BasicRepository
from app.db.models import Category


class CategoryRepository(BasicRepository):
    model = Category