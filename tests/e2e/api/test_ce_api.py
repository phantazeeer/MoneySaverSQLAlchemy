import pytest
from httpx import AsyncClient

@pytest.mark.asyncio(loop_scope="session")
async def test_get_my_records(logged_client: AsyncClient):
    resp = await logged_client.get("/user/me/records")
    assert resp.status_code == 200
    records = resp.json()
    assert isinstance(records, list)
    assert len(records) == 4


@pytest.mark.asyncio(loop_scope="session")
async def test_get_my_records_unauthorized(unlogged_client: AsyncClient):
    resp = await unlogged_client.get("/user/me/records")
    assert resp.status_code == 307


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("record_data, expected_status", [
    ({"operation_type": "0", "value": 1000, "comment": "Зарплата"}, 201),
    ({"operation_type": "1", "value": 500, "comment": "Продукты"}, 201),
    ({"operation_type": "0", "value": -100}, 201),
    ({"operation_type": "2", "value": 100}, 422),
    ({"value": 100}, 422),
])
async def test_add_record(logged_client: AsyncClient, record_data, expected_status):
    resp = await logged_client.post("/records/", data=record_data)
    assert resp.status_code == expected_status
    if expected_status == 201:
        assert resp.json() == 'OK'


@pytest.mark.asyncio(loop_scope="session")
async def test_get_single_record(logged_client: AsyncClient):
    resp = await logged_client.get("/user/me/records")
    records = resp.json()
    assert len(records) > 0
    record_id = records[0]["id"]

    resp2 = await logged_client.get(f"/records/{record_id}")
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["id"] == record_id
    assert data["user_id"] == 1


@pytest.mark.asyncio(loop_scope="session")
async def test_get_nonexistent_record(logged_client: AsyncClient):
    resp = await logged_client.get("/records/99999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Запись не найдена"


@pytest.mark.asyncio(loop_scope="session")
async def test_update_record(logged_client: AsyncClient):
    resp = await logged_client.get("/user/me/records")
    records = resp.json()
    record_id = records[0]["id"]
    old_value = records[0]["value"]

    new_value = old_value + 100
    update_data = {"value": new_value, "comment": "updated"}
    resp2 = await logged_client.put(f"/records/{record_id}", data=update_data)
    assert resp2.status_code == 200
    assert resp2.json() == "OK"

    resp3 = await logged_client.get(f"/records/{record_id}")
    updated = resp3.json()
    assert updated["value"] == new_value
    assert updated["comment"] == "updated"


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_record(logged_client: AsyncClient):

    add_resp = await logged_client.post("/records/", data={"operation_type": "0", "value": 777})
    assert add_resp.status_code == 201


    records_resp = await logged_client.get("/user/me/records")
    record = next(r for r in records_resp.json() if r["value"] == 777)
    record_id = record["id"]


    del_resp = await logged_client.delete(f"/records/{record_id}")
    assert del_resp.status_code == 200


    get_resp = await logged_client.get(f"/records/{record_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_update_record_unauthorized(unlogged_client: AsyncClient):
    resp = await unlogged_client.put("/records/1", data={"value": 100})
    assert resp.status_code == 307


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_record_unauthorized(unlogged_client: AsyncClient):
    resp = await unlogged_client.delete("/records/1")
    assert resp.status_code == 307