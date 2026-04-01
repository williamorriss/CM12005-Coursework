from aiosqlite import Connection, Row

from db import get_db
from fastapi import APIRouter, Depends
from auth import authorize
from fastapi import HTTPException
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/plants")

class PlantView(BaseModel):
    id: int
    name: str

    @staticmethod
    def from_row(row: Row) -> "PlantView":
        return PlantView(id=row["ID"], name=row["Name"])

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
    user_id = Depends(authorize),
    db: Connection = Depends(get_db)
) -> list[PlantView]:
    async with db.execute_fetchall("""
        SELECT ID, Name FROM Plants WHERE UserID = ?
    """, (user_id, )) as plants:
        return [PlantView.from_row(row) for row in plants]

@router.post("")
async def add_plant(
    name: str,
    user_id = Depends(authorize),
    db: Connection = Depends(get_db)
):
    async with db.execute_insert("""
        INSERT INTO Plants(Name, UserID) VALUES (?, ?) 
    """, (name, user_id)):
        await db.commit()

# notes

@router.get("/{plant_id}/notes", response_model=list[NoteView])
async def get_notes(
    plant_id: int,
    user_id = Depends(authorize),
    db: Connection = Depends(get_db)
) -> list[NoteView]:
    if not await owns_plant(user_id, plant_id, db):
        raise HTTPException(status_code=404, detail="Plants does not belong to this user")

    async with db.execute_fetchall("""
       SELECT ID, Note, Rating, Timestamp FROM Notes WHERE PlantID = ?
       """, (user_id, )) as notes:
        return [NoteView.from_row(note) for note in notes]

@router.post("/{plant_id}/notes")
async def post_note(
    plant_id: int,
    note: str,
    rating: int,
    user_id = Depends(authorize),
    db: Connection = Depends(get_db)
):
    if not await owns_plant(user_id, plant_id, db):
        raise HTTPException(status_code=404, detail="Plants does not belong to this user")

    async with db.execute_insert("""
        INSERT INTO Notes(PlantID, Note, Rating, Timestamp) VALUES (?, ?, ?, ?)
    """, (plant_id, note, rating, datetime.now())):
        await db.commit()


async def owns_plant(user_id: int, plant_id: int, db: Connection) -> bool:
    async with db.execute(
        "SELECT EXISTS(SELECT 1 FROM Plants WHERE UserID = ? AND ID = ?)",
        (user_id, plant_id)
    ) as cursor:
        row = await cursor.fetchone()
        return bool(row[0])