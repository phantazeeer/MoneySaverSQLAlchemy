from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Path

from app.api.schemas import CreateLimit, Limit
from app.services.limits_service import LimitService
from app.utils import get_jwt_payload
from app.utils.dependencies import get_limit_service as get_service
from app.utils.logger import get_logger

router = APIRouter(prefix="/limits", tags=["Working with limits"])
log = get_logger(__name__)


@router.get("/{id}")
async def get_user_limit(
    limit_id: Annotated[int, Path()],
    user_id: Annotated[int, Depends(get_jwt_payload)],
    service: Annotated[LimitService, Depends(get_service)],
) -> Limit | None:
    try:
        res = await service.get_limit(user_id, id=limit_id)
        return res
    except Exception as err:
        if str(err) == "У пользователя нет лимита":
            raise HTTPException(400, "У пользователя нет лимита") from None
        else:
            raise


@router.post("/", status_code=201)
async def create_user_limit(
    limit: Annotated[CreateLimit, Form()],
    user_id: Annotated[int, Depends(get_jwt_payload)],
    service: Annotated[LimitService, Depends(get_service)],
):
    try:
        await service.create_limit(user_id, limit)
        return {"detail": "ok"}
    except Exception:
        raise


@router.delete("/{id}")
async def delete_user_limit(
    limit_id: Annotated[int, Path()],
    user_id: Annotated[int, Depends(get_jwt_payload)],
    service: Annotated[LimitService, Depends(get_service)],
):
    try:
        await service.delete_limit_by_id(user_id, limit_id)
    except Exception as err:
        if str(err) == "Такого лимита не существует":
            raise HTTPException(400, "Такого лимита не существует") from None
        else:
            raise
