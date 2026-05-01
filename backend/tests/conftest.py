import re
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from dataclasses import replace
from typing import AsyncGenerator, Callable

import pytest
from aiosqlite import Connection, Row, connect
from fastapi.responses import Response

from achievements import AchievementSystem
from api.auth import set_auth_cookie
from config import AppConfig
from db import get_db, init_connection
from main import app
from sensor import SensorSystem

JWT_TEST_KEY = "testkeytestkeytestkeytestkeytestkeytestkeytestkey"


def mangle_cookie(user_id: int) -> str:
    response = Response("test response")
    set_auth_cookie(JWT_TEST_KEY, user_id, response)
    assert (cookie_header := response.headers.get("set-cookie")) is not None
    assert (matches := re.match("auth-token=(.*);", cookie_header)) is not None
    return matches[1]


@pytest.fixture
async def testdb() -> AsyncGenerator[Connection, None]:
    async with connect(":memory:") as db:
        db.row_factory = Row
        await init_connection(db)
        yield db


@pytest.fixture(autouse=True)
def _system(testdb_manager: Callable[[], AbstractAsyncContextManager[Connection]]):
    print("systems changed")
    SensorSystem(get_db=testdb_manager)
    AchievementSystem(get_db=testdb_manager)


@pytest.fixture
def testdb_manager(
    testdb: Connection,
) -> Callable[[], AbstractAsyncContextManager[Connection]]:
    @asynccontextmanager
    async def _manager() -> AsyncGenerator[Connection, None]:
        yield testdb

    return _manager


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def get_config(test_server: None) -> AsyncGenerator[AppConfig, None]:
    return app.state.config


@pytest.fixture
async def test_server(testdb: Connection) -> AsyncGenerator[None, None]:
    async def override_db():
        yield testdb

    app.state.config = replace(app.state.config, jwt_key=JWT_TEST_KEY)
    app.dependency_overrides[get_db] = override_db
    yield
    app.dependency_overrides.clear()
