import io
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx
from aiosqlite import Connection
from fastapi import UploadFile, status
from fastapi.testclient import TestClient

from config import AppConfig
from db import make_static_url
from main import app
from tests.conftest import mangle_cookie


@dataclass
class NewPlant:
    name: str
    image_file: str | None


async def test_delete_plant_no_auth(test_server: None):
    client = TestClient(app)

    response = client.delete("/api/plants/1")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def get_page_url(image_url: str) -> str:
    # actual CDN page /= page url (page url takes time to update after removal)
    path_id = urlparse(image_url).path.split("/")[1]
    return f"https://ibb.co/{path_id}"


async def test_delete_plant_no_own(testdb: Connection, test_server: None):
    client = TestClient(app)

    await testdb.execute_insert(
        "INSERT INTO Plants (ID, UserID, Name) VALUES (?, ?, 'Jabba')", (1, 2)
    )
    await testdb.commit()

    client.cookies.set("auth-token", mangle_cookie(1))
    response = client.delete("/api/plants/1")

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_plant_with_image(
    testdb: Connection, test_server: None, get_config: AppConfig
):
    # unrelated plant owned by same user
    await testdb.execute_insert(
        "INSERT INTO Plants (ID, UserID, Name) VALUES (2, 1, 'Abigail')", ()
    )

    with open("test.png", "rb") as image:
        url, delete_url = await make_static_url(
            get_config.imgbb_key,
            UploadFile(filename="test.png", file=io.BytesIO(image.read())),
        )

    try:
        image_row = await testdb.execute_insert(
            "INSERT INTO Images (URL, DeleteURL) Values (?, ?)", (url, delete_url)
        )
        assert image_row is not None
        img_id = image_row[0]
        name = "Charles Cabbage"

        plant_row = await testdb.execute_insert(
            "INSERT INTO Plants (ID, UserID, Name, ImageID) VALUES (1, 1, ?, ?)",
            (name, img_id),
        )
        assert plant_row is not None
        plant_id = plant_row[0]
        await testdb.commit()

        client = TestClient(app)
        client.cookies.set("auth-token", mangle_cookie(1))

        response = client.delete("/api/plants/1")
        assert response.is_success

        check_plant = await testdb.execute(
            "SELECT EXISTS (SELECT 1 FROM Plants WHERE ID = ?)", (plant_id,)
        )
        cursor = await check_plant.fetchone()
        assert cursor is not None and not cursor[0]

        check_image = await testdb.execute(
            "SELECT EXISTS (SELECT 1 FROM Images WHERE ID = ?)", (img_id,)
        )
        cursor = await check_image.fetchone()
        assert cursor is not None and not cursor[0]

        async with httpx.AsyncClient() as httpx_client:
            img_bb_response = await httpx_client.get(get_page_url(url))
            assert img_bb_response.is_error
    finally:
        async with httpx.AsyncClient() as httpx_client:
            img_bb_response = await httpx_client.get(delete_url)


async def test_get_plant_without_image(testdb: Connection, test_server: None):
    # unrelated plant owned by same user
    await testdb.execute_insert(
        "INSERT INTO Plants (ID, UserID, Name) VALUES (2, 1, 'Garmunch')"
    )

    await testdb.execute_insert(
        "INSERT INTO Plants (ID, UserID, Name) VALUES (1, 1, 'Fargo')", ()
    )
    await testdb.commit()

    client = TestClient(app)
    client.cookies.set("auth-token", mangle_cookie(1))

    response = client.delete("/api/plants/1")
    assert response.is_success

    check_plant = await testdb.execute(
        "SELECT EXISTS (SELECT 1 FROM Plants WHERE ID = 1)", ()
    )
    cursor = await check_plant.fetchone()
    assert cursor is not None and not cursor[0]
