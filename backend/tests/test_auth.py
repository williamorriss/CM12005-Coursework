import pytest
from aiosqlite import Connection
from conftest import JWT_TEST_KEY, mangle_cookie
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.testclient import TestClient

from api.auth import UserSchema, authorize, parse_cas_response
from config import AppConfig
from main import app

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


async def test_make_user(testdb: Connection, test_server: None) -> None:  # noqa: F811
    client = TestClient(app)
    username = "oh god make it stop"
    row = await testdb.execute_insert(
        "INSERT INTO Users (Username) VALUES (?)", (username,)
    )
    assert row is not None
    user_id = row[0]
    client.cookies.set("auth-token", mangle_cookie(user_id))

    user_schema = UserSchema.model_validate(client.get("api/auth/session").json())
    assert user_schema.username == username
