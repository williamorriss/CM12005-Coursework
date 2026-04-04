from aiosqlite import Connection, Row
from db import get_db, owns_plant, owns_sensor
from fastapi import APIRouter, Depends
from . import authorize
from fastapi import HTTPException
from fastapi.requests import Request
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/logging")

LOG_FIELDS = {"temperature", "ph", "inserted_timestamp" }

class Log(BaseModel):
    temperature: float | None
    ph: float | None
    collected_timestamp: datetime | None

    @staticmethod
    def from_row(row: Row) -> "Log":
        return Log(
            temperature=row["Temperature"],
            ph=row["pH"],
            collected_timestamp=row["CollectedTimestamp"],
        )


def get_log_fields(request: Request) -> list[str]:
    out = []
    for v in request.query_params.getlist("include"):
        if v in LOG_FIELDS:
            out.append(v)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown log field {v}")

    return out if out else list(LOG_FIELDS)


@router.get("/", response_model=list[Log])
async def get_logs(
    plant_id: int | None = None,
    sensor_id: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    include: list[str] = Depends(get_log_fields),
    user_id: int = Depends(authorize),
    db: Connection = Depends(get_db),
) -> list[Log]:
    if plant_id is not None:
        if not await owns_plant(user_id, plant_id, db):
            raise HTTPException(status_code=401, detail="Does not own plant.")

    if sensor_id is not None:
        if not await owns_sensor(user_id, sensor_id, db):
            raise HTTPException(status_code=401, detail="Does not own sensor.")

    fields = ",".join(include)

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
        return list(map(Log.from_row, logs))