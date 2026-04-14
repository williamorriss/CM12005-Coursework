from typing import cast
from fastapi import Request, Form, BackgroundTasks

from aiosqlite import Connection, Row
from starlette.responses import Response

from achievements import AchievementSystem
from db import get_db, owns_plant
from fastapi import APIRouter, Depends, status, UploadFile, File
from api.auth import authorize
from fastapi import HTTPException
from pydantic import BaseModel
import httpx

router = APIRouter(prefix="/plants")

def get_imgbb_api_key(request: Request) -> str:
    return cast(str, request.app.state.IMGBB_API_KEY)

class PlantSchema(BaseModel):
    id: int
    name: str
    image_url: str | None

    @staticmethod
    def from_row(row: Row) -> "PlantSchema":
        return PlantSchema(
            id=row["ID"],
            name=row["Name"],
            image_url=row["ImageURL"]
        )

@router.get("", response_model=list[PlantSchema])
async def get_plants(
    user_id: int = Depends(authorize),
    db: Connection = Depends(get_db)
) -> list[PlantSchema]:
    async with db.execute_fetchall("""
        SELECT Plants.ID as ID, Name, URL as ImageURL FROM Plants
        LEFT JOIN Images ON Plants.ImageID = Images.ID
        WHERE UserID = ?
    """, (user_id, )) as plants:
        return [PlantSchema.from_row(row) for row in plants]

@router.get("/{plant_id}", response_model=PlantSchema)
async def get_plant(
    plant_id: int,
    user_id: int = Depends(authorize),
    db: Connection = Depends(get_db)
) -> PlantSchema:
    if not await owns_plant(user_id, plant_id, db):
        raise HTTPException(status_code=401, detail="Plant does not belong to this user")

    async with db.execute("""
       SELECT Plants.ID as ID, Name, URL as ImageURL FROM Plants
        LEFT JOIN Images ON Plants.ImageID = Images.ID
       WHERE Plants.ID = ?
    """, (plant_id, )) as cursor:
        row = await cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Plant does not exist")
        return PlantSchema.from_row(row)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=PlantSchema)
async def add_plant(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    picture: UploadFile | None = File(...),
    user_id: int = Depends(authorize),
    imgbb_api_key: str = Depends(get_imgbb_api_key),
    db: Connection = Depends(get_db),
    achievement_system: AchievementSystem = Depends(AchievementSystem),
) -> PlantSchema:
    image_id: int | None = None
    url: str | None = None
    if picture is not None and picture.size != 0:
        url, delete_url = await make_static_url(imgbb_api_key, picture)
        if (row := await db.execute_insert(
            "INSERT INTO Images(URL, DeleteURL) VALUES (?, ?)",
            (url, delete_url)
        )) is None:
            raise HTTPException(status_code=500, detail="Failed to create image resource")
        image_id = row[0]

    if (row := await db.execute_insert(
        "INSERT INTO Plants(Name, UserID, ImageID) VALUES (?, ?, ?)"
    , (name, user_id, image_id)
    )) is None:
        raise HTTPException(status_code=500, detail="Failed to create plant")

    plant_id = row[0]

    await db.commit()
    background_tasks.add_task(achievement_system.plant_achievements, user_id) # use background task just in case achievements become slower
    return PlantSchema(
        id=plant_id,
        name=name,
        image_url = url
    )

@router.delete("/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plant(
    plant_id: int,
    user_id: int = Depends(authorize),
    db: Connection = Depends(get_db)
) -> Response:
    if not await owns_plant(user_id, plant_id, db):
        raise HTTPException(status_code=404, detail="Plants does not belong to this user")

    await delete_image(plant_id, db)
    await db.execute("DELETE FROM Plants WHERE ID = ?", (plant_id,))
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def delete_image(plant_id: int, db: Connection) -> None:
    async with db.execute("SELECT ImageID FROM Plants WHERE ID = ?", (plant_id,)) as cursor:
        row = await cursor.fetchone()
    if row is None or (image_id := row[0]) is None:
        return

    async with db.execute("SELECT DeleteUrl FROM Images WHERE ID = ?", (image_id,)) as cursor:
        row = await cursor.fetchone()
    if row is None or (delete_url := row[0]) is None:
        raise HTTPException(status_code=500, detail="Image resource has no delete URL")

    async with httpx.AsyncClient() as client:
        response = await client.delete(delete_url)
        if response.is_error:
            raise HTTPException(status_code=500, detail="Could not delete image")

    await db.execute("DELETE FROM Images WHERE ID = ?", (image_id,))
    await db.commit()

async def make_static_url(api_key: str, file: UploadFile) -> tuple[str, str]:
    files = { "image" : await file.read() } # per api spec it MUST be "image"
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.imgbb.com/1/upload?key={api_key}",
            files = files,
            data={ "name" : file.filename }
        )

    if response.is_error:
        raise HTTPException(status_code=500, detail="Could not make static url")


    json_response = response.json()
    if not json_response["success"]:
        raise HTTPException(status_code=500, detail="Provider failed to make static url")

    print(json_response)
    data = json_response["data"]
    delete_url = data["delete_url"]
    url = data["url"]
    return url, delete_url