from dataclasses import dataclass
from io import BytesIO

import httpx
import pytest
from aiosqlite import Connection
from fastapi import status
from fastapi.testclient import TestClient
from PIL import Image

from api.plants import PlantSchema
from db import delete_image
from main import app
from tests import rms_img_diff
from tests.conftest import mangle_cookie


@dataclass
class NewPlant:
    name: str
    image_file: str | None


async def test_make_plant_no_auth(test_server: None):
    client = TestClient(app)

    response = client.get("/api/plants")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "plant",
    [
        NewPlant(name="Borys", image_file=None),
    ],
)
async def test_make_plant_no_image(
    plant: NewPlant, testdb: Connection, test_server: None
) -> None:
    client = TestClient(app)
    client.cookies.set("auth-token", mangle_cookie(1))

    assert plant.image_file is None

    response = client.post(
        "/api/plants",
        data={"name": plant.name},
    )

    response_plant = PlantSchema.model_validate(response.json())
    assert response_plant.name == plant.name

    cursor = await testdb.execute(
        "SELECT UserID, Name, ImageID FROM Plants WHERE ID = ?", (response_plant.id,)
    )
    row = await cursor.fetchone()
    assert row is not None
    assert row["UserID"] == 1
    assert row["Name"] == plant.name
    assert row["ImageID"] is None


@pytest.mark.parametrize(
    "plant",
    [
        NewPlant(name="Garus", image_file="test.png"),
    ],
)
async def test_make_plant_with_image(
    plant: NewPlant, testdb: Connection, test_server: None
) -> None:
    assert plant.image_file is not None
    client = TestClient(app)
    client.cookies.set("auth-token", mangle_cookie(1))
    response_plant = None
    try:
        with open(plant.image_file, "rb") as image:
            response = client.post(
                "/api/plants",
                data={"name": plant.name},
                files={"picture": (plant.image_file, image, "image/png")},
            )
        response_plant = PlantSchema.model_validate(response.json())
        assert response_plant.name == plant.name

        cursor = await testdb.execute(
            "SELECT UserID, Name, ImageID FROM Plants WHERE ID = ?",
            (response_plant.id,),
        )
        row = await cursor.fetchone()
        assert row is not None
        assert row["UserID"] == 1
        assert row["Name"] == plant.name
        assert (image_id := row["ImageID"]) is not None

        cursor = await testdb.execute(
            "SELECT URL FROM Images WHERE ID = ?", (image_id,)
        )
        row = await cursor.fetchone()
        assert row is not None
        assert (image_url := row["URL"]) is not None

        async with httpx.AsyncClient() as httpx_client:
            response = await httpx_client.get(image_url)
            uploaded_image = Image.open(BytesIO(response.content))
            stored_image = Image.open(plant.image_file)
            diff = rms_img_diff(uploaded_image, stored_image)
            assert diff < 10.0
    finally:
        if response_plant is not None:
            await delete_image(response_plant.id, testdb)
