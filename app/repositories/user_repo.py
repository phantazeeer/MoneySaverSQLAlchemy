from .base_repo import BasicRepository
from app.db.models import User
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update


class UserRepository(BasicRepository):
    model = User

    async def add_user(self, username: str, email: str, password: str):
        try:
            await self.add_one(username=username, email=email, password=password)
        except IntegrityError as err:
            if "user.email" in str(err):
                raise ValueError("Почта неуникальна")
            raise err

    async def delete_by_user(self, id: int):
        return await self.delete_by_id(id)

    async def update_user(self, id: int, **kwargs):
        elements_to_update = kwargs.keys()
        if "email" in elements_to_update:
            stmt = select(self.model).where(self.model.email == kwargs["email"])
            if (await self.session.execute(stmt)).fetchone():
                raise ValueError("email is already used")
        await self.session.execute(update(self.model).values(**kwargs).where(self.model.id == id))
