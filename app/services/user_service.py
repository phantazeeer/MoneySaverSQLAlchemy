from app.utils import get_password_hash, verify_password, create_token
from app.api.schemas import User
from fastapi import HTTPException
from sqlite3 import IntegrityError
from app.db.DAO import UserDAO


class UserService:
    async def init_session(self, userdao: UserDAO):
        self.user_dao = userdao
        await self.user_dao.init_conn()

    async def add_user(self, username: str, email: str, password: str) -> None:
        await self.user_dao.create(username=username, email=email, password=get_password_hash(password))

    async def get_user_by(self, email: str | None = None, id: int | None = None) -> User:
        if email:
            row = (await self.user_dao.get_by(email=email))[0]
        elif id:
            row = (await self.user_dao.get_by(id=id))[0]
        else:
            raise HTTPException(400, 'incorrect using get_user_by')
        user = User(balance=row.balance,
                    username=row.username,
                    email=row.email,
                    goal_name=row.goal_name,
                    goal_value= int(row.goal_value) if row.goal_value else 0,  # доделать страницу отображения пользователя
                    created_at=row.created_at)
        return user

    async def delete_user(self, id: int) -> None:
        await self.user_dao.delete(id=id)

    async def update_user(self, id: int, **kwargs) -> None:
        try:
            await self.user_dao.update(id=id, **kwargs)
        except IntegrityError as err:
            if "user.email" in str(err):
                raise HTTPException(400, "Введите другую почту")

    async def login(self, email: str, password: str) -> str:
        users = await self.user_dao.get_by(email=email)
        if len(users) == 0:
            raise HTTPException(404, "Пользователь не найден")
        user = users[0]
        if not verify_password(password, user.password):
            raise HTTPException(400, "Неправильный пароль")
        else:
            access_token = create_token(user.id)
            return access_token
