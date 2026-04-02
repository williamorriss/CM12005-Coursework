import os
from typing import cast
from fastapi import Request, Form

from aiosqlite import Connection, Row
from fastapi.responses import Response
from starlette.responses import JSONResponse

from db import get_db
from fastapi import APIRouter, Depends, status, UploadFile, File
from auth import authorize
from fastapi import HTTPException
from pydantic import BaseModel
from datetime import datetime
import httpx

router = APIRouter(prefix="/plants")

def get_imgbb_api_key(request: Request) -> str:
    return cast(str, request.app.state.IMGBB_API_KEY)

class PlantView(BaseModel):
    id: int
    name: str
    image_url: str | None

    @staticmethod
    def from_row(row: Row) -> "PlantView":
        return PlantView(
            id=row["ID"],
            name=row["Name"],
            image_url=row["ImageURL"]
        )

class NoteView(BaseModel):
    id: int
    note: str
    rating: int
    timestamp: datetime

    @staticmethod
    def from_row(row: Row) -> "NoteView":
        return NoteView(
            id=row["ID"],
            note=row["Note"],
            rating=row["rating"],
            timestamp=row["timestamp"]
        )

@router.get("", response_model=list[PlantView])
async def get_plants(
    user_id: int = Depends(authorize),
    db: Connection = Depends(get_db)
) -> list[PlantView]:
    async with db.execute_fetchall("""
        SELECT Plants.ID as ID, Name, URL as ImageURL FROM Plants
        LEFT JOIN Images ON Plants.ImageID = Images.ID
        WHERE UserID = ?
    """, (user_id, )) as plants:
        return [PlantView.from_row(row) for row in plants]

@router.post("", status_code=status.HTTP_201_CREATED)
async def add_plant(
    name: str = Form(...),
    picture: UploadFile = File(...),
    user_id: int = Depends(authorize),
    imgbb_api_key: str = Depends(get_imgbb_api_key),
    db: Connection = Depends(get_db)
) -> PlantView:
    url, delete_url = await make_static_url(imgbb_api_key, picture)
    image_id  = row[0] if (row := await db.execute_insert(
        "INSERT INTO Images(URL, DeleteURL) VALUES (?, ?)",
        (url, delete_url)
    )) else None

    if image_id is None:
        raise HTTPException(status_code=500, detail="Failed to create image resource")

    plant_id = cast(int, row[0]) if (row := await db.execute_insert(
        "INSERT INTO Plants(Name, UserID, ImageID) VALUES (?, ?, ?)"
        , (name, user_id, image_id)
    )) else None

    if plant_id is None:
        raise HTTPException(status_code=500, detail="Failed to create plant")

    await db.commit()
    return PlantView(
        id=plant_id,
        name=name,
        image_url = url
    )

# notes

@router.get("/{plant_id}/notes", response_model=list[NoteView])
async def get_notes(
    plant_id: int,
    user_id: int = Depends(authorize),
    db: Connection = Depends(get_db)
) -> list[NoteView]:
    if not await owns_plant(user_id, plant_id, db):
        raise HTTPException(status_code=404, detail="Plants does not belong to this user")

    async with db.execute_fetchall("""
       SELECT ID, Note, Rating, Timestamp FROM Notes WHERE PlantID = ?
       """, (user_id, )) as notes:
        return [NoteView.from_row(note) for note in notes]

@router.post("/{plant_id}/notes", status_code=status.HTTP_201_CREATED)
async def post_note(
    plant_id: int,
    note: str = Form(...),
    rating: int = Form(...),
    user_id: int = Depends(authorize),
    db: Connection = Depends(get_db)
) -> NoteView:
    if not await owns_plant(user_id, plant_id, db):
        raise HTTPException(status_code=404, detail="Plants does not belong to this user")

    async with db.execute_insert("""
        INSERT INTO Notes(PlantID, Note, Rating) VALUES (?, ?, ?, ?) RETURNING ID, Timestamp
    """, (plant_id, note, rating, datetime.now())) as row:
        assert row is not None
        note_id = row[0]
        timestamp = row[1]
        await db.commit()

    return NoteView(
        id=note_id,
        note=note,
        rating=rating,
        timestamp=timestamp
    )

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


    json_reponse = response.json()
    if not json_reponse["success"]:
        raise HTTPException(status_code=500, detail="Provider failed to make static url")

    print(json_reponse)
    data = json_reponse["data"]
    delete_url = data["delete_url"]
    url = data["url"]
    return (url, delete_url)

async def owns_plant(user_id: int, plant_id: int, db: Connection) -> bool:
    async with db.execute(
        "SELECT EXISTS(SELECT 1 FROM Plants WHERE UserID = ? AND ID = ?)",
        (user_id, plant_id)
    ) as cursor:
        row = await cursor.fetchone()
        assert row is not None
        return bool(cast(int, row[0]))