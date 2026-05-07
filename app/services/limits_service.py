from app.api.schemas import Limit
from app.utils.uow import IUnitOfWork
from app.utils.logger import get_logger

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
                log.exception("Exception in LimitService.get_limit", exc_info=False)
                raise

    async def delete_limit(self, user_id: int):
        try:
            async with self.uow:
                await self.uow.limits.delete_by_user(user_id)
        except Exception as err:
            if str(err) == "У пользователя нет лимита":
                raise err from None
            else:
                log.exception("Exception in LimitService.delete_limit", exc_info=False)
                raise

    async def update_limit(self, user_id: int, period: str, value: int):
        async with self.uow:
            try:
                if not period in ("day", "week", "month"):
                    raise ValueError("Период должен быть день, неделя или месяц")
                await self.uow.limits.update_limit(user_id, period, value)
            except Exception as err:
                if str(err) == "У пользователя нет лимита":
                    await self.uow.limits.add_one(user_id=user_id, period=period, value=value)
                else:
                    log.exception("Exception in LimitService.update_limit", exc_info=False)
                    raise
