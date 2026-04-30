import csv
from contextlib import asynccontextmanager
from typing import AsyncGenerator, cast

import httpx
from aiosqlite import Connection, Row, connect
from fastapi import HTTPException, UploadFile

DBNAME = "test.db"


@asynccontextmanager
async def get_db_contextmanager() -> AsyncGenerator[Connection, None]:
    """
    Gets db connection. Use `get_db` with Depends for routes etc where
    `Depends` can be used

    Note:
        This is an async context manager so use
        ```python
            async with get_db_contextmanager() as db:
             ...
        ```
        to use the connection
    """
    async with connect(DBNAME) as db:
        db.row_factory = Row
        yield db


async def get_db() -> AsyncGenerator[Connection, None]:
    """
    Gets db connection via dependency injection

    Note:
        Use this with db: ... = Depends(get_db)
        Otherwise `get_db_contextmanager`
    """
    async with connect(DBNAME) as db:
        db.row_factory = Row
        yield db


async def init_db() -> None:
    """
    Method to initialise database (local .db file)
    """
    async with connect(DBNAME) as db:
        await init_connection(db)


async def init_connection(db: Connection) -> None:
    await db.execute(
        "PRAGMA journal_mode=WAL"
    )  # Write Ahead Log for concurrent read/ writes
    await db.execute("PRAGMA busy_timeout=1000")
    await db.execute("PRAGMA synchronous=NORMAL")
    with open("sql/schema.sql", "r") as schema_file:
        schema_sql = schema_file.read()
        await db.executescript(schema_sql)

    await _load_awards(db)
    await db.commit()
    print("Schema applied")


async def _load_awards(db: Connection) -> None:
    with open("sql/awards.csv") as awards_file:
        awards_reader = csv.reader(awards_file)
        await db.execute("DELETE FROM Awards WHERE true")
        next(awards_reader)  # skip columns
        await db.executemany(
            "INSERT INTO Awards (Code, Description) VALUES(?, ?)", awards_reader
        )


async def owns_plant(user_id: int, plant_id: int, db: Connection) -> bool:
    async with db.execute(
        "SELECT EXISTS(SELECT 1 FROM Plants WHERE UserID = ? AND ID = ?)",
        (user_id, plant_id),
    ) as cursor:
        row = await cursor.fetchone()
        assert row is not None
        return bool(cast(int, row[0]))


async def delete_image(plant_id: int, db: Connection) -> None:
    async with db.execute(
        "SELECT ImageID FROM Plants WHERE ID = ?", (plant_id,)
    ) as cursor:
        row = await cursor.fetchone()
    if row is None or (image_id := row[0]) is None:
        return

    async with db.execute(
        "SELECT DeleteUrl FROM Images WHERE ID = ?", (image_id,)
    ) as cursor:
        row = await cursor.fetchone()
    if row is None or (delete_url := row[0]) is None:
        raise HTTPException(status_code=500, detail="Image resource has no delete URL")

    async with httpx.AsyncClient() as client:
        response = await client.delete(delete_url)
        if response.is_error:
            raise HTTPException(status_code=500, detail="Could not delete image")

    await db.execute("DELETE FROM Images WHERE ID = ?", (image_id,))
    await db.commit()


async def make_static_url(api_key: str, file: UploadFile) -> tuple[str, str]:
    files = {"image": await file.read()}  # per api spec it MUST be "image"
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.imgbb.com/1/upload?key={api_key}",
            files=files,
            data={"name": file.filename},
        )

    if response.is_error:
        raise HTTPException(status_code=500, detail="Could not make static url")

    json_response = response.json()
    if not json_response["success"]:
        raise HTTPException(
            status_code=500, detail="Provider failed to make static url"
        )

    print(json_response)
    data = json_response["data"]
    delete_url = data["delete_url"]
    url = data["url"]
    return url, delete_url
