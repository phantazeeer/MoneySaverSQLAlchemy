from typing import Annotated

from fastapi import APIRouter, Depends, status, Response, HTTPException, Form

from app.api.schemas import UserLogin, UserChange, User
from app.services import UserService
from app.api.schemas import UserRegister
from app.utils import get_jwt_payload
from app.db.DAO import SQLiteUserDAO
from app.api.endpoints.costs_and_earnings import get_service as get_ce_service, CEService, Record

router = APIRouter(prefix='/user', tags=['Working with user'])


async def get_service():
    service = UserService()
    await service.init_session(SQLiteUserDAO())
    return service


@router.get('/me')
async def me(user_id: int = Depends(get_jwt_payload), service: UserService = Depends(get_service)) -> User:
    res = await service.get_user_by(id=user_id)
    return res


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(create: Annotated[UserRegister, Form()], service: UserService = Depends(get_service)) -> None:
    await service.add_user(create.username, str(create.email), create.password)


@router.post('/login', status_code=status.HTTP_200_OK, response_model=None)
async def login(user: Annotated[UserLogin, Form()], service: UserService = Depends(get_service)) -> Response:
    token = await service.login(str(user.email), user.password)
    res = Response("OK", status_code=200)
    res.set_cookie('Authorization', token, httponly=True)
    return res


@router.get('/logout', status_code=status.HTTP_200_OK, response_model=None)
async def logout() -> Response:
    res = Response("OK", status_code=200)
    res.delete_cookie('Authorization')
    return res


@router.put('/change_user', status_code=status.HTTP_200_OK, deprecated=True)
async def change_user(changes: Annotated[UserChange, Form()], user_id: int = Depends(get_jwt_payload),
                      service: UserService = Depends(get_service)) -> str:
    changes = changes.model_dump()
    if len(changes.keys()) == 0:
        raise HTTPException(400, "Пустой запрос")

    await service.update_user(user_id, **changes)
    return "OK"

@router.put('/me', status_code=status.HTTP_200_OK)
async def change_me(changes: Annotated[UserChange, Form()], user_id: int = Depends(get_jwt_payload),
                      service: UserService = Depends(get_service)) -> str:
    res = await change_user(changes=changes, user_id=user_id, service=service)
    return res

@router.get('/me/records')
async def get_records(user_id: int = Depends(get_jwt_payload),
                           service: CEService = Depends(get_ce_service)) -> list[Record]:
    return await service.get_records_by(user_id=user_id)
