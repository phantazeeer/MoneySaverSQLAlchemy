from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import NoResultFound

from app.api.schemas import Record
from app.db.models import CostsAndEarnings
from app.services.costs_and_earnings_service import CostsAndEarningsService


@pytest.fixture
def service(uow_mock):
    return CostsAndEarningsService(uow=uow_mock)


@pytest.fixture(autouse=True)
def mock_record_validate():
    with patch("app.services.costs_and_earnings_service.Record.model_validate") as mock:

        def side_effect(data):
            return MagicMock(spec=Record, **data)

        mock.side_effect = side_effect
        yield mock


async def test_add_record_success(service, uow_mock):
    await service.add_record(user_id=1, operation_type="0", value=100, comment="test")
    uow_mock.records.add_one.assert_called_once_with(
        user_id=1,
        operation_type=0,
        value=100,
        comment="test",
    )


async def test_add_record_without_comment(service, uow_mock):
    await service.add_record(user_id=2, operation_type="1", value=50)
    uow_mock.records.add_one.assert_called_once_with(
        user_id=2,
        operation_type=1,
        value=50,
        comment=None,
    )


async def test_delete_record_success(service, uow_mock):
    record_mock = AsyncMock(user_id=1)
    uow_mock.records.get_one.return_value = record_mock

    await service.delete_record(id=10, user_id=1)

    uow_mock.records.get_one.assert_called_once_with(id=10)
    uow_mock.records.delete_by_id.assert_called_once_with(10)


async def test_delete_record_not_owner(service, uow_mock):
    record_mock = AsyncMock(user_id=2)
    uow_mock.records.get_one.return_value = record_mock

    with pytest.raises(ValueError, match="Пользователь не является владельцем записи"):
        await service.delete_record(id=10, user_id=1)

    uow_mock.records.delete_by_id.assert_not_called()


async def test_delete_record_not_found(service, uow_mock):
    uow_mock.records.get_one.side_effect = NoResultFound()

    with pytest.raises(Exception, match="Запись не найдена"):
        await service.delete_record(id=999, user_id=1)


async def test_get_records_by_id_and_user_success(service, uow_mock):
    orm_record = MagicMock(spec=CostsAndEarnings)
    orm_record.id = 1
    orm_record.user_id = 1
    orm_record.operation_type = 0
    orm_record.value = 100
    orm_record.comment = ""
    orm_record.category_id = None
    orm_record.created_at = None

    uow_mock.records.get_one.return_value = orm_record

    expected_record = Record.model_validate(
        {
            "id": 1,
            "user_id": 1,
            "operation_type": 0,
            "value": 100,
            "comment": "",
            "category": None,
            "created_at": None,
        },
    )
    with patch(
        "app.services.costs_and_earnings_service.Record.model_validate",
        return_value=expected_record,
    ) as mock_validate:
        result = await service.get_records_by(id=1, user_id=1)

    uow_mock.records.get_one.assert_called_once_with(id=1)
    mock_validate.assert_called_once_with(
        {
            "id": 1,
            "user_id": 1,
            "operation_type": 0,
            "value": 100,
            "comment": "",
            "category": None,
            "created_at": None,
        },
    )
    assert result == expected_record


async def test_get_records_by_id_and_user_not_owner(service, uow_mock):
    orm_record = MagicMock(spec=CostsAndEarnings)
    orm_record.user_id = 2

    uow_mock.records.get_one.return_value = orm_record

    with pytest.raises(ValueError, match="Пользователь не является владельцем записи"):
        await service.get_records_by(id=1, user_id=1)


async def test_get_records_by_id_not_found(service, uow_mock):
    uow_mock.records.get_one.side_effect = NoResultFound()

    with pytest.raises(Exception, match="Запись не найдена"):
        await service.get_records_by(id=1, user_id=1)


async def test_get_records_by_user_only(service, uow_mock):
    records_list = []
    for i in range(1, 3):
        orm_record = MagicMock(spec=CostsAndEarnings)
        orm_record.id = i
        orm_record.user_id = 1
        orm_record.operation_type = 0
        orm_record.value = 100 * i
        orm_record.comment = ""
        orm_record.category_id = None
        orm_record.created_at = None
        records_list.append(orm_record)
    uow_mock.records.get_list_by.return_value = records_list

    result = await service.get_records_by(user_id=1)

    uow_mock.records.get_list_by.assert_called_once_with(user_id=1)
    assert len(result) == 2


async def test_get_records_by_user_only_not_found(service, uow_mock):
    uow_mock.records.get_list_by.side_effect = NoResultFound()

    with pytest.raises(Exception, match="Записи не найдены"):
        await service.get_records_by(user_id=1)


async def test_get_records_by_no_params(service):
    with pytest.raises(ValueError, match="Введите user_id или user_id и id"):
        await service.get_records_by()


async def test_update_record_success_all_fields(service, uow_mock):
    record_mock = AsyncMock(user_id=1, operation_type=0, value=100, comment="old", category_id=None)
    uow_mock.records.get_one.return_value = record_mock

    await service.update_record(id=1, user_id=1, operation_type=1, value=200, comment="new")

    uow_mock.records.update_record.assert_called_once_with(
        1,
        1,
        operation_type=1,
        value=200,
        comment="new",
        category_id=None,
    )


async def test_update_record_partial_fields(service, uow_mock):
    record_mock = AsyncMock(user_id=1, operation_type=0, value=100, comment="old")
    uow_mock.records.get_one.return_value = record_mock

    await service.update_record(id=1, user_id=1, value=500)

    uow_mock.records.update_record.assert_called_once_with(
        1,
        1,
        operation_type=0,
        value=500,
        comment="old",
        category_id=None,
    )


async def test_update_record_not_owner(service, uow_mock):
    record_mock = AsyncMock(user_id=2)
    uow_mock.records.get_one.return_value = record_mock

    with pytest.raises(ValueError, match="Пользователь не является владельцем записи"):
        await service.update_record(id=1, user_id=1)


async def test_update_record_not_found(service, uow_mock):
    uow_mock.records.get_one.side_effect = NoResultFound()

    with pytest.raises(Exception, match="Запись не найдена"):
        await service.update_record(id=999, user_id=1)


async def test_user_costs_or_earnings_earnings(service, uow_mock):
    records_list = [{"id": 1, "user_id": 1, "operation_type": 0, "value": 10}]
    uow_mock.records.get_list_by.return_value = records_list

    result = await service.user_costs_or_earnings(user_id=1, filter="earnings")

    uow_mock.records.get_list_by.assert_called_once_with(user_id=1, operation_type=0)
    assert len(result) == 1


async def test_user_costs_or_earnings_costs(service, uow_mock):
    records_list = []
    uow_mock.records.get_list_by.return_value = records_list

    result = await service.user_costs_or_earnings(user_id=1, filter="costs")

    uow_mock.records.get_list_by.assert_called_once_with(user_id=1, operation_type=1)
    assert result == []


async def test_create_graphics_no_records(service, uow_mock):
    uow_mock.records.get_list_by_date.return_value = []

    result = await service.create_graphics(
        period=(datetime(2023, 1, 1), datetime(2023, 1, 31)),
        user_id=1,
    )
    assert result is None


async def test_create_graphics_with_records_less_30_days(service, uow_mock):
    # Подготовка данных
    now = datetime(2023, 2, 1, tzinfo=timezone.utc)

    uow_mock.records.get_list_by_date.return_value = [
        {
            "id": 1,
            "user_id": 1,
            "operation_type": bool(0),
            "value": 100,
            "created_at": datetime(2023, 1, 15, tzinfo=timezone.utc),
        },
        {
            "id": 2,
            "user_id": 1,
            "operation_type": bool(1),
            "value": 30,
            "created_at": datetime(2023, 1, 20, tzinfo=timezone.utc),
        },
    ]

    user_mock = AsyncMock(balance=1000)
    uow_mock.users.get_one.return_value = user_mock

    with patch("app.services.costs_and_earnings_service.datetime") as mock_datetime:
        mock_datetime.now.return_value = now
        with patch("app.services.costs_and_earnings_service.plt") as mock_plt:
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_plt.subplots.return_value = (mock_fig, mock_ax)

            with patch("app.services.costs_and_earnings_service.base64.b64encode") as mock_b64:
                mock_b64.return_value = b"encoded_string"
                result = await service.create_graphics(
                    period=(datetime(2023, 1, 1), datetime(2023, 1, 31)),
                    user_id=1,
                )

    mock_plt.subplots.assert_called_once()
    mock_ax.plot.assert_called_once()
    args, _ = mock_ax.plot.call_args
    assert args[0] == ["15", "20"]
    assert len(args[1]) == 2
    mock_plt.savefig.assert_called_once()
    mock_plt.close.assert_called_once()
    mock_b64.assert_called_once()
    assert result == "encoded_string"


async def test_create_graphics_between_30_and_360_days(service, uow_mock):
    now = datetime(2023, 12, 1, tzinfo=timezone.utc)
    uow_mock.records.get_list_by_date.return_value = [
        {
            "id": 1,
            "user_id": 1,
            "operation_type": bool(0),
            "value": 50,
            "created_at": datetime(2023, 6, 15, tzinfo=timezone.utc),
        },
    ]
    uow_mock.users.get_one.return_value = AsyncMock(balance=500)

    with patch("app.services.costs_and_earnings_service.datetime") as mock_datetime:
        mock_datetime.now.return_value = now
        with patch("app.services.costs_and_earnings_service.plt") as mock_plt:
            mock_plt.subplots.return_value = (MagicMock(), MagicMock())
            with patch("app.services.costs_and_earnings_service.base64.b64encode", return_value=b"img"):
                await service.create_graphics(
                    period=(datetime(2023, 1, 1), datetime(2023, 12, 31)),
                    user_id=1,
                )
    args, _ = mock_plt.subplots.return_value[1].plot.call_args
    assert args[0] == ["15.06"]


async def test_create_graphics_more_than_360_days(service, uow_mock):
    now = datetime(2025, 1, 1, tzinfo=timezone.utc)
    uow_mock.records.get_list_by_date.return_value = [
        {
            "id": 1,
            "user_id": 1,
            "operation_type": bool(1),
            "value": 20,
            "created_at": datetime(2023, 1, 1, tzinfo=timezone.utc),
        },
    ]
    uow_mock.users.get_one.return_value = AsyncMock(balance=100)

    with patch("app.services.costs_and_earnings_service.datetime") as mock_datetime:
        mock_datetime.now.return_value = now
        with patch("app.services.costs_and_earnings_service.plt") as mock_plt:
            mock_plt.subplots.return_value = (MagicMock(), MagicMock())
            with patch("app.services.costs_and_earnings_service.base64.b64encode", return_value=b"img"):
                await service.create_graphics(
                    period=(datetime(2023, 1, 1), datetime(2025, 1, 1)),
                    user_id=1,
                )
    args, _ = mock_plt.subplots.return_value[1].plot.call_args
    assert args[0] == ["01.01.2023"]
