from fastapi import APIRouter, Depends, status, Response, HTTPException

from app.api.schemas import UserLogin, UserChange
from app.services import UserService
from app.api.schemas import UserRegister
from app.utils import get_jwt_payload

router = APIRouter(prefix='/user', tags=['Working with user'])


async def get_service():
    service = UserService()
    await service.init_session()
    return service


@router.post('/me')
async def me(user_id: int = Depends(get_jwt_payload), service: UserService = Depends(get_service)):
    res = await service.get_user_by(id=user_id)
    return res


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(create: UserRegister, service: UserService = Depends(get_service)):
    await service.add_user(create.username, str(create.email), create.password)


@router.post('/login')
async def login(user: UserLogin, service: UserService = Depends(get_service)):
    token = await service.login(str(user.email), user.password)
    res = Response("OK", status_code=200)
    res.set_cookie('Authorization', token, httponly=True)
    return res


@router.post('/logout')
async def logout():
    res = Response("OK", status_code=200)
    res.delete_cookie('Authorization')
    return res


@router.put('/change_user')
async def change_user(changes: UserChange, user_id: int = Depends(get_jwt_payload),
                      service: UserService = Depends(get_service)):
    changes = changes.model_dump()

    if "goal_name" in changes.keys() and "goal_value" in changes.keys():
        changes["goal"] = changes.pop("goal_name") + "#" + str(changes.pop("goal_value"))
    elif "goal_name" in changes.keys():
        changes.pop("goal_name")
    elif "goal_value" in changes.keys():
        changes.pop("goal_value")
    if len(changes.keys()) == 0:
        raise HTTPException(400, "Пустой запрос")

    await service.update_user(user_id, **changes)
    return "OK"
