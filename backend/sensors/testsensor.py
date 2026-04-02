from random import randrange
from datetime import datetime, timedelta
import numpy as np
from collections import namedtuple
import multiprocessing
import asyncio
import aiosqlite
from . import Sensor
from db import DBNAME

TestSample = namedtuple("TestSample", ["temperature", "pH", "timestamp"])

def fake_sample() -> TestSample:
    temperature = randrange(-10, 40)
    ph = randrange(0, 14)
    return TestSample(temperature, ph, datetime.now())

class TestSensor(Sensor):
    def __init__(self, sensor_id: int, plant_id: int, name: str):
        self.name = name
        self.sensor_id = sensor_id
        self.plant_id = plant_id
        self.aggregate_delay = timedelta(minutes=1)
        self._stop_event = multiprocessing.Event()

    def start(self):
        self._stop_event.clear()
        multiprocessing.Process(target=self._run, daemon=True).start()

    def stop(self):
        self._stop_event.set()

    def is_running(self) -> bool:
        return not self._stop_event.is_set()

    def set_target(self, plant_id: int):
        self.plant_id = plant_id

    def _run(self):
        asyncio.run(self._process())

    async def _process(self):
        samples = []
        next_write = datetime.now() + self.aggregate_delay

        while self.is_running():
            if datetime.now() > next_write:
                if samples:
                    await self._db_writer(np.array(samples))
                samples.clear()
                next_write = datetime.now() + self.aggregate_delay

            samples.append(fake_sample())
            await asyncio.sleep(1)

    @staticmethod
    def _collate_queue(samples: np.ndarray) -> TestSample:
        return TestSample(
            float(samples[:, 0].mean()),
            float(samples[:, 1].mean()),
            samples[:, 2].max()
        )

    async def _db_writer(self, samples: np.ndarray) -> None:
        collated_sample = TestSensor._collate_queue(samples)

        async with aiosqlite.connect(DBNAME) as db:
            temp, ph, timestamp = collated_sample
            await db.execute(
                "INSERT INTO Logs (plantID, temperature, pH, CollectedTimestamp) VALUES (?, ?, ?, ?)",
                (self.plant_id, temp, ph, timestamp)
            )
            await db.commit()
