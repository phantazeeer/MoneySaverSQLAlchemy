from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.exc import NoResultFound

from app.api.schemas import User
from app.services.user_service import UserService


@pytest.fixture
def user_service(uow_mock):
    return UserService(uow=uow_mock)


@pytest.fixture(autouse=True)
def mock_utils():
    with (
        patch("app.services.user_service.get_password_hash", return_value="hashed_pw"),
        patch("app.services.user_service.verify_password", return_value=True),
        patch("app.services.user_service.create_token", return_value="jwt_token"),
    ):
        yield


async def test_add_user_success(user_service, uow_mock):
    await user_service.add_user("testuser", "test@example.com", "plainpassword")
    uow_mock.users.add_user.assert_called_once_with(
        username="testuser",
        email="test@example.com",
        password="hashed_pw",
    )


async def test_add_user_duplicate_email(user_service, uow_mock):
    uow_mock.users.add_user.side_effect = ValueError("Почта неуникальна")

    with pytest.raises(Exception) as exc_info:
        await user_service.add_user("u", "e@x.com", "p")

    assert str(exc_info.value) == "Эта почта уже занята"
    uow_mock.users.add_user.assert_called_once()


async def test_get_user_by_success(user_service, uow_mock):
    user_data = {
        "id": 1,
        "username": "test",
        "email": "t@t.com",
        "password": "hash",
        "balance": 0,
        "created_at": datetime.now(),
    }
    uow_mock.users.get_one.return_value = user_data

    with patch("app.services.user_service.User.model_validate", return_value=User(**user_data)):
        result = await user_service.get_user_by(id=1)

    assert result.id == 1
    assert result.username == "test"


async def test_get_user_by_error(user_service, uow_mock):
    uow_mock.users.get_one.side_effect = Exception("DB error")

    with pytest.raises(Exception, match="DB error"):
        await user_service.get_user_by(email="x@x.com")


async def test_delete_user_success(user_service, uow_mock):
    await user_service.delete_user(42)
    uow_mock.users.delete_by_user.assert_called_once_with(42)


async def test_update_user_success(user_service, uow_mock):
    await user_service.update_user(1, username="newname")
    uow_mock.users.update_user.assert_called_once_with(1, username="newname")


async def test_update_user_integrity_error(user_service, uow_mock):
    integrity_error = ValueError("email is already used")
    uow_mock.users.update_user.side_effect = integrity_error

    with pytest.raises(Exception) as exc_info:
        await user_service.update_user(1, email="taken@example.com")

    assert str(exc_info.value) == "Введите другую почту"


async def test_login_user_not_found(user_service, uow_mock):
    uow_mock.users.get_one.side_effect = NoResultFound()

    with pytest.raises(Exception) as exc_info:
        await user_service.login("no@exist.com", "pass")

    assert str(exc_info.value) == "Пользователь не найден"


async def test_login_wrong_password(user_service, uow_mock):
    user_obj = AsyncMock()
    user_obj.password = "hashed_pass"
    uow_mock.users.get_one.return_value = user_obj

    with patch("app.services.user_service.verify_password", return_value=False):
        with pytest.raises(Exception) as exc_info:
            await user_service.login("user@ex.com", "wrong")

        assert str(exc_info.value) == "Неправильный пароль"


async def test_login_success(user_service, uow_mock):
    user_obj = AsyncMock()
    user_obj.id = 100
    user_obj.password = "hashed_pass"
    uow_mock.users.get_one.return_value = user_obj

    token = await user_service.login("correct@ex.com", "right")
    assert token == "jwt_token"


async def test_get_sum_of_costs_and_earn(user_service, uow_mock):
    uow_mock.users.get_user_costs_and_earnings.return_value = (1000, 200)
    earnings, costs = await user_service.get_sum_of_costs_and_earn(42)
    assert earnings == 1000
    assert costs == 200
