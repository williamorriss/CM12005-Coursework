from pydantic import BaseModel

class LogData(BaseModel):
    id: int
    temperature: float
    ph: float
    collected_timestamp: int
    insert_timestamp: int

class SensorData(BaseModel):
    id: int
    name: str

class NoteData(BaseModel):
    id: int
    content: str
    rating: int
    timestamp: int

class PlantData(BaseModel):
    id: int
    name: str
    image_url: str
    Sensors: list[int]
    Notes: list[int]
    Logs: list[int]