from fastapi.responses import FileResponse
from fastapi import FastAPI
from auth import router as auth_router


app = FastAPI()
app.state.ORIGIN = "http://127.0.0.1:8000"
app.state.CAS_ORIGIN = "https://auth.bath.ac.uk"
app.state.KEY = "testkeybpfdgsfgoiabegoabgongebiagiaebgaobxxxxxegiobaeogbieaosbget"
app.state.ALLOWED_ORIGINS = [app.state.ORIGIN] # add frontend dev server here
app.include_router(auth_router)

@app.get("/")
async def index():
    return FileResponse("index.html")