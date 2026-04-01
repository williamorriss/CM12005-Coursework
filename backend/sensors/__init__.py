from abc import ABC, abstractmethod

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

# reexports
from .sensor import router