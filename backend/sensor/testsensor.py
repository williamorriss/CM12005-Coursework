from asyncio.queues import Queue
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import numpy as np
import asyncio
import aiosqlite
from sensor.sensor import Sample
from db import DBNAME
from random import randrange

type SensorHandle = UUID
type ConnectionHandle = UUID

def fake_sample() -> Sample:
    temperature = randrange(-10, 40)
    ph = randrange(0, 14)
    return Sample(temperature, ph, datetime.now())


def collate(samples: np.ndarray) -> Sample:
    return Sample(
        float(samples[:, 0].mean()),
        float(samples[:, 1].mean()),
        samples[:, 2].max()
    )
  
class SensorSystem:
    _instance: "SensorSystem | None" = None

    def __new__(cls) -> "SensorSystem":
        if cls._instance is None:
            cls._instance = (super().__new__(cls))

        assert cls._instance is not None
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "connections"):  # already initialised
            return
        self._connections: dict[int, list[UUID]] = {}
        self._listeners: dict[UUID, Queue[Sample]] = {}

    
    async def _process(self):
        while True:
            collated = [
                (x[0], collate(np.array(x[1])))
                 for x in (await asyncio.gather(*[SensorSystem.collect_n(sensor_id) for sensor_id in self._connections.keys()])) 
                 if x is not None
            ]
            asyncio.create_task(self._db_writer(collated))
            for sensor_id, sample in collated:
                for uuid in self._connections[sensor_id]:
                    self._listeners[uuid].put_nowait(sample)

    async def _db_writer(self, collated: list[tuple[int,Sample]]) -> None:
        async with aiosqlite.connect(DBNAME) as db:
            await db.executemany(
                "INSERT INTO Logs (SensorID, temperature, pH, CollectedTimestamp) VALUES (?, ?, ?, ?, ?)",
                [(sensor_id, sample.temperature, sample.ph, sample.timestamp) for sensor_id, sample in collated]
            )

            await db.commit()

            
    @staticmethod
    async def collect_n(sensor_id: int, n: int = 6, delay_seconds: float = 10) -> tuple[int,list[Sample]] | None:
        samples = []
        try:
            for _ in range(n):
                sample = fake_sample()
                samples.append(sample) 
                await asyncio.sleep(delay_seconds) 
            return sensor_id,samples
        except asyncio.CancelledError:
            return None 



    def create_listener(self, sensor_id: int, plant_id: int) -> tuple[UUID, Queue[Sample]]:
        queue: Queue[Sample] = Queue()
        uuid = uuid4()
        self._listeners[uuid] = queue
        self._connections.setdefault(sensor_id, []).append(uuid)
        return uuid, queue

    def remove_listener(self, sensor_id: int, queue_id: UUID) -> None:
        if sensor_id in self._connections:
            self._connections[user_id].remove(queue_id)
            del self._listeners[queue_id]




