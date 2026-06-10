from datetime import date
from io import BytesIO

from openpyxl import Workbook
from sqlalchemy.exc import NoResultFound

from app.api.schemas import Category, ExportFilter, User
from app.utils import create_token, get_password_hash, verify_password
from app.utils.logger import get_logger
from app.utils.uow import IUnitOfWork

log = get_logger(__name__)


class UserService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_user(self, username: str, email: str, password: str) -> None:
        try:
            async with self.uow:
                log.debug("'add_user' is running")
                await self.uow.users.add_user(username=username, email=email, password=get_password_hash(password))
                log.debug("user %s successfully added", email)
        except ValueError as err:
            if "Почта неуникальна" in str(err):
                log.warning("someone tried to register with %s email", email)
                raise Exception("Эта почта уже занята") from None
            log.exception("Exception in add_user", exc_info=False)
            raise err

    async def get_user_by(self, **kwargs) -> User:
        try:
            async with self.uow:
                res = await self.uow.users.get_one(**kwargs)
                return User.model_validate(res)
        except Exception as err:
            msg = str(err)
            params = ", ".join(f"{i}={kwargs[i]}" for i in kwargs.keys())
            if "Пользователь" in msg and "не найден" in msg:
                log.warning("User with %s not found", params)
                raise Exception("Пользователь не найден") from None
            log.exception("Exception in get_user_by, %s", params, exc_info=False)
            raise

    async def delete_user(self, id: int) -> None:
        try:
            async with self.uow:
                await self.uow.users.delete_by_user(id)
        except Exception as err:
            msg = str(err)
            if "Пользователь" in msg and "не найден" in msg:
                log.warning("User with id=%s not found", id)
                raise Exception("Пользователь не найден") from None
            log.exception("Exception in delete_user with id=%s", id, exc_info=False)
            raise

    async def update_user(self, id: int, **kwargs) -> None:
        try:
            async with self.uow:
                await self.uow.users.update_user(id, **kwargs)
        except ValueError as err:
            if str(err) == "email is already used":
                raise Exception("Введите другую почту") from None
        except Exception:
            params = ", ".join(f"{i}={kwargs[i]}" for i in kwargs.keys())
            log.exception("Exception in update_user with id=%s and %s", id, params, exc_info=False)
            raise

    async def login(self, email: str, password: str) -> str:
        try:
            async with self.uow:
                user = await self.uow.users.get_one(email=email)
                if not verify_password(password, user.password):
                    raise Exception("Неправильный пароль") from None
                else:
                    access_token = create_token(user.id)
                    return access_token
        except NoResultFound:
            raise Exception("Пользователь не найден") from None
        except Exception as err:
            msg = str(err)
            if "Неправильный пароль" == msg:
                raise
            log.exception("Exception in login with email=%s", email, exc_info=False)
            raise

    async def get_sum_of_costs_and_earn(self, user_id: int):
        async with self.uow:
            earnings, costs = await self.uow.users.get_user_costs_and_earnings(user_id)
            return earnings, costs

    async def get_sum_of_costs_and_earn_in_limit(
        self,
        user_id: int,
        period: tuple[date, date],
        categories: list[Category],
    ):
        try:
            async with self.uow:
                sum_costs = 0
                for i in categories:
                    costs = await self.uow.users.get_costs_in_limit(user_id, period, i.id)
                    sum_costs += costs if costs else 0
                return sum_costs
        except Exception as err:
            if str(err) == "У пользователя нет трат за этот период":
                raise
            log.exception(
                "Exception in get_sum_of_costs_and_earn_in_limit user_id=%s, period=%s",
                user_id,
                period,
                exc_info=False,
            )
            raise

    async def export_to_excel(self, user_id: int, filters: ExportFilter | None = None):
        try:
            async with self.uow:
                buffer = BytesIO()
                table = Workbook()
                ws = table.active
                ws.append(["№", "Дата", "Время", "Тип операции", "Сумма", "Категория", "Комментарий"])

                filter_kwargs = {"user_id": user_id}
                if filters:
                    if filters.operation_type != "all":
                        filter_kwargs["operation_type"] = int(filters.operation_type == "expense")
                log.debug("%s, %s, %s", user_id, filter_kwargs, filters)
                db_records = (await self.uow.records.get_list_by(**filter_kwargs)).all()

                for idx, el in enumerate(db_records):
                    if filters:
                        if filters.categories:
                            cat_name = el.category.name if el.category else "none"
                            if cat_name not in filters.categories:
                                continue
                    ws.append(
                        [
                            idx + 1,
                            el.created_at.date().strftime("%d.%m.%Y"),
                            el.created_at.time().strftime("%H:%M"),
                            "Расход" if el.operation_type else "Доход",
                            el.value,
                            el.category.name if el.category else None,
                            el.comment,
                        ],
                    )
                table.save(buffer)
                buffer.seek(0)
                return buffer
        except NoResultFound:
            raise Exception("У пользователя нет записей") from None
        except Exception:
            log.exception("Exception in export_to_excel user_id=%s, filters=%s", user_id, filters, exc_info=False)
            raise
