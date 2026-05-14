import calendar
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.exc import NoResultFound

from app.api.schemas import CreateLimit, Limit
from app.utils.logger import get_logger
from app.utils.uow import IUnitOfWork

log = get_logger(__name__)


class LimitService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    @staticmethod
    def update_start_end_limit(limit, now: date):
        if limit.period is not None:
            if limit.end <= now and limit.period == "month":
                previous_month = calendar.monthrange(now.year, (now.month - 1))[1]
                this_month = calendar.monthrange(now.year, now.month)[1]
                limit.start += timedelta(days=previous_month)
                limit.end += timedelta(days=this_month)
            if limit.end <= now and limit.period == "week":
                start = now - timedelta(days=now.weekday())
                limit.end = start + timedelta(days=7)
                limit.start = start
            elif limit.end <= now and limit.period == "day":
                limit.end = now + timedelta(days=1)
                limit.start = now

    async def get_limit(self, user_id: int, **kwargs) -> Limit:
        try:
            async with self.uow:
                now = datetime.now(timezone.utc)
                limit = await self.uow.limits.get_one(user_id, **kwargs)
                self.update_start_end_limit(limit, now)
                return Limit.get_from_orm(limit)
        except Exception as err:
            if str(err) == "У пользователя нет лимита":
                raise Exception("У пользователя нет лимита") from None
            else:
                params = ", ".join(f"{i}={kwargs[i]}" for i in kwargs.keys())
                log.exception("Exception in get_limit with user_id=%s, %s", user_id, params, exc_info=False)
                raise

    async def get_list_of_limits(self, user_id: int, **kwargs) -> list[Limit]:
        try:
            async with self.uow:
                now = datetime.now(timezone.utc).date()
                limits = await self.uow.limits.get_list_by(user_id, **kwargs)
                for limit in limits:
                    self.update_start_end_limit(limit, now)
                return [Limit.get_from_orm(limit) for limit in limits]
        except Exception as err:
            if str(err) == "У пользователя нет лимитов":
                raise Exception("У пользователя нет лимитов") from None
            else:
                params = ", ".join(f"{i}={kwargs[i]}" for i in kwargs.keys())
                log.exception("Exception in get_list_of_limits with user_id=%s, %s", user_id, params, exc_info=False)
                raise

    async def delete_all_user_limits(self, user_id: int):
        try:
            async with self.uow:
                log.debug("Deleting user_id's=%s limits", user_id)
                deleted = await self.uow.limits.delete_by_user(user_id)
                log.debug("Deleted limits with id: %s", "; ".join([str(i) for i in deleted]))
        except Exception as err:
            if str(err) == "У пользователя нет лимитов":
                raise err from None
            else:
                log.exception("Exception in delete_all_user_limits with user_id=%s", user_id, exc_info=False)
                raise

    async def delete_limit_by_id(self, user_id: int, limit: int | str):
        try:
            async with self.uow:
                log.debug("Deleting user_id's=%s limit with id=%s", user_id, limit)
                if isinstance(limit, int) or limit.isnumeric():
                    try:
                        limit = await self.uow.limits.get_one(user_id, id=int(limit)) # проверка, что такая запись вообще есть
                        await self.uow.limits.delete_by_id(id=int(limit))
                    except Exception as err:
                        if str(err) == "У пользователя нет этого лимита":
                            limit = await self.uow.limits.delete_by_name_and_user(user_id, name=limit)
                        else:
                            raise
                elif isinstance(limit, str):
                    limit = await self.uow.limits.delete_by_name_and_user(user_id, name=limit)
                else:
                    raise ValueError("Limit should be int or str")
        except Exception as err:
            if str(err) == "Такого лимита не существует":
                raise
            log.exception("Exception in delete_limit_by_id with user_id=%s, limit=%s", user_id, limit, exc_info=False)
            raise

    async def create_limit(self, user_id: int, limit: CreateLimit):
        async with self.uow:
            try:
                if limit.period not in ("day", "week", "month", "once", None):
                    raise ValueError("Период должен быть день, неделя или месяц")
                period = limit.period if limit.period in ("day", "week", "month") else None
                categories = []
                for name in limit.categories:
                    try:
                        category = await self.uow.categories.get_one(user_id=user_id, name=name)
                        categories.append(category.id)
                    except NoResultFound:
                        raise Exception("У пользователя нет этой категории") from None
                await self.uow.limits.add_one(
                    name=limit.name,
                    user_id=user_id,
                    period=period,
                    value=limit.value,
                    start=limit.start,
                    end=limit.end,
                    categories=categories,
                )

            except Exception as err:
                if isinstance(err, ValueError) and str(err) == "Период должен быть день, неделя или месяц":
                    raise err
                else:
                    log.exception("Exception in create_limit with CreateLimit=%s", limit, exc_info=False)
                    raise
