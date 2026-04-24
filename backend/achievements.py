from asyncio import Queue
from uuid import uuid4, UUID
from db import get_db_contextmanager, get_plantcount_achievements, AchievementEvent

"""
TEST PLANT CODES:
P1 : 1 plant
P10 : 10 plants
"""

PLANT_COUNT_CODES = {"P1", "P10"}

class AchievementSystem:
    """
    A singleton class that manages achievements. 
    General Usage:
        1) An api client sends a GET request to api/achievements/stream
        2) A listener queue is created along with its UUID handle (to later refer to the connection) 
        3) In routes etc when the conditons for an achievement are met, the `send` method (preferably 
           as a background task) is used to push an AchievementEvent to all of the relevant listener queues
        4) This triggers a server side event in .../stream, sending an AchievementSchema to the client
        5) When the connection is closed, the UUID handle is used to remove the listener queue from the system
    """
    
    # used so __init__ is not called multiple times 
    _instance: "AchievementSystem | None" = None

    def __new__(cls) -> "AchievementSystem":
        # checks if already initialised, if so, skips __init__ (very important!!!!!!!!!)
        if cls._instance is None:
            cls._instance = (super().__new__(cls))

        assert cls._instance is not None
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "connections"):  # already initialised
            return
        self._connections: dict[int, list[UUID]] = {}
        self._listeners: dict[UUID, Queue[AchievementEvent]] = {}


    def create_listener(self, user_id: int) -> tuple[UUID, Queue[AchievementEvent]]:
        """
        Creates a listener queue and associated handle.
        Args:
            user_id: int - id of the client.

        Returns:
            tuple[UUID, Queue[AchievementEvent]] - handle and listener queue. 

        """

        queue: Queue[AchievementEvent] = Queue()
        uuid = uuid4()
        self._listeners[uuid] = queue
        self._connections.setdefault(user_id, []).append(uuid)

        return uuid, queue

    def remove_listener(self, user_id: int, queue_id: UUID) -> None:
        """
        Removes the listener queue with the given handle for a given user.

        Args:
            user_id: int - id of the client
            queue_id: UUID - handle of the listener queue
        """
        if user_id in self._connections:
            self._connections[user_id].remove(queue_id)
            del self._listeners[queue_id]

    async def send(self, user_id: int, event: AchievementEvent) -> None:
        """
        Sends an AchievementEvent to all listener queues associated with a user (all in the case of multiple connections per user)
        """
        
        for queue_id in self._connections.get(user_id, []):
            await self._listeners[queue_id].put(event)



async def plant_achievements(user_id: int) -> None:
    achievements = AchievementSystem()
    async with get_db_contextmanager() as db:
        for event in await get_plantcount_achievements(db, user_id):
            await achievements.send(user_id, event);

