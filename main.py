from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import aiosqlite
from fastapi import FastAPI
from auth import router as auth_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Here so a single db connection can be used throughout the server lifetime.
    application.state.ORIGIN = "http://127.0.0.1:8000"
    application.state.CAS_ORIGIN = "https://auth.bath.ac.uk"
    application.state.ALLOWED_ORIGINS = [application.state.ORIGIN] # add frontend dev server here
    application.state.db = await aiosqlite.connect("test.db")
    yield
    await app.state.db.close()

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)

@app.get("/")
async def index():
    return FileResponse("index.html")