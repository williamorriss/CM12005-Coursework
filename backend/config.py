from typing import Final, NamedTuple, cast

from fastapi.requests import Request

ORIGIN: Final[str] = "http://localhost:5173"


class AppConfig(NamedTuple):
    """
    Immutable structure to hold the current configuration of the server
    """

    jwt_key: str
    imgbb_key: str
    origin: str = ORIGIN
    allowed_origins: tuple[str, ...] = ()
    cas_origin: str = "https://auth.bath.ac.uk"


# extractors
def get_config(request: Request) -> "AppConfig":
    """
    Extractor to get the current configuration of the server

    ```python
        config: AppConfig = Depends(get_config)
    ```
    """
    return cast(AppConfig, request.app.state.config)
