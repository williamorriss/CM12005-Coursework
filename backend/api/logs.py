from aiosqlite import Connection, Row
from db import get_db, owns_plant, owns_sensor
from fastapi import APIRouter, Depends
from api.auth import authorize
from fastapi import HTTPException
from fastapi.requests import Request
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/logging")


class LogView(BaseModel):
    temperature: float | None
    ph: float | None
    collected_timestamp: datetime | None

    @staticmethod
    def from_row(row: Row) -> "LogView":
        return LogView(
            temperature=row["Temperature"],
            ph=row["pH"],
            collected_timestamp=row["CollectedTimestamp"],
        )

class LogField(str, Enum):
    temperature = "temperature"
    ph = "ph"
    inserted_timestamp = "inserted_timestamp"


@router.get("/", response_model=list[LogView])
async def get_logs(
    plant_id: int | None = None,
    sensor_id: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    include: list[LogField] | None = None,
    user_id: int = Depends(authorize),
    db: Connection = Depends(get_db),
) -> list[LogView]:
    if plant_id is not None:
        if not await owns_plant(user_id, plant_id, db):
            raise HTTPException(status_code=401, detail="Does not own plant.")

    if sensor_id is not None:
        if not await owns_sensor(user_id, sensor_id, db):
            raise HTTPException(status_code=401, detail="Does not own sensor.")

    fields = ",".join(include) if include else "*"

    async with db.execute_fetchall(f"""
        SELECT {fields} FROM Logs 
        WHERE UserID = ? 
        AND (PlantID = :plant_id OR ? IS NULL)
        AND (SensorID = :sensor_id OR :sensor_id IS NULL)
        AND (created_at >= :date_from OR :date_from IS NULL)
        AND (created_at <= :date_to  OR :date_to IS NULL)
    """, {
        "plant_id": plant_id,
        "sensor_id": sensor_id,
        "date_from": date_from,
        "date_to": date_to,
    } ) as logs:
        return list(map(LogView.from_row, logs))