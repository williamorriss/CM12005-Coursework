from typing import AsyncGenerator
from aiosqlite import connect, Connection, Row
from fastapi.requests import Request


DBNAME = "test.db"

async def get_db(_r: Request) -> AsyncGenerator[Connection, None]:
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