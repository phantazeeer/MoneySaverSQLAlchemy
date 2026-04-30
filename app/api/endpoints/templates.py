from typing import Annotated, Literal
from types import NoneType
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services import CostsAndEarningsService as CEService
from app.services import UserService
from app.utils import get_jwt_payload
from app.utils.logger import get_logger
from app.forms import FastAddRecordForm, LoginForm, RegisterForm, ChangeRecordForm, ChooseDateForm, ChangeTargetForm
from app.utils.dependencies import get_ce_service, get_user_service

router = APIRouter(tags=['Working with templates'])

templates = Jinja2Templates(directory="app/templates")
log = get_logger(__name__)


@router.get("/", name="main_page")
async def main(req: Request, user_id: Annotated[int, Depends(get_jwt_payload)],
               ce_service: CEService = Depends(get_ce_service),
               filter_by: Annotated[Literal["costs", "earnings"], Query()] | None = None,
               change_targ: Annotated[Literal["1"], Query()] | None = None,
               user_service: UserService = Depends(get_user_service)):
    user = await user_service.get_user_by(id=user_id)
    if filter_by:
        records = await ce_service.user_costs_or_earnings(user_id=user_id, filter=filter_by)
    else:
        records = await ce_service.get_records_by(user_id=user_id)
    if change_targ:
        change_target_form = ChangeTargetForm()
    else:
        change_target_form = None
    earnings, costs = await user_service.get_sum_of_costs_and_earn(user_id)

    return templates.TemplateResponse(
        request=req, name="user_page.html", context={"user": user,
                                                     "records": records,
                                                     "FastAddRecordForm": FastAddRecordForm(),
                                                     "ChangeTargetForm": change_target_form,
                                                     "total_earnings": earnings,
                                                     "total_costs": costs}
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
        return templates.TemplateResponse(
            request=req, name="change_record.html", context={"record": None,
                                                             "user": user,
                                                             "records": records,
                                                             "form": None}
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


@router.get('/statistics', name='statistics_page')
async def statistics(req: Request, user_id: Annotated[int, Depends(get_jwt_payload)],
                     delta: Annotated[Literal["1", "6", "12"], Query()] | None = None,
                     user_service: UserService = Depends(get_user_service)):
    if not isinstance(delta, NoneType):
        return RedirectResponse(
            f"/statistics/choose_date?start={(datetime.now(timezone.utc) - timedelta(days=int(delta) * 30)).date()}&end={(datetime.now(timezone.utc)).date()}")
    user = await user_service.get_user_by(id=user_id)
    return templates.TemplateResponse(
        request=req, name="statistics.html", context={"user": user,
                                                      "form": None}
    )


@router.get('/statistics/choose_date', name='statistics_page')
async def statistics(req: Request, user_id: Annotated[int, Depends(get_jwt_payload)],
                     ce_service: CEService = Depends(get_ce_service),
                     start: Annotated[str, Query()] | None = None,
                     end: Annotated[str, Query()] | None = None,
                     user_service: UserService = Depends(get_user_service)):
    user = await user_service.get_user_by(id=user_id)
    if not (isinstance(end, NoneType) or isinstance(start, NoneType)):
        try:
            start = datetime.strptime(start, '%Y-%m-%d')
            end = datetime.strptime(end, '%Y-%m-%d')
            if start >= end and datetime.now() < start:
                raise ValueError
            image = await ce_service.create_graphics(period=(start, end), user_id=user_id)
            log.debug(image)
            return templates.TemplateResponse(
                request=req, name="statistics.html", context={"user": user,
                                                              "form": ChooseDateForm(),
                                                              "error": None,
                                                              "image": image}
            )
        except ValueError as e:
            print(str(e))
            return templates.TemplateResponse(
                request=req, name="statistics.html", context={"user": user,
                                                              "form": ChooseDateForm(),
                                                              "error": "Введите корректные данные",
                                                              "image": None}
            )
    return templates.TemplateResponse(
        request=req, name="statistics.html", context={"user": user,
                                                      "form": ChooseDateForm(),
                                                      "error": None,
                                                      "image": None}
    )
