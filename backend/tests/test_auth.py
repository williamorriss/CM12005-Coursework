import re
from typing import AsyncGenerator

import pytest
from aiosqlite import Connection, Row, connect
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.testclient import TestClient

from api.auth import UserSchema, authorize, parse_cas_response, set_auth_cookie
from config import AppConfig
from db import get_db, init_connection
from main import app

JWT_TEST_KEY = "testkey"

CAS_SUCCESS = """
<cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
    <cas:authenticationSuccess>
        <cas:user>wvam20</cas:user>
    </cas:authenticationSuccess>
</cas:serviceResponse>
"""

CAS_INVALID_TICKET = """
<cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
    <cas:authenticationFailure code='INVALID_TICKET'>
        Ticket &#039;ticket&#039; not recognized
    </cas:authenticationFailure>
</cas:serviceResponse>
"""

CAS_UNAUTHORIZED_SERVICE = """
<cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
    <cas:authenticationFailure code='UNAUTHORIZED_SERVICE'>
        The application you attempted to authenticate to is not authorized to use CAS.
    </cas:authenticationFailure>
</cas:serviceResponse>
"""


def mangle_cookie(user_id: int) -> str:
    response = Response("test response")
    set_auth_cookie(JWT_TEST_KEY, user_id, response)
    assert (cookie_header := response.headers.get("set-cookie")) is not None
    assert (matches := re.match("auth-token=(.*);", cookie_header)) is not None
    return matches[1]


@pytest.fixture
async def get_testdb() -> AsyncGenerator[Connection, None]:
    async with connect(":memory:") as conn:
        conn.row_factory = Row
        await init_connection(conn)
        yield conn


@pytest.fixture
async def test_server(get_testdb: Connection) -> AsyncGenerator[None, None]:
    async def override_db():
        yield get_testdb

    app.state.config = AppConfig(jwt_key=JWT_TEST_KEY, imgbb_key="")
    app.dependency_overrides[get_db] = override_db
    yield
    app.dependency_overrides.clear()


@pytest.mark.parametrize(
    "message,expected",
    [
        (CAS_SUCCESS, "wvam20"),
        (CAS_UNAUTHORIZED_SERVICE, ValueError),
        (CAS_UNAUTHORIZED_SERVICE, ValueError),
        ("sdfghsdkfhgk", ValueError),
        ("", ValueError),
    ],
)
def test_parse_cas_response(message: str, expected: str | ValueError) -> None:
    if expected is ValueError:
        with pytest.raises(ValueError):
            parse_cas_response(message)
    else:
        assert parse_cas_response(message) == expected


def test_jwt() -> None:
    user_id = 100
    auth_cookie = mangle_cookie(user_id)
    app = FastAPI()
    app.state.config = AppConfig(jwt_key=JWT_TEST_KEY, imgbb_key="")

    request = Request(
        scope={
            "type": "http",
            "headers": [(b"cookie", f"auth-token={auth_cookie}".encode("utf-8"))],
            "app": app,
        }
    )
    result_id = authorize(request)
    assert user_id == result_id


async def test_make_user(get_testdb: Connection, test_server: None) -> None:
    client = TestClient(app)
    username = "oh god make it stop"
    row = await get_testdb.execute_insert(
        "INSERT INTO Users (Username) VALUES (?)", (username,)
    )
    assert row is not None
    user_id = row[0]

    auth_cookie = mangle_cookie(user_id)

    user_schema = UserSchema.model_validate(
        client.get("api/auth/session", cookies={"auth-token": auth_cookie}).json()
    )
    assert user_schema.username == username
