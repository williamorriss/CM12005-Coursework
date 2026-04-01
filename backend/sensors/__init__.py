from abc import ABC, abstractmethod

<<<<<<< HEAD
from collections import namedtuple
from asyncio import Queue

Sample = namedtuple("Sample", ["temperature", "ph", "timestamp"])

=======
>>>>>>> 13e1dc504d87b0fa4288ec041312f01c468236f7
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

<<<<<<< HEAD
    @abstractmethod
    def add_watcher(self, queue: Queue[Sample]):
        pass

    @abstractmethod
    def remove_watcher(self, queue: Queue[Sample]):
        pass

# reexports
from .routes import router
=======
# reexports
from .sensor import router
>>>>>>> 13e1dc504d87b0fa4288ec041312f01c468236f7
