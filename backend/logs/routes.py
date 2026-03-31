# from typing import Any
#
# from aiosqlite import Connection, Row
# from db import get_db
# from fastapi import APIRouter, Depends
# from auth import authorize
# from fastapi.responses import RedirectResponse, Response
# from fastapi import HTTPException
# import httpx
# from fastapi.requests import Request
# from pydantic import BaseModel
# from datetime import datetime, timedelta, timezone
# from datetime import datetime
# from logs.sensor import Sensor
# import multiprocessing
#
# router = APIRouter(prefix="/")
#
# LOG_FIELDS = {"temperature", "ph", "inserted_timestamp" }
# 
# class Log(BaseModel):
#     temperature: float | None
#     ph: float | None
#     collected_timestamp: datetime | None
#     inserted_timestamp: datetime | None
#
#     @staticmethod
#     def from_row(row: Row) -> "Log":
#         temperature = getattr(row, "temperature")
#         ph = getattr(row, "ph")
#         inserted_timestamp = getattr(row, "inserted_timestamp")
#         return Log(temperature=temperature, ph=ph, collected_timestamp=inserted_timestamp)
#
#
#
#
# def _get_from_row(row: Row, key: str) -> Any | None:
#     if key in row.keys():
#         return row[key]
#     else:
#         return None
#
# def get_log_fields(request: Request) -> list[str]:
#     out = []
#     for v in request.query_params.getlist("include"):
#         if v in LOG_FIELDS:
#             out.append(v)
#         else:
#             raise HTTPException(status_code=400, detail=f"Unknown log field {v}")
#
#     return out if out else list(LOG_FIELDS)
#
#
# @router.get("/", response_model=list[Log])
# async def get_logs(
#     user_id = Depends(authorize),
#     db: Connection = Depends(get_db),
#     plant_id = int,
#     include: list[str] = Depends(get_log_fields),
#     date_from: datetime | None = None,
#     date_to: datetime | None = None,
# ) -> list[Log]:
#     date_start = date_from if date_from else datetime.min
#     date_end = date_to if date_to else datetime.max
#     fields = ",".join(include)
#
#     async with db.execute_fetchall(f"""
#         SELECT {fields} FROM Logs WHERE UserID = ? AND PlantID = ? AND InsertTimestamp BETWEEN ? AND ?
#     """, (user_id, plant_id, date_start, date_end)) as logs:
#         return list(map(Log.from_row, logs))
#
#
# @router.get("/sensors", response_model=list[SensorView])
# async def get_sensors (
#     user_id = Depends(authorize),
#     db: Connection = Depends(get_db),
# ):
#     async with db.execute_fetchall("""
#         SELECT ID, PlantID, Name FROM Sensors WHERE UserID = ?
#     """, (user_id, )) as sensors:
#         return list(map(SensorView.from_row, sensors))