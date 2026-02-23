from typing import Annotated, Literal
from types import NoneType

from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services import CostsAndEarningsService as CEService
from app.services import UserService
from app.utils import get_jwt_payload
from app.forms import FastAddRecordForm, LoginForm, RegisterForm, ChangeRecordForm

router = APIRouter(tags=['Working with templates'])

templates = Jinja2Templates(directory="app/templates")


async def get_ce_service() -> CEService:
    service = CEService()
    await service.init_session()
    return service


async def get_user_service() -> UserService:
    service = UserService()
    await service.init_session()
    return service


@router.get("/", name="main_page")
async def main(req: Request, user_id: Annotated[int, Depends(get_jwt_payload)],
               ce_service: CEService = Depends(get_ce_service),
               filter_by: Annotated[Literal["costs", "earnings"], Query()] | None = None,
               user_service: UserService = Depends(get_user_service)):
    print(user_id)
    if not isinstance(filter_by, NoneType):
        records = await ce_service.user_costs_or_earnings(user_id=user_id, filter=filter_by)
    else:
        records = await ce_service.get_records_by(user_id=user_id)
    user = await user_service.get_user_by(id=user_id)

    return templates.TemplateResponse(
        request=req, name="user_page.html", context={"user": user,
                                                     "records": records,
                                                     "FastAddRecordForm": FastAddRecordForm()}
    )


@router.get("/login", name="login_page")
async def login(req: Request):
    return templates.TemplateResponse(
        request=req, name="login_page.html", context={"form": LoginForm()}
    )


@router.get('/logout')
async def logout() -> RedirectResponse:
    res = RedirectResponse('/login')
    res.delete_cookie("Authorization")
    return res


@router.get("/register", name="register_page")
async def login(req: Request):
    return templates.TemplateResponse(
        request=req, name="register_page.html", context={"form": RegisterForm()}
    )


@router.get('/change_record', name="change_record_page")
async def change_record(req: Request, user_id: Annotated[int, Depends(get_jwt_payload)],
                        id: Annotated[int | None, Query()] = None,
                        ce_service: CEService = Depends(get_ce_service),
                        user_service: UserService = Depends(get_user_service)):
    if isinstance(id, NoneType):
        records = await ce_service.get_records_by(user_id=user_id)
        user = await user_service.get_user_by(id=user_id)
        record = None
        return templates.TemplateResponse(
            request=req, name="change_record.html", context={"record": record,
                                                             "user": user,
                                                             "records": records,
                                                             "form": ChangeRecordForm()}
        )
    else:
        records = await ce_service.get_records_by(user_id=user_id)
        record = await ce_service.get_records_by(id=id, user_id=user_id)
        user = await user_service.get_user_by(id=user_id)
        form = ChangeRecordForm()
        form.value.data = record.value
        form.operation_type.data = record.operation_type
        form.comment.data = record.comment
        return templates.TemplateResponse(
            request=req, name="change_record.html", context={"record": record,
                                                             "user": user,
                                                             "records": records,
                                                             "form": form}
        )
