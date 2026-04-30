from asyncio import Queue, QueueFull
from enum import Enum
from typing import NamedTuple

from aiosqlite import Connection

from db import get_db_contextmanager


class AchievementCode(str, Enum):
    """
    Enum of all recognised achievements

    Note:
        Should be fine to define here (for now) but can
        be relocated/ extracted from db if this becomes too unwieldly
    """

    P1 = "P1"  # 1 Plant
    P10 = "P10"  # 10 Plants
    DEV = "<dev>"


class AchievementEvent(NamedTuple):
    """
    Emitted achievement event.
    """

    code: AchievementCode


class AchievementSystem:
    """
    A singleton class to manage achievements.
    """

    _instance: "AchievementSystem | None" = None

    # maps user_id -> list of queues listening for that user's achievements
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
        Creates a async `AchievementEvent` queue to which achievements for this user
        will be pushed to.
        """

        queue: Queue[AchievementEvent] = Queue()
        self._listeners.setdefault(user_id, []).append(queue)

        return queue

    def remove_listener(self, user_id: int, queue: Queue[AchievementEvent]) -> None:
        """
        Removes this queue (by reference) from the list of this user's listeners

        Note:
            Raises exception if queue is not a listener for this user
        """
        if user_id not in self._listeners:
            raise Exception("This queue is not registered under this user (if at all)")

        self._listeners[user_id] = [
            q for q in self._listeners[user_id] if q is not queue
        ]

    def send(self, user_id: int, event: AchievementEvent) -> None:
        """
        Sends an AchievementEvent to all listener queues associated with this user

        Note:
            use this to broadcast when an achievement is acomplished in routes etc....
        """

        for queue in self._listeners.get(user_id, []):
            try:
                queue.put_nowait(event)
            except QueueFull:
                print("queue overflow")


async def plant_achievements(user_id: int) -> None:
    """
    Convenience method to calculate whether this user has achieved any new
    plant achievements

    Note:
        Currently only checks plant count (e.g 1 plant etc) but can be expanded
    """
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
