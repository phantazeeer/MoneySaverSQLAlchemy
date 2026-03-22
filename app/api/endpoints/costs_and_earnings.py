from typing import Annotated

from fastapi import APIRouter, Depends, status, Form, Path, HTTPException

from app.services import CostsAndEarningsService as CEService
from app.utils import get_jwt_payload
from app.api.schemas import AddRecord, ChangeRecord, Record
from app.utils.uow import UnitOfWork, IUnitOfWork

router = APIRouter(prefix='/records', tags=['Working with records'])


async def get_service(uow: IUnitOfWork = Depends(UnitOfWork)) -> CEService:
    service = CEService(uow)
    return service


@router.post('/', status_code=status.HTTP_201_CREATED)
async def add(record: Annotated[AddRecord, Form()], user_id: int = Depends(get_jwt_payload),
              service: CEService = Depends(get_service)) -> str:
    await service.add_record(user_id, **(record.model_dump()))
    return "OK"


@router.get('/{id}')
async def get(id: Annotated[int, Path()], user_id: int = Depends(get_jwt_payload),
              service: CEService = Depends(get_service)) -> Record:
    try:
        return await service.get_records_by(id=id, user_id=user_id)
    except ValueError as err:
        if str(err) == "Пользователь не является владельцем записи":
            raise HTTPException(403, "Пользователь не является владельцем записи")
    except Exception as err:
        if str(err) == "Запись не найдена":
            raise HTTPException(404, "Запись не найдена")


@router.put('/{id}')
async def update(id: Annotated[int, Path()], changes: Annotated[ChangeRecord, Form()],
                 user_id: int = Depends(get_jwt_payload),
                 service: CEService = Depends(get_service)) -> str:
    try:
        await service.update_record(id, user_id, int(changes.operation_type), changes.value, changes.comment)
        return "OK"
    except ValueError as err:
        if str(err) == "Пользователь не является владельцем записи":
            raise HTTPException(403, "Пользователь не является владельцем записи")
    except Exception as err:
        if str(err) == "Запись не найдена":
            raise HTTPException(404, "Запись не найдена")


@router.delete('/{id}')
async def delete(id: int, user_id: int = Depends(get_jwt_payload),
                 service: CEService = Depends(get_service)) -> str:
    try:
        await service.delete_record(id=id, user_id=user_id)
        return "OK"
    except ValueError as err:
        if str(err) == "Пользователь не является владельцем записи":
            raise HTTPException(403, "Пользователь не является владельцем записи")
    except Exception as err:
        if str(err) == "Запись не найдена":
            raise HTTPException(404, "Запись не найдена")
