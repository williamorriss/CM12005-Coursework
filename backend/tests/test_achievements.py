from fastapi.testclient import TestClient

from achievements import AchievementCode, AchievementEvent, AchievementSystem
from api.achievements import AchievementSchema
from main import app
from tests.conftest import mangle_cookie


def test_ping(test_server: None) -> None:
    achievements = AchievementSystem()
    client = TestClient(app)
    client.cookies.set("auth-token", mangle_cookie(1))

    with client.stream("GET", "/stream") as stream:
        achievements.send(1, AchievementEvent(code=AchievementCode.DEV))
        for line in stream.iter_lines():
            if line.startswith("data:"):
                event = AchievementSchema.model_validate_json(line[5:].strip())
                assert event.code == str(AchievementCode.DEV)
                stream.close()


def test_listener() -> None:
    achievements = AchievementSystem()
    q = achievements.create_listener(1)
    achievements.send(1, AchievementEvent(code=AchievementCode.DEV))
    event = q.get_nowait()
    assert event.code == AchievementCode.DEV
