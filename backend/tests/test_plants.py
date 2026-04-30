from dataclasses import dataclass

from aiosqlite import Connection
from conftest import mangle_cookie
from fastapi import status
from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from api.plants import PlantSchema
from main import app

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


async def test_all_plant_no_auth(test_server: None) -> None:
    client = TestClient(app)
    client.cookies.set("auth-token", mangle_cookie(1))


async def test_get_all_plants_no_auth(test_server: None):
    client = TestClient(app)

    response = client.get("/api/plants")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_all_plants(testdb: Connection, test_server: None) -> None:
    plant_lookup = {plant.plant_id: plant for plant in TESTPLANTS}
    await insert_plants(testdb)
    client = TestClient(app)
    client.cookies.set("auth-token", mangle_cookie(1))
    for response_plant in PlantList.validate_python(client.get("api/plants").json()):
        true_plant = plant_lookup[response_plant.id]
        assert response_plant.image_url == true_plant.image_url
        assert response_plant.name == true_plant.name


async def test_get_all_plants_single(testdb: Connection, test_server: None) -> None:
    plant_lookup = {plant.plant_id: plant for plant in TESTPLANTS}
    await insert_plants(testdb)
    client = TestClient(app)
    client.cookies.set("auth-token", mangle_cookie(2))
    response_plants = PlantList.validate_python(client.get("api/plants").json())
    assert len(response_plants) == 1
    response_plant = response_plants[0]
    true_plant = plant_lookup[response_plant.id]
    assert response_plant.image_url == true_plant.image_url
    assert response_plant.name == true_plant.name


async def test_get_all_plants_none(testdb: Connection, test_server: None) -> None:
    await insert_plants(testdb)
    client = TestClient(app)
    client.cookies.set("auth-token", mangle_cookie(3))
    response_plants = PlantList.validate_python(client.get("api/plants").json())
    assert len(response_plants) == 0


# api/plant/{plant_id}
async def test_get_plant_with_image(testdb: Connection, test_server: None):
    # unrelated plant owned by same user
    await testdb.execute_insert(
        "INSERT INTO Plants (ID, UserID, Name) VALUES (2, 1, 'Alfredo')", ()
    )
    img_url = "hahahahahahahahahahha"
    name = "Alamanzo"
    await testdb.execute_insert(
        "INSERT INTO Images (ID, URL, DeleteURL) VALUES (1, ?, '<deleteurl>')",
        (img_url,),
    )

    await testdb.execute_insert(
        "INSERT INTO Plants (ID, UserID, Name, ImageID) VALUES (1, 1, ?, 1)", (name,)
    )
    await testdb.commit()

    client = TestClient(app)
    client.cookies.set("auth-token", mangle_cookie(1))

    plant = PlantSchema.model_validate(client.get("/api/plants/1").json())
    assert plant.id == 1
    assert plant.image_url == img_url
    assert plant.name == name


async def test_get_plant_without_image(testdb: Connection, test_server: None):
    # unrelated plant owned by same user
    await testdb.execute_insert(
        "INSERT INTO Plants (ID, UserID, Name) VALUES (2, 1, 'Garmunch')"
    )

    name = "Ratatatata"
    await testdb.execute_insert(
        "INSERT INTO Plants (ID, UserID, Name) VALUES (1, 1, ?)", (name,)
    )
    await testdb.commit()

    client = TestClient(app)
    client.cookies.set("auth-token", mangle_cookie(1))

    plant = PlantSchema.model_validate(client.get("/api/plants/1").json())
    assert plant.id == 1
    assert plant.name == name
    assert plant.image_url is None


async def test_get_plant_not_owned(testdb: Connection, test_server: None):
    await testdb.execute_insert(
        "INSERT INTO Plants (UserID, Name) VALUES (1, 'JaMarcus')"
    )

    client = TestClient(app)
    client.cookies.set("auth-token", mangle_cookie(1))

    response = client.get("/api/plants/999")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_plant_no_auth(test_server: None):
    client = TestClient(app)

    response = client.get("/api/plants/1")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_plant_unauthorized(testdb: Connection, test_server: None):
    await testdb.execute_insert(
        "INSERT INTO Plants (ID, UserID, Name) VALUES (1, 1, 'Ragadable')"
    )

    client = TestClient(app)

    response = client.get("/api/plants/1")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
