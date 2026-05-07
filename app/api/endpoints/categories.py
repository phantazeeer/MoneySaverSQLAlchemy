from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Body

from app.services import CategoryService
from app.utils import get_jwt_payload
from app.utils.dependencies import get_categories_service as get_service
from app.utils.logger import get_logger

router = APIRouter(prefix="/categories", tags=["Working with categories"])
log = get_logger(__name__)


@router.post("/", status_code=201)
async def create_category(
    name: Annotated[str, Body()],
    user_id: Annotated[int, Depends(get_jwt_payload)],
    service: Annotated[CategoryService, Depends(get_service)],
):
    try:
        await service.add_category(name=name, user_id=user_id)
        return "OK"
    except ValueError as err:
        if str(err) == "Категория с таким именем уже существует":
            raise HTTPException(400, "Категория с таким именем уже существует") from None
        else:
            raise err


@router.get("/{category}")
async def get_category_by(
    category: int | str,
    user_id: Annotated[int, Depends(get_jwt_payload)],
    service: Annotated[CategoryService, Depends(get_service)],
):
    if category.isdigit():
        category = int(category)
    return await service.get_categories_by(category=category, user_id=user_id)


@router.delete("/{category}")
async def delete_category(
    category: int | str,
    user_id: Annotated[int, Depends(get_jwt_payload)],
    service: Annotated[CategoryService, Depends(get_service)],
):
    if category.isdigit():
        category = int(category)
    try:
        return await service.delete_category(category_id=category, user_id=user_id)
    except ValueError as err:
        if str(err) == "Запись не найдена":
            raise HTTPException(400, "Запись не найдена") from None
        else:
            raise err
