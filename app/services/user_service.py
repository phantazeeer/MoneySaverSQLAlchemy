from app.db.database import get_session
from app.utils import get_password_hash, verify_password, create_token
from datetime import datetime, timezone
from fastapi import HTTPException


class UserService:
    async def init_session(self):
        self.conn = await get_session()

    async def add_user(self, username: str, email: str, password: str):
        await self.conn.execute("""INSERT INTO user (username, email, password, created_at) VALUES (?, ?, ?, ?);""",
                                (username, email, get_password_hash(password), datetime.now(timezone.utc)))
        await self.conn.commit()

    async def get_user_by(self, email: str | None = None, id: int | None = None):
        if email:
            cursor = await self.conn.execute("""SELECT balance, username, email, goal, created_at FROM user WHERE email = ?""", (email,))
        elif id:
            cursor = await self.conn.execute("""SELECT balance, username, email, goal, created_at FROM user WHERE id = ?""", (id,))
        else:
            raise Exception('incorrect using get_user_by')
        res = await cursor.fetchone()
        return res

    async def delete_user(self, id: int):
        await self.conn.execute("""DELETE FROM user WHERE id = ?""", (id,))
        await self.conn.commit()

    async def update_goal(self, id: int, goal: str):
        await self.conn.execute("""UPDATE user SET goal = ? WHERE id = ?""", (goal, id))
        await self.conn.commit()


    async def login(self, email: str, password: str) -> str:
        user = await (await self.conn.execute("""SELECT * FROM user WHERE email = ?""", (email,))).fetchone()
        if not user:
            raise HTTPException(404, "Пользователь не найден")
        if not verify_password(password, user[4]):
            raise HTTPException(400, "Неправильный пароль")
        else:
            access_token = create_token(user[0])
            return access_token