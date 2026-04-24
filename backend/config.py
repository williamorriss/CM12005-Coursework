from typing import Final, cast, ClassVar
from dataclasses import dataclass
from fastapi.requests import Request

ORIGIN: Final[str] = "http://localhost:5173"

@dataclass(frozen=True)
class AppConfig:
    origin: str
    jwt_key: str
    imgbb_key: str
    allowed_origins: tuple[str, ...] = ()
    cas_origin: str = "https://auth.bath.ac.uk"
    _instance: ClassVar["AppConfig | None"] = None

    def __new__(cls, *args, **kwargs) -> "AppConfig":
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(
        self,
        jwt_key: str,
        imgbb_key: str,
        origin: str = ORIGIN,
        allowed_origins: tuple[str, ...] = (ORIGIN,),
        cas_origin: str = "https://auth.bath.ac.uk"
    ) -> None:
        if hasattr(self, "origin"):
            return
        # bypassing frozen
        object.__setattr__(self, "origin", origin)
        object.__setattr__(self, "jwt_key", jwt_key)
        object.__setattr__(self, "imgbb_key", imgbb_key)
        object.__setattr__(self, "allowed_origins", allowed_origins)
        object.__setattr__(self, "cas_origin", cas_origin)

    # extractors
    @staticmethod
    def get_config(request: Request) -> "AppConfig":
        return cast(AppConfig, request.app.state.config)
