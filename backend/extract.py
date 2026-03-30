# Extractors for `Request` used for dependency injection
from typing import Any, AsyncGenerator

from fastapi import Request, HTTPException
from aiosqlite import Connection, connect
import jwt

DBNAME = "test.db"

async def get_db(_r: Request) -> AsyncGenerator[Connection, Any]:
    async with connect("test.db") as db:
        yield db

def get_allowed_origins(request: Request) -> list[str]:
    return request.app.state.ALLOWED_ORIGINS

def get_cas_origin(request: Request) -> str:
    return request.app.state.CAS_ORIGIN

def get_origin(request: Request) -> str:
    return request.app.state.ORIGIN

def get_auth_key(request: Request) -> str:
    return request.app.state.KEY

def authorize(request: Request) -> int:
    auth_token = request.cookies.get("auth-token")
    if auth_token is None:
        raise HTTPException(status_code=401, detail="No auth token")

    try:
        claims = jwt.decode(
            jwt=auth_token,
            key=get_auth_key(request),
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid auth token")

    return claims["user_id"]