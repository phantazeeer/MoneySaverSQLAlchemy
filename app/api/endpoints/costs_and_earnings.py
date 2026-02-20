from fastapi import APIRouter, Depends, status

from app.services import CostsAndEarningsService

router = APIRouter(prefix='/records', tags=['Working with records'])

async def get_service():
    service = CostsAndEarningsService()
    await service.init_session()
    return service
