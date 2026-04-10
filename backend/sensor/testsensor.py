from datetime import datetime, timedelta
from aiosqlite import Row
import numpy as np
import asyncio
import aiosqlite
from sensor.sensor import Sensor, Sample
from db import DBNAME
from random import randrange

def fake_sample() -> Sample:
    temperature = randrange(-10, 40)
    ph = randrange(0, 14)
    return Sample(temperature, ph, datetime.now())

class TestSensor(Sensor):
    def __init__(self, sensor_id: int, plant_id: int, name: str):
        self._name = name
        self._sensor_id = sensor_id
        self._plant_id = plant_id
        self._aggregate_delay = timedelta(seconds=3)
        self._task: asyncio.Task[None] | None = None
        self._watchers: list[asyncio.Queue[Sample]] = []

    @staticmethod
    def from_row(row: Row) -> "TestSensor":
        return TestSensor(
            sensor_id=row["SensorID"],
            plant_id=row["Plant_id"],
            name=row["Name"]
        )

    def start(self) -> None:
        print(f"{self._name} {self._sensor_id} RUNNING")
        self._task = asyncio.create_task(self._process())

    def stop(self) -> None:
        if self._task:
            self._task.cancel()
            self._task = None

    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()

    def set_target(self, plant_id: int) -> None:
        self._plant_id = plant_id

    def add_watcher(self, queue: asyncio.Queue[Sample]) -> None:
        self._watchers.append(queue)

    def remove_watcher(self, queue: asyncio.Queue[Sample]) -> None:
        self._watchers.remove(queue)

    async def _process(self) -> None:
        samples: list[Sample] = []
        next_write = datetime.now() + self._aggregate_delay

        try:
            while True:
                if datetime.now() > next_write:
                    if samples:
                        collated = TestSensor._collate(np.array(samples))
                        await self._db_writer(collated)
                        await self._push_collated(collated)

                    samples.clear()
                    next_write = datetime.now() + self._aggregate_delay

                samples.append(fake_sample())
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    async def _push_collated(self, collated: Sample) -> None:
        for listener in self._watchers:
            await listener.put(collated)

    @staticmethod
    def _collate(samples: np.ndarray) -> Sample:
        return Sample(
            float(samples[:, 0].mean()),
            float(samples[:, 1].mean()),
            samples[:, 2].max()
        )

    async def _db_writer(self, collated: Sample) -> None:
        print(f"WRITING {collated}")

        async with aiosqlite.connect(DBNAME) as db:
            temp, ph, timestamp = collated
            await db.execute(
                "INSERT INTO Logs (SensorID, PlantID, temperature, pH, CollectedTimestamp) VALUES (?, ?, ?, ?, ?)",
                (self._sensor_id, self._plant_id, temp, ph, timestamp)
            )
            await db.commit()