import pytest
import pytest_asyncio
from sqlalchemy import delete, insert, or_, select
from sqlalchemy.exc import NoResultFound

from app.api.schemas.user import UserChange
from app.db.models import CostsAndEarnings, User
from app.repositories.user_repo import UserRepository


@pytest_asyncio.fixture
async def user_repo(ready_session):
    user_repo = UserRepository(ready_session)
    yield user_repo


async def test_repo_add(user_repo, ready_session):
    await user_repo.add_user(username="test_user", email="e@x.com", password="hashed_pswd")
    await ready_session.commit()

    stmt = select(User).where(User.username == "test_user")
    added_user = (await ready_session.execute(stmt)).scalar_one()
    assert added_user
    assert added_user.username == "test_user"
    assert added_user.email == "e@x.com"
    assert added_user.password == "hashed_pswd"
    stmt = delete(User).where(User.username == "test_user", User.email == "e@x.com")
    await ready_session.execute(stmt)
    await ready_session.commit()


async def test_repo_add_nonunique(user_repo, ready_session):
    await user_repo.add_user(username="test_user1", email="e@x.com", password="hashed_pswd")
    await ready_session.commit()
    with pytest.raises(ValueError, match="Почта неуникальна"):
        await user_repo.add_user(username="test_user2", email="e@x.com", password="hashed_pswd")

    stmt = delete(User).where(User.username == "test_user1", User.email == "e@x.com")
    await ready_session.execute(stmt)
    await ready_session.commit()


async def test_repo_delete_user(user_repo, ready_session):
    stmt = insert(User).values(username="test_user", email="e@x.com", password="pswd").returning(User.id)
    user_id = (await ready_session.execute(stmt)).scalar_one()
    await ready_session.commit()

    await user_repo.delete_by_user(user_id)
    await ready_session.commit()

    stmt = select(User).where(User.id == user_id)
    with pytest.raises(NoResultFound):
        (await ready_session.execute(stmt)).scalar_one()


async def test_repo_update_user(user_repo, ready_session):
    stmt = insert(User).values(username="test_user", email="e@x.com", password="pswd").returning(User.id)
    user_id = (await ready_session.execute(stmt)).scalar_one()
    await ready_session.commit()

    changes = UserChange(username="test_user1", balance=123, goal_name="goal!!!", goal_value=124).model_dump()
    await user_repo.update_user(user_id, **changes)
    await ready_session.commit()

    stmt = select(User).where(User.email == "e@x.com")
    user = (await ready_session.execute(stmt)).scalar_one()
    assert user.username == "test_user1"
    assert user.balance == 123
    assert user.goal_name == "goal!!!"
    assert user.goal_value == 124

    stmt = delete(User).where(User.email == "e@x.com")
    await ready_session.execute(stmt)
    await ready_session.commit()


async def test_repo_update_with_used_email(user_repo, ready_session):
    stmt = insert(User).values(username="test_user", email="e@x.com", password="pswd").returning(User.id)
    user_id = (await ready_session.execute(stmt)).scalar_one()
    stmt = insert(User).values(username="other_user", email="e1@x.com", password="pswd1")
    await ready_session.execute(stmt)
    await ready_session.commit()

    changes = UserChange(
        username="test_user1",
        balance=123,
        goal_name="goal!!!",
        email="e1@x.com",
        goal_value=124,
    ).model_dump()

    with pytest.raises(ValueError, match="email is already used"):
        await user_repo.update_user(user_id, **changes)
        await ready_session.commit()

    stmt = delete(User).where(or_(User.email == "e@x.com", User.email == "e1@x.com"))
    await ready_session.execute(stmt)
    await ready_session.commit()


async def test_repo_get_user_costs_and_earnings(user_repo, ready_session):
    stmt = insert(User).values(username="test_user", email="e@x.com", password="pswd").returning(User.id)
    user_id = (await ready_session.execute(stmt)).scalar_one()
    await ready_session.commit()
    for i in range(1, 10):
        stmt = insert(CostsAndEarnings).values(user_id=user_id, operation_type=i % 2, value=100 * i)
        await ready_session.execute(stmt)
        await ready_session.commit()

    earnings, costs = await user_repo.get_user_costs_and_earnings(user_id)

    assert costs == 100 + 300 + 500 + 700 + 900
    assert earnings == 200 + 400 + 600 + 800

    stmt = delete(CostsAndEarnings).where(CostsAndEarnings.user_id == user_id)
    await ready_session.execute(stmt)
    stmt = delete(User).where(User.email == "e@x.com")
    await ready_session.execute(stmt)
    await ready_session.commit()
