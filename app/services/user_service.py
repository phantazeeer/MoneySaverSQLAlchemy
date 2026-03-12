from app.db.database import get_session
from app.utils import get_password_hash, verify_password, create_token
from app.api.schemas import User
from datetime import datetime, timezone
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
            row = (await self.user_dao.get_by(mode="AND", email=email))[0]
        elif id:
            row = (await self.user_dao.get_by(mode="AND", id=id))[0]
        else:
            raise HTTPException(400, 'incorrect using get_user_by')
        goal_value = row[5][row[5].index('#') + 1:]
        user = User(balance=row[1],
                    username=row[2],
                    email=row[3],
                    goal_name=row[5][:row[5].index('#')],
                    goal_value= int(goal_value) if goal_value else 0,  # доделать страницу отображения пользователя
                    created_at=row[6])
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
        users = await self.user_dao.get_by(mode="AND", email=email)
        if len(users) == 0:
            raise HTTPException(404, "Пользователь не найден")
        user = users[0]
        print(user)
        if not verify_password(password, user[4]):
            raise HTTPException(400, "Неправильный пароль")
        else:
            access_token = create_token(user[0])
            return access_token
