from datetime import datetime, timedelta, timezone
from types import NoneType
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.api.schemas import User
from app.forms import (
    ChangeRecordForm,
    ChangeTargetForm,
    ChooseDateForm,
    CreateLimitForm,
    FastAddRecordForm,
    LoginForm,
    RegisterForm,
)
from app.services import CategoryService, LimitService, UserService
from app.services import CostsAndEarningsService as CEService
from app.utils import get_jwt_payload
from app.utils.dependencies import get_categories_service, get_ce_service, get_limit_service, get_user_service
from app.utils.logger import get_logger

router = APIRouter(tags=["Working with templates"])

templates = Jinja2Templates(directory="app/templates")
log = get_logger(__name__)


@router.get("/", name="main_page")
async def main(
    req: Request,
    user_id: Annotated[int, Depends(get_jwt_payload)],
    ce_service: Annotated[CEService, Depends(get_ce_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    categ_service: Annotated[CategoryService, Depends(get_categories_service)],
    limit_service: Annotated[LimitService, Depends(get_limit_service)],
    filter_by: Annotated[Literal["costs", "earnings"], Query()] | None = None,
    change_targ: Annotated[Literal["1"], Query()] | None = None,
    change_limit: Annotated[Literal["1"], Query()] | None = None,
):
    try:
        user = User.model_validate(await user_service.get_user_by(id=user_id))
    except Exception as err:
        if str(err) == "Пользователь не найден":
            raise HTTPException(400, "Пользователь не найден") from None
    if filter_by:
        records = await ce_service.user_costs_or_earnings(user_id=user_id, filter=filter_by)
    else:
        records = await ce_service.get_records_by(user_id=user_id)
    change_target_form = ChangeTargetForm() if change_targ else None
    change_limit_form = CreateLimitForm() if change_limit else None
    earnings, costs = await user_service.get_sum_of_costs_and_earn(user_id)
    categories = await categ_service.get_user_categories(user_id)
    categories_name = [i.name for i in categories]
    form = FastAddRecordForm(categories=categories_name)
    try:
        user_limits = await limit_service.get_list_of_limits(user_id)
        limits = []
        for limit in user_limits:
            data_to_render = {}
            data_to_render["id"] = limit.id
            data_to_render["value"] = limit.value
            data_to_render["name"] = limit.name
            data_to_render["period"] = True if limit.period else False
            try:
                log.debug(limit.categories)
                data_to_render["spent"] = await user_service.get_sum_of_costs_and_earn_in_limit(
                    user_id,
                    (limit.start, limit.end),
                    limit.categories,
                )
            except Exception as err:
                if str(err) == "У пользователя нет трат за этот период":
                    data_to_render["spent"] = 0
                else:
                    raise
            limits.append(data_to_render)
        user_data = user.model_dump()
        user_data["limit"] = limits
    except Exception as err:
        if str(err) != "У пользователя нет лимита":
            user_data = user.model_dump()
            user_data["limit"] = None
        log.exception("Exception in /templates/ while getting limit")
        raise

    log.debug(user_data["limit"])
    return templates.TemplateResponse(
        request=req,
        name="user_page.html",
        context={
            "user": user_data,
            "records": records,
            "FastAddRecordForm": form,
            "ChangeTargetForm": change_target_form,
            "total_earnings": earnings,
            "total_costs": costs,
            "categories": categories,
            "ChangeLimitForm": change_limit_form,
        },
    )


@router.get("/login", name="login_page")
async def login(req: Request):
    return templates.TemplateResponse(
        request=req,
        name="login_page.html",
        context={"form": LoginForm()},
    )


@router.get("/logout")
async def logout() -> RedirectResponse:
    res = RedirectResponse("/login")
    res.delete_cookie("Authorization")
    return res


@router.get("/register", name="register_page")
async def register(req: Request):
    return templates.TemplateResponse(
        request=req,
        name="register_page.html",
        context={"form": RegisterForm()},
    )


@router.get("/change_record", name="change_record_page")
async def change_record(
    req: Request,
    user_id: Annotated[int, Depends(get_jwt_payload)],
    ce_service: Annotated[CEService, Depends(get_ce_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    categ_service: Annotated[CategoryService, Depends(get_categories_service)],
    id: Annotated[int | None, Query()] = None,
):
    categories = await categ_service.get_user_categories(user_id)
    if isinstance(id, NoneType):
        records = await ce_service.get_records_by(user_id=user_id)
        try:
            user = await user_service.get_user_by(id=user_id)
            return templates.TemplateResponse(
                request=req,
                name="change_record.html",
                context={
                    "record": None,
                    "user": user,
                    "records": records,
                    "form": None,
                    "categories": categories,
                },
            )
        except Exception as err:
            if str(err) == "Пользователь не найден":
                raise HTTPException(400, "Пользователь не найден") from None
    else:
        records = await ce_service.get_records_by(user_id=user_id)
        record = await ce_service.get_records_by(id=id, user_id=user_id)
        try:
            user = await user_service.get_user_by(id=user_id)
            form = ChangeRecordForm(categories=[i.name for i in categories])
            form.value.data = record.value
            form.operation_type.data = "1" if record.operation_type else "0"
            form.comment.data = record.comment
            form.category.data = record.category
            return templates.TemplateResponse(
                request=req,
                name="change_record.html",
                context={
                    "record": record,
                    "user": user,
                    "records": records,
                    "form": form,
                    "categories": categories,
                },
            )
        except Exception as err:
            if str(err) == "Пользователь не найден":
                raise HTTPException(400, "Пользователь не найден") from None
            raise


@router.get("/statistics", name="statistics_page")
async def statistics(
    req: Request,
    user_id: Annotated[int, Depends(get_jwt_payload)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    delta: Annotated[Literal["1", "6", "12"], Query()] | None = None,
):
    if not isinstance(delta, NoneType):
        return RedirectResponse(
            f"/statistics/choose_date?start={(datetime.now(timezone.utc) - timedelta(days=int(delta) * 30)).date()}"
            f"&end={datetime.now(timezone.utc).date()}",
        )
    try:
        user = await user_service.get_user_by(id=user_id)
        return templates.TemplateResponse(
            request=req,
            name="statistics.html",
            context={"user": user, "form": None},
        )
    except Exception as err:
        if str(err) == "Пользователь не найден":
            raise HTTPException(400, "Пользователь не найден") from None


@router.get("/statistics/choose_date", name="statistics_page")
async def statistics_with_delta(
    req: Request,
    user_id: Annotated[int, Depends(get_jwt_payload)],
    ce_service: Annotated[CEService, Depends(get_ce_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    start: Annotated[str, Query()] | None = None,
    end: Annotated[str, Query()] | None = None,
):
    try:
        user = await user_service.get_user_by(id=user_id)
        if not (isinstance(end, NoneType) or isinstance(start, NoneType)):
            try:
                start = datetime.strptime(start, "%Y-%m-%d")
                end = datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1)
                if start >= end and datetime.now() < start:
                    raise ValueError
                image = await ce_service.create_graphics(period=(start, end), user_id=user_id)
                return templates.TemplateResponse(
                    request=req,
                    name="statistics.html",
                    context={
                        "user": user,
                        "form": ChooseDateForm(),
                        "error": None,
                        "image": image,
                    },
                )
            except ValueError as e:
                print(str(e))
                return templates.TemplateResponse(
                    request=req,
                    name="statistics.html",
                    context={
                        "user": user,
                        "form": ChooseDateForm(),
                        "error": "Введите корректные данные",
                        "image": None,
                    },
                )
        return templates.TemplateResponse(
            request=req,
            name="statistics.html",
            context={
                "user": user,
                "form": ChooseDateForm(),
                "error": None,
                "image": None,
            },
        )
    except Exception as err:
        if str(err) == "Пользователь не найден":
            raise HTTPException(400, "Пользователь не найден") from None
        raise


@router.get("/control_limits")
async def control_limits(
    req: Request,
    user_service: Annotated[UserService, Depends(get_user_service)],
    limit_service: Annotated[LimitService, Depends(get_limit_service)],
    user_id: Annotated[int, Depends(get_jwt_payload)],
    categ_service: Annotated[CategoryService, Depends(get_categories_service)],
):
    try:
        user = await user_service.get_user_by(id=user_id)
        user_limits = await limit_service.get_list_of_limits(user_id)
        limits = []
        for limit in user_limits:
            data_to_render = {}
            data_to_render["id"] = limit.id
            data_to_render["value"] = limit.value
            data_to_render["name"] = limit.name
            data_to_render["period"] = True if limit.period else False
            try:
                log.debug(limit.categories)
                data_to_render["spent"] = await user_service.get_sum_of_costs_and_earn_in_limit(
                    user_id,
                    (limit.start, limit.end),
                    limit.categories,
                )
            except Exception as err:
                if str(err) == "У пользователя нет трат за этот период":
                    data_to_render["spent"] = 0
                else:
                    raise
            limits.append(data_to_render)
    except Exception as err:
        if str(err) != "У пользователя нет лимита":
            limits = None
        log.exception("Exception in /templates/ while getting limit")
        raise
    categories = [i.name for i in await categ_service.get_user_categories(user_id)]
    log.debug(limits)
    return templates.TemplateResponse(
        request=req,
        name="control_limits.html",
        context={"user": user, "limits": limits, "form": CreateLimitForm(), "categories": categories},
    )
