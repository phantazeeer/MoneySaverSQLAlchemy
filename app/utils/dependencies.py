from app.utils.uow import UnitOfWork
from app.db.database import session_factory
from fastapi import Depends
from app.services.user_service import UserService
from app.services.costs_and_earnings_service import CostsAndEarningsService

def get_sqlalchemy_session():
    return session_factory

def get_uow(sess_maker=Depends(get_sqlalchemy_session)):
    return UnitOfWork(sess_maker)


def get_user_service(uow=Depends(get_uow)) -> UserService:
    return UserService(uow)


def get_ce_service(uow=Depends(get_uow)) -> CostsAndEarningsService:
    return CostsAndEarningsService(uow)
