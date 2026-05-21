import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
async def test_get_me_unauthorized(unlogged_client: AsyncClient):
    resp = await unlogged_client.get("/user/me")
    assert resp.status_code == 307


@pytest.mark.asyncio(loop_scope="session")
async def test_get_me_authorized(logged_client: AsyncClient):
    resp = await logged_client.get("/user/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "ms@gmail.com"
    assert data["username"] == "Максим Струнников"
    assert "balance" in data
    assert "goal_name" in data
    assert "goal_value" in data


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    "changes, expected_status, expected_field",
    [
        ({"username": "Новое имя"}, 200, "username"),
        ({"balance": 10000}, 200, "balance"),
        ({"email": "newemail@example.com"}, 200, "email"),
        ({"goal_name": "Купить машину", "goal_value": 2000000}, 200, "goal_name"),
        ({"email": "ms@gmail.com"}, 200, "email"),
    ],
)
async def test_change_me(logged_client: AsyncClient, changes, expected_status, expected_field):
    resp = await logged_client.put("/user/me", data=changes)
    assert resp.status_code == expected_status
    if expected_status == 200:
        get_resp = await logged_client.get("/user/me")
        assert get_resp.json()[expected_field] == changes[expected_field]
    elif expected_status == 409:
        assert resp.json()["detail"] == "email is already used"
    elif expected_status == 422:
        assert "detail" in resp.json()


@pytest.mark.asyncio(loop_scope="session")
async def test_register_new_user(unlogged_client: AsyncClient):
    data = {
        "username": "NewUser",
        "email": "newuser@example.com",
        "password": "secret",
    }
    resp = await unlogged_client.post("/user/register", data=data)
    assert resp.status_code == 201
    assert resp.json() is None


@pytest.mark.asyncio(loop_scope="session")
async def test_register_duplicate_email(unlogged_client: AsyncClient):
    data = {
        "username": "Duplicate",
        "email": "ms@gmail.com",
        "password": "123",
    }
    resp = await unlogged_client.post("/user/register", data=data)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Эта почта уже занята"


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    "credentials, expected_status, expected_detail",
    [
        ({"email": "ms@gmail.com", "password": "123"}, 200, None),
        ({"email": "wrong@example.com", "password": "123"}, 400, "Пользователь не найден"),
        ({"email": "ms@gmail.com", "password": "wrong"}, 400, "Неправильный пароль"),
        ({"email": "", "password": ""}, 422, None),
    ],
)
async def test_login(unlogged_client: AsyncClient, credentials, expected_status, expected_detail):
    resp = await unlogged_client.post("/user/login", data=credentials)
    assert resp.status_code == expected_status
    if expected_status == 200:
        assert "Authorization" in resp.cookies
    elif expected_detail:
        assert resp.json()["detail"] == expected_detail


@pytest.mark.asyncio(loop_scope="session")
async def test_logout(logged_client: AsyncClient):
    resp = await logged_client.get("/user/logout")
    assert resp.status_code == 200
    # После выхода кука должна быть удалена
    assert "Authorization" not in resp.cookies or resp.cookies.get("Authorization") == ""
