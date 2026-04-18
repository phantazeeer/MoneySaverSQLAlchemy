from app.utils.uow import UnitOfWork
from app.db.database import get_async_session
from fastapi import Depends
from app.services.user_service import UserService
from app.services.costs_and_earnings_service import CostsAndEarningsService


def get_sqlalchemy_session():
    return get_async_session()


def get_user_service(_session_maker=Depends(get_sqlalchemy_session)) -> UserService:
    return UserService(UnitOfWork(_session_maker))


def get_ce_service(_session_maker=Depends(get_sqlalchemy_session)):
    return CostsAndEarningsService(UnitOfWork(_session_maker))
