from typing import AsyncGenerator, cast
from aiosqlite import connect, Connection, Row
from fastapi.requests import Request

DBNAME = "test.db"

async def get_db() -> AsyncGenerator[Connection, None]:
    async with connect("test.db") as db:
        db.row_factory = Row
        yield db

async def init_db() -> None:
    with open("sql/schema.sql", 'r') as schema_file:
        schema_sql = schema_file.read()
        async with connect(DBNAME) as db:
            await db.execute("PRAGMA journal_mode=WAL") # Write Ahead Log for concurrent read/ writes
            await db.execute("PRAGMA busy_timeout=1000")
            await db.execute("PRAGMA synchronous=NORMAL")
            await db.executescript(schema_sql)
            await db.commit()
            print(f"Schema applied")

async def owns_plant(user_id: int, plant_id: int, db: Connection) -> bool:
    async with db.execute(
            "SELECT EXISTS(SELECT 1 FROM Plants WHERE UserID = ? AND ID = ?)",
            (user_id, plant_id)
    ) as cursor:
        row = await cursor.fetchone()
        assert row is not None
        return bool(cast(int, row[0]))

async def owns_sensor(user_id: int, sensor_id: int, db: Connection) -> bool:
    async with db.execute(
            "SELECT EXISTS(SELECT 1 FROM Sensors WHERE UserID = ? AND ID = ?)",
            (user_id, sensor_id)
    ) as cursor:
        row = await cursor.fetchone()
    assert row is not None
    return bool(cast(int, row[0]))