from app.api.schemas import Limit
from app.utils.logger import get_logger
from app.utils.uow import IUnitOfWork

log = get_logger(__name__)


class LimitService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_limit(self, user_id: int) -> Limit:
        try:
            async with self.uow:
                limit = await self.uow.limits.get_one(user_id=user_id)
                return Limit.model_validate(limit)
        except Exception as err:
            if str(err) == "У пользователя нет лимита":
                raise Exception("У пользователя нет лимита") from None
            else:
                log.exception("Exception in get_limit with user_id=%s", user_id, exc_info=False)
                raise

    async def delete_limit(self, user_id: int):
        try:
            async with self.uow:
                await self.uow.limits.delete_by_user(user_id)
        except Exception as err:
            if str(err) == "У пользователя нет лимита":
                raise err from None
            else:
                log.exception("Exception in delete_limit with user_id=%s", user_id, exc_info=False)
                raise

    async def update_limit(self, user_id: int, period: str, value: int):
        async with self.uow:
            try:
                if period not in ("day", "week", "month"):
                    raise ValueError("Период должен быть день, неделя или месяц")
                await self.uow.limits.update_limit(user_id, period, value)
            except Exception as err:
                if str(err) == "У пользователя нет лимита":
                    await self.uow.limits.add_one(user_id=user_id, period=period, value=value)
                if isinstance(err, ValueError) and str(err) == "Период должен быть день, неделя или месяц":
                    raise err
                else:
                    log.exception("Exception in update_limit with "
                                  "user_id=%s, period=%s, value=%s", user_id, period, value, exc_info=False)
                    raise
