from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Response, status

from app.api.endpoints.costs_and_earnings import CEService, Record
from app.api.endpoints.costs_and_earnings import get_service as get_ce_service
from app.api.schemas import User, UserChange, UserLogin, UserRegister
from app.services import CategoryService, UserService
from app.utils import get_jwt_payload
from app.utils.dependencies import get_categories_service
from app.utils.dependencies import get_user_service as get_service

router = APIRouter(prefix="/user", tags=["Working with user"])


@router.get("/me")
async def me(
    user_id: Annotated[int, Depends(get_jwt_payload)],
    service: Annotated[UserService, Depends(get_service)],
) -> User:
    try:
        res = await service.get_user_by(id=user_id)
        return res
    except Exception as err:
        if str(err) == "Пользователь не найден":
            raise HTTPException(400, "Пользователь не найден") from None
        raise


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    create: Annotated[UserRegister, Form()],
    service: Annotated[UserService, Depends(get_service)],
) -> None:
    try:
        await service.add_user(create.username, str(create.email), create.password)
    except Exception as err:
        if str(err) == "Эта почта уже занята":
            raise HTTPException(400, str(err)) from None
        raise err


@router.post("/login", status_code=status.HTTP_200_OK, response_model=None)
async def login(user: Annotated[UserLogin, Form()], service: Annotated[UserService, Depends(get_service)]) -> Response:
    try:
        token = await service.login(str(user.email), user.password)
    except Exception as err:
        if str(err) == "Пользователь не найден":
            raise HTTPException(400, "Пользователь не найден") from None
        if str(err) == "Неправильный пароль":
            raise HTTPException(400, "Неправильный пароль") from None
        raise err
    res = Response("OK", status_code=200)
    res.set_cookie("Authorization", token, httponly=True)
    return res


@router.get("/logout", status_code=status.HTTP_200_OK, response_model=None)
async def logout() -> Response:
    res = Response("OK", status_code=200)
    res.delete_cookie("Authorization")
    return res


@router.put("/me", status_code=status.HTTP_200_OK)
async def change_me(
    changes: Annotated[UserChange, Form()],
    user_id: Annotated[int, Depends(get_jwt_payload)],
    service: Annotated[UserService, Depends(get_service)],
) -> str:
    changes = changes.model_dump()
    if len(changes.keys()) == 0:
        raise HTTPException(400, "Пустой запрос")
    try:
        await service.update_user(user_id, **changes)
        return "OK"
    except Exception as err:
        if str(err) == "Введите другую почту":
            raise HTTPException(400, "Введите другую почту") from None
        raise err


@router.get("/me/records")
async def get_records(
    user_id: Annotated[int, Depends(get_jwt_payload)],
    service: Annotated[CEService, Depends(get_ce_service)],
) -> list[Record]:
    try:
        return await service.get_records_by(user_id=user_id)
    except ValueError as err:
        if str(err) == "Пользователь не является владельцем записи":
            raise HTTPException(403, "Пользователь не является владельцем записи") from None
    except Exception as err:
        if str(err) == "Записи не найдены":
            raise HTTPException(404, "Записи не найдены") from None


@router.get("/me/categories")
async def get_categories(
    user_id: Annotated[int, Depends(get_jwt_payload)],
    service: Annotated[CategoryService, Depends(get_categories_service)],
):
    return await service.get_user_categories(user_id)
