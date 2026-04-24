from db import init_db
from typing import Any, AsyncGenerator, cast, Final
from fastapi import FastAPI
from contextlib import asynccontextmanager
from api import router
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from config import AppConfig

load_dotenv()

@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, Any]:
    await init_db()
    yield

# signing_key = os.getenv("SIGNING_KEY")
# imgbb_key = os.getenv("IMGBB_KEY")
config = AppConfig(
    jwt_key="aeui4baibviruabirbviruiadbiburbaiurbaiuriabir213io3u4iu23o4u23oiu4",
    imgbb_key="f7616c52863e992deb9e183c38a22468"
)

app = FastAPI(lifespan=lifespan)

app.include_router(router)

# technically not needed
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(config.allowed_origins),
    allow_credentials=True,
    allow_headers=["AUTHORIZATION", "CONTENT_TYPE", "COOKIE", "ACCEPT"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

app.state.config = config
