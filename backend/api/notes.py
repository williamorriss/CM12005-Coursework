from fastapi import Form
from aiosqlite import Connection, Row
from starlette.responses import Response

from db import get_db, owns_plant
from fastapi import APIRouter, Depends, status
from . import authorize
from fastapi import HTTPException
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/plants/{plant_id}/notes")


class NoteView(BaseModel):
    id: int
    plant_id: int
    note: str
    rating: int
    timestamp: datetime

    @staticmethod
    def from_row(row: Row) -> "NoteView":
        return NoteView(
            id=row["ID"],
            plant_id=row["PlantID"],
            note=row["Note"],
            rating=row["Rating"],
            timestamp=row["Timestamp"]
        )



@router.get("", response_model=list[NoteView])
async def get_notes(
        plant_id: int,
        user_id: int = Depends(authorize),
        db: Connection = Depends(get_db)
) -> list[NoteView]:
    if not await owns_plant(user_id, plant_id, db):
        raise HTTPException(status_code=404, detail="Plants does not belong to this user")

    async with db.execute_fetchall(
            "SELECT ID, PlantID, Note, Rating, Timestamp FROM Notes WHERE PlantID = ?"
            , (plant_id, )) as notes:
        return [NoteView.from_row(note) for note in notes]

@router.post("", status_code=status.HTTP_201_CREATED, response_model=NoteView)
async def post_note(
        plant_id: int,
        note: str = Form(...),
        rating: int = Form(...),
        user_id: int = Depends(authorize),
        db: Connection = Depends(get_db)
) -> NoteView:
    if not await owns_plant(user_id, plant_id, db):
        raise HTTPException(status_code=404, detail="Plants does not belong to this user")

    async with db.execute(
            "INSERT INTO Notes(PlantID, Note, Rating) VALUES (?, ?, ?) RETURNING ID, Timestamp"
            , (plant_id, note, rating)) as cursor:
        if (row := await cursor.fetchone()) is None:
            raise HTTPException(status_code=400, detail="Failed to create note")
        await db.commit()

    note_id, timestamp = row
    return NoteView(
        id=note_id,
        plant_id=plant_id,
        note=note,
        rating=rating,
        timestamp=timestamp
    )

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
        plant_id: int,
        note_id: int,
        user_id: int = Depends(authorize),
        db: Connection = Depends(get_db)
) -> Response:
    if not await owns_plant(user_id, plant_id, db):
        raise HTTPException(status_code=404, detail="Plants does not belong to this user")

    await db.execute("DELETE FROM Notes WHERE ID = ?", (note_id,))
    await db.commit()
    return Response(status_code=204)