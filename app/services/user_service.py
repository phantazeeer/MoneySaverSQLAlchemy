from app.utils import get_password_hash, verify_password, create_token
from app.api.schemas import User
from sqlalchemy.exc import NoResultFound, IntegrityError
from app.utils.uow import IUnitOfWork


class UserService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_user(self, username: str, email: str, password: str) -> None:
        try:
            async with self.uow:
                await self.uow.users.add_user(username=username, email=email, password=get_password_hash(password))
        except ValueError as err:
            if "Почта неуникальна" in str(err):
                raise Exception("Эта почта уже занята")
            raise err

    async def get_user_by(self, **kwargs) -> User:
        try:
            async with self.uow:
                res = await self.uow.users.get_one(**kwargs)
                return User.model_validate(res)
        except Exception as err:
            raise err


    async def delete_user(self, id: int) -> None:
        async with self.uow:
            await self.uow.users.delete_by_user(id)


    async def update_user(self, id: int, **kwargs) -> None:
        try:
            async with self.uow:
                await self.uow.users.update_user(id, **kwargs)
        except IntegrityError as err:
            if "user.email" in str(err):
                raise Exception("Введите другую почту")

    async def login(self, email: str, password: str) -> str:
        async with self.uow:
            try:
                user = await self.uow.users.get_one(email=email)
            except NoResultFound:
                raise Exception("Пользователь не найден")
            if not verify_password(password, user.password):
                raise Exception("Неправильный пароль")
            else:
                access_token = create_token(user.id)
                return access_token
