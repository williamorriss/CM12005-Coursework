from fastapi import FastAPI
from starlette.responses import FileResponse

from auth import router as auth_router

ORIGIN: str = "http://127.0.0.1:8000"

app = FastAPI()

app.include_router(auth_router)

@app.get("/")
async def index():
    return FileResponse("index.html")