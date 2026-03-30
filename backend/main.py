from fastapi.responses import FileResponse
from auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

import aiosqlite
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from extract import DBNAME

DEV_SERVER = "http://localhost:5173"
ORIGIN = "http://localhost:8000"
CAS_ORIGIN = "https://auth.bath.ac.uk"

@asynccontextmanager
async def lifespan(_app: FastAPI):
    import os
    print(os.getcwd())

    try:
        with open("backend/schema.sql", 'r') as schema_file:
            schema_sql = schema_file.read()
            async with aiosqlite.connect(DBNAME) as db:
                await db.executescript(schema_sql)
                await db.commit()
                print(f"Schema applied")
    except FileNotFoundError:
        with open("schema.sql", 'r') as schema_file:
            schema_sql = schema_file.read()
            async with aiosqlite.connect(DBNAME) as db:
                await db.executescript(schema_sql)
                await db.commit()
                print(f"Schema applied")

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