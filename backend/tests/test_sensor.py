from contextlib import AbstractAsyncContextManager
from typing import Callable

import httpx
from aiosqlite import Connection
from fastapi.testclient import TestClient

from api.sensors import owns_sensor
from main import app
from sensor import SensorSystem
from tests.conftest import mangle_cookie


async def test_owns_sensor(testdb: Connection) -> None:
    client = TestClient(app)
    await testdb.execute("INSERT INTO Users (ID, Username) VALUES (1, 'OBrian')")
    await testdb.execute(
        "INSERT INTO Sensors (ID, UserID, Name) VALUES (1, 1, 'Efiegel')"
    )
    await testdb.commit()
    client.cookies.set("auth-token", mangle_cookie(1))

    assert await owns_sensor(1, 1, testdb)


async def test_sensor_system(
    testdb: Connection,
    testdb_manager: Callable[[], AbstractAsyncContextManager[Connection, None]],
) -> None:
    await testdb.execute("INSERT INTO Users (ID, Username) VALUES (1, 'Xa')")
    await testdb.execute(
        "INSERT INTO Plants (ID, UserID, Name) VALUES (1, 1, 'Daemon')"
    )
    await testdb.execute(
        "INSERT INTO Sensors (ID, UserID, PlantID, Name) VALUES (1, 1, 1, 'Ometius')"
    )
    await testdb.commit()
    sensors = SensorSystem(get_db=testdb_manager, delay=0.5)

    queue = sensors.attach_sensor(1)
    await sensors.activate_sensor(1)
    first_entry = await queue.get()
    _ = await queue.get()
    sensors.deactivate_sensor(1)

    cursor = await testdb.execute(
        "SELECT PlantID, SensorID, Temperature, PH FROM Logs ORDER BY CollectedTimestamp ASC"
    )
    row = await cursor.fetchone()
    assert row is not None
    assert row["PlantID"] == 1
    assert row["SensorID"] == 1

    assert first_entry.temperature == row["Temperature"]

    assert first_entry.ph == row["PH"]


async def test_sensor_ping(
    testdb: Connection,
    test_server: None,
    testdb_manager: Callable[[], AbstractAsyncContextManager[Connection, None]],
):
    await testdb.execute("INSERT INTO Users (ID, Username) VALUES (1, 'Gabriel')")
    await testdb.execute(
        "INSERT INTO Plants (ID, UserID, Name) VALUES (1, 1, 'Quaxly')"
    )
    await testdb.execute(
        "INSERT INTO Sensors (ID, UserID, PlantID, Name) VALUES (1, 1, 1, 'Kleinsfold')"
    )
    await testdb.commit()

    sensors = SensorSystem(get_db=testdb_manager, delay=0.5)
    q = sensors.attach_sensor(1)

    # httpx async client more powerful (allows server async processes)
    # apparently not powerful enough for streaming...
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
        cookies={"auth-token": mangle_cookie(1)},
    ) as client:
        start_response = await client.post("/api/sensors/1/session")
        assert start_response.is_success

        sample = await q.get()
        _ = await q.get()

        delete_response = await client.delete("/api/sensors/1/session")
        assert delete_response.is_success

    assert sample is not None
    cursor = await testdb.execute(
        "SELECT PlantID, SensorID, Temperature, PH FROM Logs ORDER BY CollectedTimestamp ASC"
    )
    row = await cursor.fetchone()
    assert row is not None
    assert row["PlantID"] == 1
    assert row["SensorID"] == 1
    assert sample.temperature == row["Temperature"]
    assert sample.ph == row["PH"]


async def test_double_ping(
    testdb: Connection,
    test_server: None,
    testdb_manager: Callable[[], AbstractAsyncContextManager[Connection, None]],
) -> None:
    await testdb.execute("INSERT INTO Users (ID, Username) VALUES (1, 'Gooble')")
    await testdb.execute("INSERT INTO Plants (ID, UserID, Name) VALUES (1, 1, 'Yam')")
    await testdb.execute(
        "INSERT INTO Sensors (ID, UserID, PlantID, Name) VALUES (1, 1, 1, 'Kop')"
    )
    await testdb.commit()

    client = TestClient(app)
    client.cookies.set("auth-token", mangle_cookie(1))

    r1 = client.post("api/sensors/1/session")
    assert r1.is_success

    r2 = client.post("api/sensors/1/session")
    assert r2.is_error

    r1 = client.delete("api/sensors/1/session")
    assert r1.is_success

    r2 = client.delete("api/sensors/1/session")
    assert r2.is_error
