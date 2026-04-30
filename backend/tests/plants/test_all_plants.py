from dataclasses import dataclass

import pytest
from aiosqlite import Connection
from fastapi import status
from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from api.plants import PlantSchema
from main import app
from tests.conftest import mangle_cookie

PlantList = TypeAdapter(list[PlantSchema])


@dataclass
class FakePlant:
    user_id: int
    plant_id: int
    image_url: str | None
    name: str


TESTPLANTS: list[FakePlant] = [
    FakePlant(user_id=1, plant_id=1, image_url="http://plant1url", name="Gilbert"),
    FakePlant(user_id=1, plant_id=2, image_url=None, name="Gamalon"),
    FakePlant(user_id=2, plant_id=3, image_url=None, name="Hilbert"),
]


# api/plants
async def insert_fake_image(db: Connection, url: str | None) -> int | None:
    if url is None:
        return None

    row = await db.execute_insert(
        "INSERT INTO Images (URL, DeleteURL) VALUES (?, ?)", (url, "<delete_url>")
    )
    assert row is not None
    return row[0]


async def insert_plants(db: Connection) -> None:
    for plant in TESTPLANTS:
        image_id = await insert_fake_image(db, plant.image_url)
        row = await db.execute_insert(
            "INSERT INTO Plants (ID, UserID, Name, ImageID) VALUES (?, ?, ?, ?)",
            (plant.plant_id, plant.user_id, plant.name, image_id),
        )
        assert row is not None
    await db.commit()


async def test_get_all_plants_no_auth(test_server: None):
    client = TestClient(app)

    response = client.get("/api/plants")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("user_id", [1, 2, 3])
async def test_get_all_plants(
    user_id: int, testdb: Connection, test_server: None
) -> None:
    plant_lookup = {plant.plant_id: plant for plant in TESTPLANTS}
    await insert_plants(testdb)
    client = TestClient(app)
    client.cookies.set("auth-token", mangle_cookie(1))
    for response_plant in PlantList.validate_python(client.get("api/plants").json()):
        true_plant = plant_lookup[response_plant.id]
        assert response_plant.image_url == true_plant.image_url
        assert response_plant.name == true_plant.name
