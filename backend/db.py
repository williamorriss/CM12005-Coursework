import csv
from typing import AsyncGenerator, cast
from aiosqlite import connect, Connection, Row
from contextlib import asynccontextmanager

DBNAME = "test.db"


@asynccontextmanager # Add this decorator
async def get_db_contextmanager() -> AsyncGenerator[Connection, None]:
    async with connect(DBNAME) as db:
        db.row_factory = Row
        yield db

async def get_db() -> AsyncGenerator[Connection, None]:
    async with connect(DBNAME) as db:
        db.row_factory = Row
        yield db

async def init_db() -> None:
    async with connect(DBNAME) as db:
        await db.execute("PRAGMA journal_mode=WAL") # Write Ahead Log for concurrent read/ writes
        await db.execute("PRAGMA busy_timeout=1000")
        await db.execute("PRAGMA synchronous=NORMAL")
        with open("sql/schema.sql", 'r') as schema_file:
            schema_sql = schema_file.read()
            await db.executescript(schema_sql)

        await load_awards(db)
        await db.commit()
        print(f"Schema applied")

async def load_awards(db: Connection) -> None:
    with open("sql/awards.csv") as awards_file:
        awards_reader = csv.reader(awards_file)
        await db.execute("DELETE FROM Awards WHERE true")
        next(awards_reader) # skip columns
        await db.executemany("INSERT INTO Awards (Code, Description) VALUES(?, ?)", awards_reader)


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