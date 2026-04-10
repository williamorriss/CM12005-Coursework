from abc import abstractmethod, ABC
from asyncio import Queue
from collections import namedtuple


Sample = namedtuple("Sample", ["temperature", "ph", "timestamp"])

class Sensor(ABC):

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def is_running(self) -> bool:
        pass

    @abstractmethod
    def set_target(self, plant_id: int) -> None:
        pass

    @abstractmethod
    def add_watcher(self, queue: Queue[Sample]) -> None:
        pass

    @abstractmethod
    def remove_watcher(self, queue: Queue[Sample]) -> None:
        pass