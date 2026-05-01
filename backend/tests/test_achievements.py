from contextlib import AbstractAsyncContextManager
from typing import Callable

from aiosqlite import Connection
from fastapi.testclient import TestClient

from achievements import AchievementCode, AchievementEvent, AchievementSystem
from main import app
from tests.conftest import mangle_cookie


async def test_first_plant_achievement(
    testdb: Connection,
    test_server: None,
    testdb_manager: Callable[[], AbstractAsyncContextManager[Connection, None]],
) -> None:
    achievements = AchievementSystem(get_db=testdb_manager)
    # would be better to do directly with streaming but awaiting the queue in subscribe
    # brings fastapi to its knees. Should be fine as the actual streaming part is
    # reliable (when consumer seperate from producer -_-)

    await testdb.execute("INSERT INTO Users (ID, Username) VALUES (1, 'Eve')")
    await testdb.commit()

    q = achievements.create_listener(1)
    client = TestClient(app)
    client.cookies.set("auth-token", mangle_cookie(1))

    response = client.post(
        "/api/plants",
        data={"name": "Adam"},
    )
    assert response.is_success

    event = await q.get()
    assert event.code == AchievementCode.P1


def test_listener() -> None:
    achievements = AchievementSystem()
    q = achievements.create_listener(1)
    achievements.send(1, AchievementEvent(code=AchievementCode.DEV))
    event = q.get_nowait()
    assert event.code == AchievementCode.DEV
