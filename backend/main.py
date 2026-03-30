from fastapi.responses import FileResponse
from fastapi import FastAPI
from auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from extract import get_db
import aiosqlite
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI

DEV_SERVER = "http://localhost:5173"
ORIGIN = "http://localhost:8000"
CAS_ORIGIN = "https://auth.bath.ac.uk"

@asynccontextmanager
async def lifespan(_app: FastAPI):
    db: aiosqlite.Connection = await anext(get_db())
    schema_file = Path("schema.sql")

    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found")

    schema_sql = schema_file.read_text(encoding="utf-8")

    async with db.executescript(schema_sql):
        await db.executescript(schema_sql)
        await db.commit()
        print(f"✅ Schema applied successfully to")
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
app.include_router(auth_router, prefix="/api")

@app.get("/")
async def index():
    return FileResponse("index.html")