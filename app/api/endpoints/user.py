from fastapi import APIRouter, Depends, status

from app.services import UserService
from app.api.schemas import UserRegister

router = APIRouter(prefix='/user', tags=['Working with user'])

async def get_service():
    service = UserService()
    await service.init_session()
    return service


@router.post('/test')
async def test(service: UserService = Depends(get_service)):
    user = await service.get_user_by(id=1)
    return user

@router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister, service: UserService = Depends(get_service)):
    await service.add_user(user.username, str(user.email), user.password)

