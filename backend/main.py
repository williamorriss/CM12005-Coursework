from fastapi.responses import FileResponse
import aiosqlite
from contextlib import asynccontextmanager
from extract import DBNAME

from fastapi import FastAPI
from auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from physical.testsensor import TestSensor

DEV_SERVER = "http://localhost:5173"
ORIGIN = "http://localhost:8000"
CAS_ORIGIN = "https://auth.bath.ac.uk"

@asynccontextmanager
async def lifespan(_app: FastAPI):
    test_sensor = TestSensor(plant_id=0)
    test_sensor.start()

    await init_db()
    yield

async def init_db():
    with open("sql/schema.sql", 'r') as schema_file:
        schema_sql = schema_file.read()
        async with aiosqlite.connect(DBNAME) as db:
            await db.execute("PRAGMA journal_mode=WAL") # Write Ahead Log for concurrent read/ writes
            await db.execute("PRAGMA busy_timeout=1000")
            await db.execute("PRAGMA synchronous=NORMAL")
            await db.executescript(schema_sql)
            await db.commit()
            print(f"Schema applied")

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
app.include_router(auth_router, prefix="/api")

@app.get("/")
async def index():
    return FileResponse("index.html")