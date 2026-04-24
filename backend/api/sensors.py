from collections.abc import AsyncIterable
from datetime import datetime
from typing import cast

from aiosqlite import Connection, Row
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse, Response
from fastapi.sse import EventSourceResponse
from pydantic import BaseModel

from api.auth import authorize
from db import get_db
from sensor import Sample, SensorSystem

router = APIRouter(prefix="/sensors")


class SensorSchema(BaseModel):
    sensor_id: int
    plant_id: int | None
    name: str

    @staticmethod
    def from_row(row: Row) -> "SensorSchema":
        sensor_id = row["ID"]
        name = row["Name"]
        plant_id = row["PlantID"]
        return SensorSchema(sensor_id=sensor_id, name=name, plant_id=plant_id)


class SampleView(BaseModel):
    temperature: float
    ph: float
    timestamp: datetime

    @staticmethod
    def from_sample(sample: Sample) -> "SampleView":
        return SampleView(
            temperature=sample.temperature, ph=sample.ph, timestamp=sample.timestamp
        )


@router.get("", response_model=list[SensorSchema])
async def get_user_sensors(
    user_id: int = Depends(authorize), db: Connection = Depends(get_db)
) -> list[SensorSchema]:
    async with db.execute_fetchall(
        """
        SELECT ID, PlantID, Name FROM Sensors WHERE UserID = ? 
    """,
        (user_id,),
    ) as rows:
        return [SensorSchema.from_row(row) for row in rows]


@router.post("/{sensor_id}/session", status_code=status.HTTP_200_OK)
async def activate_sensor(
    sensor_id: int,
    user_id: int = Depends(authorize),  # authorized endpoint
    sensors: SensorSystem = Depends(SensorSystem),
    db: Connection = Depends(get_db),
) -> JSONResponse:
    if not (await _owns_sensor(user_id, sensor_id, db)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sensor does not exist, or does not belong to this user",
        )

    if sensors.is_active(sensor_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sensor {sensor_id} is already active",
        )

    try:
        await sensors.activate_sensor(sensor_id)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": f"Sensor {sensor_id} activated"},
    )


@router.delete("/{sensor_id}/session", status_code=status.HTTP_200_OK)
async def deactivate_sensor(
    sensor_id: int,
    user_id: int = Depends(authorize),  # authorized endpoint
    sensors: SensorSystem = Depends(SensorSystem),
    db: Connection = Depends(get_db),
) -> Response:
    if not (await _owns_sensor(user_id, sensor_id, db)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sensor does not exist, or does not belong to this user",
        )

    if not sensors.is_active(sensor_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="sensor is not active"
        )

    sensors.deactivate_sensor(sensor_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Sensor {sensor_id} deactivated"},
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_sensor(
    name: str = Form(...),
    plant_id: int | None = Form(...),
    user_id: int = Depends(authorize),
    db: Connection = Depends(get_db),
) -> SensorSchema:
    async with db.execute(
        "INSERT INTO Sensors (UserID, PlantID, Name) VALUES (?, ?, ?)",
        (user_id, plant_id, name),
    ) as cursor:
        await db.commit()
        sensor_id = cursor.lastrowid

    assert sensor_id is not None

    return SensorSchema(
        sensor_id=sensor_id,
        name=name,
        plant_id=plant_id,
    )


@router.delete("/{sensor_id}", status_code=status.HTTP_200_OK)
async def del_sensor(
    sensor_id: int,
    user_id: int = Depends(authorize),
    db: Connection = Depends(get_db),
) -> Response:
    if not (await _owns_sensor(user_id, sensor_id, db)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sensor does not exist, or does not belong to this user",
        )

    async with db.execute(
        """
         DELETE FROM Sensors WHERE ID = ? 
    """,
        (sensor_id,),
    ):
        await db.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Sensor {sensor_id} deleted"},
    )


@router.get("/{sensor_id}/stream", response_class=EventSourceResponse)
async def get_sensor_stream(
    request: Request,
    sensor_id: int,
    user_id: int = Depends(authorize),
    sensors: SensorSystem = Depends(SensorSystem),
    db: Connection = Depends(get_db),
) -> AsyncIterable[SampleView]:
    if not (await _owns_sensor(user_id, sensor_id, db)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sensor does not exist, or does not belong to this user",
        )

    out = sensors.attach_sensor(sensor_id)

    try:
        while True:
            if await request.is_disconnected():
                break
            data = SampleView.from_sample(await out.get())
            yield data
    finally:
        sensors.detatch_sensor(sensor_id, out)


async def _owns_sensor(user_id: int, sensor_id: int, db: Connection) -> bool:
    async with db.execute(
        "SELECT EXISTS(SELECT 1 FROM Sensors WHERE UserID = ? AND ID = ?)",
        (user_id, sensor_id),
    ) as cursor:
        row = await cursor.fetchone()
    assert row is not None
    return bool(cast(int, row[0]))
