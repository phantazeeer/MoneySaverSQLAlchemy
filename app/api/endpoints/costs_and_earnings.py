from typing import Annotated

from fastapi import APIRouter, Depends, status, Form, Query

from app.services import CostsAndEarningsService as CEService
from app.utils import get_jwt_payload
from app.api.schemas import AddRecord, ChangeRecord, Record
from app.db.DAO import SQLiteUserDAO, SQLiteCostsAndEarningsDAO as SQLiteCEDAO

router = APIRouter(prefix='/records', tags=['Working with records'])


async def get_service() -> CEService:
    service = CEService()
    await service.init_session(SQLiteUserDAO(), SQLiteCEDAO())
    return service


@router.post('/add_record', status_code=status.HTTP_201_CREATED, deprecated=True)
async def add_record(record: Annotated[AddRecord, Form()], user_id: int = Depends(get_jwt_payload),
                     service: CEService = Depends(get_service)) -> str:
    await service.add_record(user_id, **(record.model_dump()))
    return "OK"


@router.get('/get_user_records', deprecated=True)
async def get_user_records(user_id: int = Depends(get_jwt_payload),
                           service: CEService = Depends(get_service)) -> list[Record]:
    return await service.get_records_by(user_id=user_id)


@router.get('/record_by_id', deprecated=True)
async def get_record_by_id(id: int, user_id: int = Depends(get_jwt_payload),
                           service: CEService = Depends(get_service)) -> Record:
    return await service.get_records_by(id=id, user_id=user_id)


@router.delete('/delete_record_by_id', deprecated=True)
async def delete_record(id: int, user_id: int = Depends(get_jwt_payload),
                        service: CEService = Depends(get_service)) -> str:
    await service.delete_record(id=id, user_id=user_id)
    return "OK"


@router.put('/update_record', deprecated=True)
async def update_record(changes: Annotated[ChangeRecord, Form()], user_id: int = Depends(get_jwt_payload),
                        service: CEService = Depends(get_service)) -> str:
    await service.update_record(changes.id, user_id, int(changes.operation_type), changes.value, changes.comment)
    return "OK"


@router.post('/', status_code=status.HTTP_201_CREATED)
async def add(record: Annotated[AddRecord, Form()], user_id: int = Depends(get_jwt_payload),
              service: CEService = Depends(get_service)) -> str:
    return await add_record(record=record, user_id=user_id, service=service)


@router.get('/')
async def get(id: Annotated[int, Query()], user_id: int = Depends(get_jwt_payload),
              service: CEService = Depends(get_service)) -> Record:
    return await get_record_by_id(id, user_id, service)

@router.put('/')
async def update(changes: Annotated[ChangeRecord, Form()], user_id: int = Depends(get_jwt_payload),
                        service: CEService = Depends(get_service)) -> str:
    return await update_record(changes=changes, user_id=user_id, service=service)

@router.delete('/')
async def delete(id: int, user_id: int = Depends(get_jwt_payload),
                        service: CEService = Depends(get_service)) -> str:
    return await delete_record(id=id, user_id=user_id, service=service)