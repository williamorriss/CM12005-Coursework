from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from db import init_db

from fastapi import FastAPI
from auth import router as auth_router
from sensors import router as sensors_router
from fastapi.middleware.cors import CORSMiddleware


DEV_SERVER = "http://localhost:5173"
ORIGIN = "http://localhost:8000"
CAS_ORIGIN = "https://auth.bath.ac.uk"

@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, # type: ignore
    allow_origins=[DEV_SERVER],
    allow_credentials=True,
    allow_headers=["AUTHORIZATION", "CONTENT_TYPE", "COOKIE", "ACCEPT"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)


app.state.ORIGIN = ORIGIN
app.state.CAS_ORIGIN = CAS_ORIGIN
app.state.KEY = "testkeybpfdgsfgoiabegoabgongebiagiaebgaobxxxxxegiobaeogbieaosbget"
app.state.ALLOWED_ORIGINS = [app.state.ORIGIN, DEV_SERVER]
app.state.sensors = {}
app.include_router(auth_router, prefix="/api")
app.include_router(sensors_router, prefix="/api")

@app.get("/")
async def index():
    return FileResponse("index.html")