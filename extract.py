# Extractors for `Request` used for dependency injection

from fastapi import Request
from aiosqlite import Connection

def get_db(request: Request) -> Connection:
    return request.app.state.db

def get_allowed_origins(request: Request) -> list[str]:
    return request.app.state.ALLOWED_ORIGINS

def get_cas_origin(request: Request) -> str:
    return request.app.state.CAS_ORIGIN

def get_origin(request: Request) -> str:
    return request.app.state.ORIGIN