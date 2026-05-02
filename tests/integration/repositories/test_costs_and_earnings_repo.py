from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy import delete, insert, select
from sqlalchemy.exc import NoResultFound

from app.db.models import CostsAndEarnings, User
from app.repositories.costs_and_earnings_repo import CostsAndEarningsRepository


@pytest_asyncio.fixture
async def user_id(ready_session):
    stmt = insert(User).values(username="test_user", email="e@x.com", password="pswd").returning(User.id)
    user_id = (await ready_session.execute(stmt)).scalar_one()
    await ready_session.commit()
    yield user_id
    await ready_session.execute(delete(CostsAndEarnings).where(CostsAndEarnings.user_id == user_id))
    await ready_session.execute(delete(User).where(User.id == user_id))
    await ready_session.commit()


@pytest_asyncio.fixture
async def costs_repo(ready_session):
    return CostsAndEarningsRepository(ready_session)


async def test_add_one_earnings(costs_repo, ready_session, user_id):
    initial_balance = (await ready_session.get(User, user_id)).balance

    await costs_repo.add_one(user_id=user_id, operation_type=0, value=500, comment="Зарплата")
    await ready_session.commit()

    stmt = select(CostsAndEarnings).where(CostsAndEarnings.user_id == user_id)
    records = (await ready_session.execute(stmt)).scalars().all()
    assert len(records) == 1
    assert records[0].value == 500
    assert records[0].operation_type == 0
    assert records[0].comment == "Зарплата"

    updated_user = await ready_session.get(User, user_id)
    assert updated_user.balance == initial_balance + 500


async def test_add_one_cost(costs_repo, ready_session, user_id):
    initial_balance = (await ready_session.get(User, user_id)).balance

    await costs_repo.add_one(user_id=user_id, operation_type=1, value=200, comment="Продукты")
    await ready_session.commit()

    updated_user = await ready_session.get(User, user_id)
    assert updated_user.balance == initial_balance - 200


async def test_update_record_from_cost_to_earnings(costs_repo, ready_session, user_id):
    stmt = (insert(CostsAndEarnings)
            .values(user_id=user_id, operation_type=1, value=100, comment="Старый расход")
            .returning(CostsAndEarnings.id))
    record = (await ready_session.execute(stmt)).scalar_one()
    await ready_session.commit()
    record_id = record

    await costs_repo.update_record(id=record_id, user_id=user_id,
                                   operation_type=0, value=150, comment="Новый доход", category_id=None)
    await ready_session.commit()

    updated_record = await ready_session.get(CostsAndEarnings, record_id)
    assert updated_record.operation_type == 0
    assert updated_record.value == 150
    assert updated_record.comment == "Новый доход"

    user = await ready_session.get(User, user_id)
    assert user.balance == 250


async def test_update_record_earnings_to_cost(costs_repo, ready_session, user_id):
    stmt = (insert(CostsAndEarnings)
            .values(user_id=user_id, operation_type=0, value=300, comment="Старый доход")
            .returning(CostsAndEarnings.id))
    record = (await ready_session.execute(stmt)).scalar_one()
    await ready_session.commit()
    record_id = record

    await costs_repo.update_record(id=record_id, user_id=user_id,
                                   operation_type=1, value=50, comment="Новый расход", category_id=None)
    await ready_session.commit()

    user = await ready_session.get(User, user_id)
    assert user.balance == -350


async def test_update_record_change_value_only(costs_repo, ready_session, user_id):
    await costs_repo.add_one(user_id=user_id, operation_type=1, value=100, comment="Расход")
    await ready_session.commit()
    record = (
        await ready_session.execute(select(CostsAndEarnings).where(CostsAndEarnings.user_id == user_id))).scalar_one()
    record_id = record.id

    await costs_repo.update_record(id=record_id, user_id=user_id,
                                   operation_type=1, value=250, comment="Расход увеличен", category_id=None)
    await ready_session.commit()

    user = await ready_session.get(User, user_id)
    assert user.balance == -250


async def test_update_record_nonexistent(costs_repo, user_id):
    with pytest.raises(NoResultFound):
        await costs_repo.update_record(id=9999, user_id=user_id,
                                       operation_type=0, value=100, comment="Несуществующая", category_id=None)


async def test_delete_by_id(costs_repo, ready_session, user_id):
    await costs_repo.add_one(user_id=user_id, operation_type=0, value=500, comment="Доход")
    await ready_session.commit()
    record = (
        await ready_session.execute(select(CostsAndEarnings).where(CostsAndEarnings.user_id == user_id))).scalar_one()
    record_id = record.id

    await costs_repo.delete_by_id(record_id)
    await ready_session.commit()

    stmt = select(CostsAndEarnings).where(CostsAndEarnings.id == record_id)
    with pytest.raises(NoResultFound):
        (await ready_session.execute(stmt)).scalar_one()

    user = await ready_session.get(User, user_id)
    assert user.balance == 0


async def test_delete_by_id_nonexistent(costs_repo):
    with pytest.raises(NoResultFound):
        await costs_repo.delete_by_id(9999)


async def test_get_list_by_date(costs_repo, ready_session, user_id):
    base_date = datetime(2025, 1, 1, 12, 0, 0)
    dates = [
        base_date,
        base_date + timedelta(days=2),
        base_date + timedelta(days=5),
        base_date - timedelta(days=1),
    ]
    for i, dt in enumerate(dates):
        stmt = insert(CostsAndEarnings).values(
            user_id=user_id,
            operation_type=i % 2,
            value=100 * (i + 1),
            created_at=dt
        )
        await ready_session.execute(stmt)
    await ready_session.commit()

    start = datetime(2025, 1, 1, 0, 0, 0)
    end = datetime(2025, 1, 7, 0, 0, 0)

    records = await costs_repo.get_list_by_date(start=start, end=end, user_id=user_id)

    assert len(records) == 3
    assert records[0].created_at == dates[0]
    assert records[1].created_at == dates[1]
    assert records[2].created_at == dates[2]


async def test_get_list_by_date_empty(costs_repo, user_id):
    start = datetime(2025, 1, 1, 0, 0, 0)
    end = datetime(2025, 1, 7, 0, 0, 0)

    records = await costs_repo.get_list_by_date(start=start, end=end, user_id=user_id)
    assert records == []
