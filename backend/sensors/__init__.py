from abc import ABC, abstractmethod

from collections import namedtuple
from asyncio import Queue

Sample = namedtuple("Sample", ["temperature", "ph", "timestamp"])

class Sensor(ABC):

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def is_running(self) -> bool:
        pass

    @abstractmethod
    def set_target(self, plant_id: int):
        pass

    @abstractmethod
    def add_watcher(self, queue: Queue[Sample]):
        pass

    @abstractmethod
    def remove_watcher(self, queue: Queue[Sample]):
        pass

# reexports
from .routes import router