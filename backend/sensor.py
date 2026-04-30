from asyncio import CancelledError, Task, create_task, sleep
from asyncio.queues import Queue
from contextlib import AbstractAsyncContextManager
from datetime import datetime
from random import randrange
from typing import Callable, NamedTuple

from aiosqlite import Connection

from db import get_db_contextmanager


class Sample(NamedTuple):
    temperature: float
    ph: float
    timestamp: datetime


class Sensor(NamedTuple):
    sensor_id: int
    plant_id: int | None


def fake_sample() -> Sample:
    temperature = randrange(-10, 40)
    ph = randrange(0, 14)
    return Sample(temperature, ph, datetime.now())


class SensorSystem:
    _instance: "SensorSystem | None" = None
    _active: dict[int, Task[None]]
    _listeners: dict[int, list[Queue[Sample]]]
    _get_db: Callable[[], AbstractAsyncContextManager[Connection]]
    _delay: float

    def __new__(
        cls,
        get_db: Callable[
            [], AbstractAsyncContextManager[Connection]
        ] = get_db_contextmanager,
        delay: float = 10,
    ) -> "SensorSystem":
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        assert cls._instance is not None
        return cls._instance

    def __init__(
        self,
        get_db: Callable[
            [], AbstractAsyncContextManager[Connection]
        ] = get_db_contextmanager,
        delay: float = 10,
    ) -> None:
        if hasattr(self, "_active"):  # already initialised
            return

        self._delay = delay
        self._get_db = get_db
        self._active = {}
        self._listeners = {}

    def is_active(self, sensor_id: int) -> bool:
        return sensor_id in self._active

    async def sense(self, sensor_id: int) -> None:
        print(f"{sensor_id} started sensing")
        try:
            sensor = await self._get_sensor(sensor_id)
            while True:
                sample = fake_sample()
                self._broadcast(sensor, sample)
                await self.write_sample(sensor, sample)
                await sleep(self._delay)
        except CancelledError:
            print(f"{sensor_id} stopped")
            pass

    def _broadcast(self, sensor: Sensor, sample: Sample) -> None:
        for listeners in self._listeners[sensor.sensor_id]:
            listeners.put_nowait(sample)

    async def _get_sensor(self, sensor_id: int) -> Sensor:
        async with self._get_db() as db:
            async with db.execute(
                "SELECT PlantID FROM Sensors WHERE ID = ?",
                (sensor_id,),
            ) as cursor:
                row = await cursor.fetchone()
                plant_id = row[0] if row else None

        return Sensor(sensor_id=sensor_id, plant_id=plant_id)

    async def write_sample(self, sensor: Sensor, sample: Sample) -> None:
        print(f"Inserting {sample} for sensor {sensor.sensor_id} ")
        async with self._get_db() as db:
            await db.execute_insert(
                """
                INSERT INTO Logs (
                    SensorID,
                    PlantID,
                    Temperature,
                    pH,
                    CollectedTimestamp
                ) VALUES (?, ?, ?, ?, ?)""",
                (
                    sensor.sensor_id,
                    sensor.plant_id,
                    sample.temperature,
                    sample.ph,
                    sample.timestamp,
                ),
            )

            await db.commit()

    def attach_sensor(self, sensor_id: int) -> Queue[Sample]:
        queue: Queue[Sample] = Queue()
        # listeners array may be empty if attatching to a sensor that has
        # not been activated/ attached to this session
        self._listeners.setdefault(sensor_id, []).append(queue)
        return queue

    def detatch_sensor(self, sensor_id: int, queue: Queue[Sample]) -> None:
        self._listeners[sensor_id] = [
            q for q in self._listeners[sensor_id] if q is not queue
        ]  # `is not` for reference

    async def activate_sensor(self, sensor_id: int) -> None:
        if sensor_id in self._active:
            raise Exception("Sensor already active")

        # activate sensor
        task = create_task(self.sense(sensor_id))
        # make sure sensor errors actually appear
        task.add_done_callback(lambda task: task.result())
        self._active[sensor_id] = task

    def deactivate_sensor(self, sensor_id: int) -> None:
        if sensor_id not in self._active:
            raise Exception("Sensor not active")

        self._active[sensor_id].cancel()
        del self._active[sensor_id]
        if len(self._listeners[sensor_id]) == 0:
            del self._listeners[sensor_id]
