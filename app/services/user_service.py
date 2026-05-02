from sqlalchemy.exc import NoResultFound

from app.api.schemas import User
from app.utils import create_token, get_password_hash, verify_password
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
                raise Exception("Эта почта уже занята") from None
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
        except ValueError as err:
            if str(err) == "email is already used":
                raise Exception("Введите другую почту") from None

    async def login(self, email: str, password: str) -> str:
        async with self.uow:
            try:
                user = await self.uow.users.get_one(email=email)
            except NoResultFound:
                raise Exception("Пользователь не найден") from None
            if not verify_password(password, user.password):
                raise Exception("Неправильный пароль") from None
            else:
                access_token = create_token(user.id)
                return access_token

    async def get_sum_of_costs_and_earn(self, user_id: int):
        async with self.uow:
            earnings, costs = await self.uow.users.get_user_costs_and_earnings(user_id)
            return earnings, costs
