from unittest.mock import AsyncMock
import pytest

class AsyncContextManagerMock:
    def __init__(self):
        self.records = AsyncMock()
        self.users = AsyncMock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def uow_mock():
    return AsyncContextManagerMock()