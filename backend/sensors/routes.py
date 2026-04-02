import asyncio
from collections.abc import AsyncIterable
from datetime import datetime
from typing import cast

from fastapi.sse import EventSourceResponse
from pydantic import BaseModel
from fastapi.responses import Response
from fastapi import status

from . import Sensor, Sample
from aiosqlite import Connection, Row
from db import get_db
from fastapi import Depends
from auth import authorize
from fastapi import Request, APIRouter, HTTPException

from sensors.testsensor import TestSensor

router = APIRouter(prefix="/sensors")

def get_sensors(request: Request) -> dict[int, Sensor]:
    return cast(dict[int, Sensor], request.app.state.sensors)

class SensorView(BaseModel):
    sensor_id: int
    plant_id: int
    name: str

    @staticmethod
    def from_row(row: Row) -> "SensorView":
        sensor_id = row["ID"]
        name = row["Name"]
        plant_id = row["PlantID"]
        return SensorView(sensor_id=sensor_id, name=name, plant_id=plant_id)


class SampleView(BaseModel):
    temperature: float
    ph: float
    timestamp: datetime
    @staticmethod
    def from_sample(sample: Sample) -> "SampleView":
        return SampleView(temperature=sample.temperature, ph=sample.ph, timestamp=sample.timestamp)


@router.get("", response_model=list[SensorView])
async def get_user_sensors(
    user_id: int = Depends(authorize),
    db: Connection = Depends(get_db)
) -> list[SensorView]:
    async with db.execute_fetchall("""
        SELECT ID, PlantID, Name FROM Sensors WHERE UserID = ? 
    """, (user_id,)) as rows:
        return [SensorView.from_row(row) for row in rows]


@router.post("/{sensor_id}/session")
async def activate_sensor(
    sensor_id: int,
    _user_id: int = Depends(authorize), # authorized endpoint
    sensors: dict[int, Sensor] = Depends(get_sensors),
    db: Connection = Depends(get_db),
) -> Response:
    if sensor_id in sensors:
        # already running
        sensors[sensor_id].start()
        return Response(status_code=status.HTTP_201_CREATED)

    async with db.execute("""
        SELECT PlantID, Name FROM Sensors WHERE ID = ? 
    """, (sensor_id,)) as cursor:
        row = await cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Sensor not found")

    sensor = TestSensor.from_row(row)
    sensor.start()
    sensors[sensor_id] = sensor

    return Response(status_code=status.HTTP_201_CREATED, content={"message": f"Started sensor {sensor_id}"})



@router.delete("/{sensor_id}/session")
async def deactivate_sensor(
    sensor_id: int,
    _user_id: int = Depends(authorize), # authorized endpoint
    sensors: dict[int, Sensor] = Depends(get_sensors),
) -> Response:
    if sensor_id not in sensors:
        raise HTTPException(status_code=404, detail="Sensor not found")

    sensor = sensors[sensor_id]
    sensor.stop()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("")
async def add_sensor(
        name: str,
        plant_id: int | None = None,
        user_id: int = Depends(authorize),
        db: Connection = Depends(get_db),
) -> Response:
    async with db.execute(
            "INSERT INTO Sensors (UserID, PlantID, Name) VALUES (?, ?, ?)",
            (user_id, plant_id, name)
    ) as cursor:
        await db.commit()
        sensor_id = cursor.lastrowid

    return Response(
        status_code=status.HTTP_201_CREATED,
        content={"message": f"Created sensor {sensor_id}", "id": sensor_id
         }
    )

@router.delete("/{sensor_id}")
async def del_sensor (
    sensor_id: int,
    _user_id: int = Depends(authorize),
    db: Connection = Depends(get_db),
) -> Response:
    async with db.execute("""
         DELETE FROM Sensors WHERE ID = ? 
    """, (sensor_id,)) :
        await db.commit()

    return Response(
        status_code=status.HTTP_200_OK,
        content={ "message" : f"Deleted sensor {sensor_id}"}
    )

# @router.patch("/{sensor_id}")
# async def update_sensor(
#     sensor_id: int,
#     plant_id: int | None = None,
#     name: str | None = None,
#     _user_id = Depends(authorize),
#     db: Connection = Depends(get_db),
# ):
#     if plant_id:
#         await db.execute("""
#             UPDATE Sensors SET PlantID = ? WHERE ID = ?
#         """, (plant_id, sensor_id))
#
#     if name:
#         await db.execute("""
#             UPDATE Sensors SET Name = ? WHERE ID = ?
#         """, (name, sensor_id))
#
#     await db.commit()

@router.get("/{sensor_id}/stream", response_class=EventSourceResponse)
async def get_sensor_stream(
    request: Request,
    sensor_id: int,
    sensors: dict[int, Sensor] = Depends(get_sensors),
) -> AsyncIterable[SampleView]:
    out: asyncio.Queue[Sample] = asyncio.Queue()
    if sensor_id not in sensors:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor not found")

    sensor = sensors[sensor_id]
    sensor.add_watcher(out)
    try:
        while True:
            if await request.is_disconnected():
                break
            data = SampleView.from_sample(await out.get())
            yield data
    finally:
        sensor.remove_watcher(out)