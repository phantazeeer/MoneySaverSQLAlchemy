from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException

from app.api.schemas import ChangeLimit, Limit
from app.services.limits_service import LimitService
from app.utils import get_jwt_payload
from app.utils.dependencies import get_limit_service as get_service
from app.utils.logger import get_logger

router = APIRouter(prefix="/limits", tags=["Working with limits"])
log = get_logger(__name__)


@router.get("/")
async def get_user_limit(
    user_id: Annotated[int, Depends(get_jwt_payload)],
    service: Annotated[LimitService, Depends(get_service)],
) -> Limit | None:
    try:
        res = await service.get_limit(user_id)
        return res
    except Exception as err:
        if str(err) == "У пользователя нет лимита":
            raise HTTPException(400, "У пользователя нет лимита") from None
        else:
            raise


@router.put("/")
async def create_user_limit(
    limit: Annotated[ChangeLimit, Form()],
    user_id: Annotated[int, Depends(get_jwt_payload)],
    service: Annotated[LimitService, Depends(get_service)],
):
    try:
        await service.update_limit(user_id, limit.period, limit.value)
        return {"detail": "ok"}
    except Exception:
        raise


@router.delete("/")
async def delete_user_limit(
    user_id: Annotated[int, Depends(get_jwt_payload)],
    service: Annotated[LimitService, Depends(get_service)],
):
    try:
        await service.delete_limit(user_id)
    except Exception as err:
        if str(err) == "У пользователя нет лимита":
            raise HTTPException(400, "У пользователя нет лимита") from None
        else:
            raise
