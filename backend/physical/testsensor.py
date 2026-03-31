from random import randrange
from datetime import datetime, timedelta
import numpy as np
from collections import namedtuple
import multiprocessing
import asyncio
import aiosqlite

from extract import DBNAME

TestSample = namedtuple("TestSample", ["temperature", "pH", "timestamp"])

def fake_sample() -> TestSample:
    temperature = randrange(-10, 40)
    ph = randrange(0, 14)
    return TestSample(temperature, ph, datetime.now())

class TestSensor:
    def __init__(self, plant_id: int):
        self.aggregate_delay = timedelta(minutes=1)
        self.plant_id = plant_id
        self._stop_event = multiprocessing.Event()

    def start(self):
        self._stop_event.clear()
        multiprocessing.Process(target=self._run, daemon=True).start()

    def stop(self):
        self._stop_event.set()

    def _run(self):
        asyncio.run(self._process())

    async def _process(self):
        samples = []
        next_write = datetime.now() + self.aggregate_delay

        while not self._stop_event.is_set():
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