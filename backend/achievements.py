from asyncio import Queue
from uuid import uuid4, UUID

from aiosqlite import Connection

"""
TEST PLANT CODES:
P1 : 1 plant
P10 : 10 plants
"""

PLANT_COUNT_CODES = {"P1", "P10"}

class AchievementEvent:
    def __init__(self, code: str) -> None:
        self.code = code

class AchievementSystem:
    _instance: "AchievementSystem | None" = None

    def __new__(cls) -> "AchievementSystem":
        if cls._instance is None:
            cls._instance = (super().__new__(cls))

        assert cls._instance is not None
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "connections"):  # already initialised
            return
        self.connections: dict[int, list[UUID]] = {}
        self.queues: dict[UUID, Queue[AchievementEvent]] = {}


    def subscribe(self, user_id: int) -> tuple[UUID, Queue[AchievementEvent]]:
        queue: Queue[AchievementEvent] = Queue()
        uuid = uuid4()
        self.queues[uuid] = queue
        self.connections.setdefault(user_id, []).append(uuid)

        return uuid, queue

    def unsubscribe(self, user_id: int, queue_id: UUID) -> None:
        if user_id in self.connections:
            self.connections[user_id].remove(queue_id)
            del self.queues[queue_id]

    async def send(self, user_id: int, event: AchievementEvent) -> None:
        for queue_id in self.connections.get(user_id, []):
            await self.queues[queue_id].put(event)

    async def plant_achievements(self, db: Connection, user_id: int) -> None:
        async with db.execute("SELECT COUNT(*) as No FROM Plants WHERE UserID = ?", (user_id, )) as cursor:
            row = await cursor.fetchone()
            assert row is not None
            no_plants = row["No"]

        rows = await db.execute_fetchall("""
            SELECT a.Code as Code FROM Awards a
            INNER JOIN Achievements ac ON a.ID = ac.AwardID
            WHERE ac.UserID = ?""",
            (user_id, )
        )

        assert rows is not None
        codes = {row["Code"] for row in rows}

        if "P1" not in codes and no_plants > 0:
            res = await db.execute_insert("""
                INSERT INTO Achievements (AwardID, UserID)
                SELECT ID, ? FROM Awards WHERE Code = ?
            """, (user_id, 'P1'))
            print(res)
            await self.send(user_id, AchievementEvent(code="P1"))

        if "P10" not in codes and no_plants >= 10:
            await self.send(user_id, AchievementEvent(code="P10"))

        await db.commit()