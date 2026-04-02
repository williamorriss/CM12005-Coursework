import os
from typing import Any, AsyncGenerator
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from db import init_db

from fastapi import FastAPI
from auth import router as auth_router
from sensors import router as sensors_router
from plants import router as plant_router
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

DEV_SERVER = "http://localhost:5173"
ORIGIN = "http://localhost:8000"
CAS_ORIGIN = "https://auth.bath.ac.uk"

@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, Any]:
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=[DEV_SERVER],
    allow_credentials=True,
    allow_headers=["AUTHORIZATION", "CONTENT_TYPE", "COOKIE", "ACCEPT"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

signing_key = os.getenv("SIGNING_KEY")
imgbb_key = os.getenv("IMGBB_KEY")
assert signing_key and imgbb_key

# this is kind of terrible and should be made into a config class so they
# actually have types
app.state.ORIGIN = ORIGIN
app.state.CAS_ORIGIN = CAS_ORIGIN
app.state.ALLOWED_ORIGINS = [app.state.ORIGIN, DEV_SERVER]
app.state.JWT_SIGNING_KEY = signing_key
app.state.IMGBB_API_KEY = imgbb_key
app.state.sensors = {}
app.include_router(auth_router, prefix="/api")
app.include_router(sensors_router, prefix="/api")
app.include_router(plant_router, prefix="/api")

@app.get("/")
async def index() -> FileResponse:
    return FileResponse("index.html")