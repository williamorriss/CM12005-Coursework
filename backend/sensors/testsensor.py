from datetime import datetime, timedelta
import numpy as np
import asyncio
import aiosqlite
from . import Sensor, Sample
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
        self._task: asyncio.Task | None = None
        self._watchers: list[asyncio.Queue[Sample]] = []

    def start(self):
        print(f"{self._name} {self._sensor_id} RUNNING")
        self._task = asyncio.create_task(self._process())

    def stop(self):
        if self._task:
            self._task.cancel()
            self._task = None

    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()

    def set_target(self, plant_id: int):
        self._plant_id = plant_id

    def add_watcher(self, queue: asyncio.Queue[Sample]):
        self._watchers.append(queue)

    def remove_watcher(self, queue: asyncio.Queue[Sample]):
        self._watchers.remove(queue)

    async def _process(self):
        samples = []
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
        self.plant_id = plant_id
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


    async def _db_writer(self, collated: Sample) -> None:
        print(f"WRITING {collated}")

        async with aiosqlite.connect(DBNAME) as db:
            temp, ph, timestamp = collated
            await db.execute(
                "INSERT INTO Logs (SensorID, PlantID, temperature, pH, CollectedTimestamp) VALUES (?, ?, ?, ?, ?)",
                (self._sensor_id, self._plant_id, temp, ph, timestamp)

    async def _db_writer(self, samples: np.ndarray) -> None:
        collated_sample = TestSensor._collate_queue(samples)

        async with aiosqlite.connect(DBNAME) as db:
            temp, ph, timestamp = collated_sample
            await db.execute(
                "INSERT INTO Logs (plantID, temperature, pH, CollectedTimestamp) VALUES (?, ?, ?, ?)",
                (self.plant_id, temp, ph, timestamp)
            )
            await db.commit()