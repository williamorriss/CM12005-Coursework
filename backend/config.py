from typing import Final, NamedTuple, cast

from fastapi.requests import Request

ORIGIN: Final[str] = "http://localhost:5173"


class AppConfig(NamedTuple):
    jwt_key: str
    imgbb_key: str
    origin: str = ORIGIN
    allowed_origins: tuple[str, ...] = ()
    cas_origin: str = "https://auth.bath.ac.uk"


# extractors
@staticmethod
def get_config(request: Request) -> "AppConfig":
    return cast(AppConfig, request.app.state.config)
