from asyncio import Queue, QueueFull
from enum import Enum
from typing import NamedTuple

from aiosqlite import Connection

from db import get_db_contextmanager

"""
TEST PLANT CODES:
P1 : 1 plant
P10 : 10 plants
"""


class AchievementCode(str, Enum):
    P1 = "P1"
    P10 = "P10"


class AchievementEvent(NamedTuple):
    """
    Emitted achievement event.
    """

    code: AchievementCode


class AchievementSystem:
    """
    A singleton class that manages achievements.
    General Usage:
        1) An api client sends a GET request to api/achievements/stream
        2) A listener queue is created
        3) In routes etc when the conditons for an achievement are met, the `send` method (preferably
           as a background task) is used to push an AchievementEvent to all of the relevant listener queues
        4) This triggers a server side event in .../stream, sending an AchievementSchema to the client
        5) When the connection is closed, the UUID handle is used to remove the listener queue from the system
    """

    # used so __init__ is not called multiple times
    _instance: "AchievementSystem | None" = None
    _listeners: dict[int, list[Queue[AchievementEvent]]]

    def __new__(cls) -> "AchievementSystem":
        # checks if already initialised, if so, skips __init__ (very important!!!!!!!!!)
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        assert cls._instance is not None
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_listeners"):  # already initialised
            return
        self._listeners = {}

    def create_listener(self, user_id: int) -> Queue[AchievementEvent]:
        """
        Creates a listener queue and associated handle.
        Args:
            user_id: int - id of the client.

        Returns:
            Queue[AchievementEvent]] - listener queue.

        """

        queue: Queue[AchievementEvent] = Queue()
        self._listeners.setdefault(user_id, []).append(queue)

        return queue

    def remove_listener(self, user_id: int, queue: Queue[AchievementEvent]) -> None:
        """
        Removes the listener queue with the given handle for a given user.

        Args:
            user_id: int - id of the client
            queue_id: UUID - handle of the listener queue

        Raises exception if queue is not a listener for this user
        """
        if user_id not in self._listeners:
            raise Exception("This queue is not registered under this user (if at all)")

        self._listeners[user_id] = [
            q for q in self._listeners[user_id] if q is not queue
        ]

    def send(self, user_id: int, event: AchievementEvent) -> None:
        """
        Sends an AchievementEvent to all listener queues associated with a user
        (all in the case of multiple connections per user)
        """

        for queue in self._listeners.get(user_id, []):
            try:
                queue.put_nowait(event)
            except QueueFull:
                print("queue overflow")


async def plant_achievements(user_id: int) -> None:
    achievements = AchievementSystem()
    async with get_db_contextmanager() as db:
        for event in await _plantcount_achievements(db, user_id):
            achievements.send(user_id, event)


async def _plantcount_achievements(
    db: Connection, user_id: int
) -> list[AchievementEvent]:
    events: list[AchievementEvent] = []
    async with db.execute(
        "SELECT COUNT(*) as No FROM Plants WHERE UserID = ?", (user_id,)
    ) as cursor:
        row = await cursor.fetchone()
        assert row is not None
        no_plants = row["No"]

    rows = await db.execute_fetchall(
        """
        SELECT a.Code as Code FROM Awards a
        INNER JOIN Achievements ac ON a.ID = ac.AwardID
        WHERE ac.UserID = ?""",
        (user_id,),
    )

    assert rows is not None
    codes = {row["Code"] for row in rows}

    if "P1" not in codes and no_plants > 0:
        await db.execute_insert(
            """
            INSERT INTO Achievements (AwardID, UserID)
            SELECT ID, ? FROM Awards WHERE Code = ?
        """,
            (user_id, "P1"),
        )
        events.append(AchievementEvent(code=AchievementCode.P1))

    if "P10" not in codes and no_plants >= 10:
        events.append(AchievementEvent(code=AchievementCode.P10))

    await db.commit()
    return events
