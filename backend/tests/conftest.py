import re
from dataclasses import replace
from typing import AsyncGenerator

import pytest
from aiosqlite import Connection, Row, connect
from fastapi.responses import Response

from api.auth import set_auth_cookie
from db import get_db, init_connection
from main import app

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


@pytest.fixture
async def test_server(testdb: Connection) -> AsyncGenerator[None, None]:
    async def override_db():
        yield testdb

    app.state.config = replace(app.state.config, jwt_key=JWT_TEST_KEY)
    app.dependency_overrides[get_db] = override_db
    yield
    app.dependency_overrides.clear()
