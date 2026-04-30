from aiosqlite import Connection
from fastapi import status
from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from api.plants import PlantSchema
from main import app
from tests.conftest import mangle_cookie

PlantList = TypeAdapter(list[PlantSchema])


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
