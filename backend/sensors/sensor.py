from typing import cast

from pydantic import BaseModel
from starlette import status
from starlette.responses import Response

from . import Sensor
from aiosqlite import Connection, Row
from db import get_db
from fastapi import APIRouter, Depends
from auth import authorize
from fastapi import HTTPException
from fastapi.requests import Request


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
        sensor_id = row["id"]
        name = row["name"]
        plant_id = row["plant_id"]
        return SensorView(sensor_id=sensor_id, name=name, plant_id=plant_id)

@router.post("/sensors/{sensor_id}/session")
async def activate_sensor(
    sensor_id: int,
    _user_id: int = Depends(authorize), # authorized endpoint
    sensors: dict[int, Sensor] = Depends(get_sensors),
    db: Connection = Depends(get_db),
) -> Response:
    if sensor_id in sensors.keys():
        # already running
        sensors[sensor_id].start()
        return Response(status_code=status.HTTP_304_NOT_MODIFIED, content={"message": "Sensor already active"})

    async with db.execute("""
        SELECT PlantID, Name FROM Sensors WHERE ID = ? 
    """, (sensor_id,)) as cursor:
        row = await cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Sensor not found")

    sensor = TestSensor.from_row(row)
    sensor.start()
    sensors[sensor_id] = sensor

    return Response(status_code=status.HTTP_200_OK_CREATED, content={"message": f"Sensor {sensor_id} activated"})


@router.delete("/sensors/{sensor_id}/session")
async def deactivate_sensor(
    sensor_id: int,
    _user_id: int = Depends(authorize), # authorized endpoint
    sensors: dict[int, Sensor] = Depends(get_sensors),
) -> Response:
    if sensor_id in sensors.keys():
        sensor = sensors[sensor_id]
        sensor.stop()
        return Response(
            status_code=status.HTTP_200_OK,
            content={"message": f"Sensor {sensor_id} deactivated"}
        )

    raise HTTPException(status_code=404, detail="Sensor not found")

@router.post("/sensors")
async def add_sensor (
    name: str,
    user_id: int = Depends(authorize), # authorized endpoint
    plant_id: int | None = None,
    db: Connection = Depends(get_db),
) -> Response:
    async with db.execute("""
        INSERT INTO Sensors (UserID, PlantID, Name) VALUES (?, ?, ?)
    """, (user_id, plant_id, name)) as cursor:
        sensor_id= cursor.lastrowid
        await db.commit()

    return Response(
        status_code=status.HTTP_201_CREATED,
        content={"message": f"Sensor {sensor_id} added"}
    )

@router.delete("/sensors/{sensor_id}")
async def del_sensor (
    sensor_id: int,
    db: Connection = Depends(get_db),
) -> Response:
    async with db.execute("""
         DELETE FROM Sensors WHERE ID = ? 
    """, (sensor_id,)) :
        await db.commit()

    return Response(
        status_code=status.HTTP_200_OK,
        content={"message": f"Sensor {sensor_id} deleted"}
    )

@router.patch("/sensors/{sensor_id}")
async def update_sensor(
    sensor_id: int,
    plant_id: int | None = None,
    name: str | None = None,
    db: Connection = Depends(get_db),
) -> Response:
    if plant_id:
        await db.execute("""
            UPDATE Sensors SET PlantID = ? WHERE ID = ?
        """, (plant_id, sensor_id))

    if name:
        await db.execute("""
            UPDATE Sensors SET Name = ? WHERE ID = ?
        """, (name, sensor_id))

    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)