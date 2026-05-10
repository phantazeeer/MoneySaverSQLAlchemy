from datetime import datetime, time, timedelta, timezone

from app.api.schemas import CreateLimit, Limit
from app.utils.logger import get_logger
from app.utils.uow import IUnitOfWork

log = get_logger(__name__)


class LimitService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    @staticmethod
    def update_start_end_limit(limit, now: datetime):
        if limit.period is not None:
            if limit.end < now:
                start = datetime.combine(now - timedelta(days=now.weekday()), time(second=0))
                limit.end = datetime.combine(start + timedelta(days=6), time(hour=23, minute=59, second=59))
                limit.start = start

    async def get_limit(self, user_id: int, **kwargs) -> Limit:
        try:
            async with self.uow:
                now = datetime.now(timezone.utc)
                limit = await self.uow.limits.get_one(user_id, **kwargs)
                self.update_start_end_limit(limit, now)
                await self.uow.session.commit()
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
                now = datetime.now(timezone.utc)
                limits = await self.uow.limits.get_list_by(user_id, **kwargs)
                for limit in limits:
                    self.update_start_end_limit(limit, now)
                await self.uow.session.commit()
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
                log.debug("Deleted limits with id: %s", "; ".join(deleted))
        except Exception as err:
            if str(err) == "У пользователя нет лимитов":
                raise err from None
            else:
                log.exception("Exception in delete_all_user_limits with user_id=%s", user_id, exc_info=False)
                raise

    async def delete_limit_by_id(self, user_id: int, limit_id: int):
        try:
            async with self.uow:
                log.debug("Deleting user_id's=%s limit with id=%s", user_id, limit_id)
                limit = await self.uow.limits.get_one(user_id, id=limit_id)
                await self.uow.session.delete(limit)
        except Exception as err:
            if str(err) == "Такого лимита не существует":
                raise
            log.exception("Exception in delete_limit_by_id with user_id=%s, limit_id=%s",
                          user_id, limit_id, exc_info=False)
            raise

    async def create_limit(self, user_id: int, limit: CreateLimit):
        async with self.uow:
            try:
                if limit.period not in ("day", "week", "month", None):
                    raise ValueError("Период должен быть день, неделя или месяц")
                await self.uow.limits.add_one(
                    name=limit.name,
                    user_id=user_id,
                    period=limit.period,
                    value=limit.value,
                    start=limit.start,
                    end=limit.end,
                )
            except Exception as err:
                if isinstance(err, ValueError) and str(err) == "Период должен быть день, неделя или месяц":
                    raise err
                else:
                    log.exception("Exception in create_limit with CreateLimit=%s", limit, exc_info=False)
                    raise
