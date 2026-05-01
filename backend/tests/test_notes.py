from dataclasses import dataclass

import pytest
from aiosqlite import Connection
from fastapi import status
from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from api.notes import NoteSchema
from main import app
from tests.conftest import mangle_cookie

Notes = TypeAdapter(list[NoteSchema])


@dataclass
class FakeNote:
    note_id: int
    note: str
    rating: int
    plant_id: int


async def test_get_all_plants_no_auth(test_server: None):
    client = TestClient(app)

    response = client.get("/api/plants/1/notes")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def get_not_own_note(testdb: Connection, test_server: None) -> None:
    await testdb.execute("INSERT INTO Users VALUES (ID, Username) VALUES (1, 'Gödel')")
    await testdb.execute("INSERT INTO Users VALUES (ID, Username) VALUES (2, 'Russel')")
    await testdb.execute(
        "INSERT INTO PNlants VALUES (ID, UserID, Name) VALUES (2, 1, 'G')"
    )

    await testdb.execute(
        "INSERT INTO Notes VALUES (ID, PlantID, Note, Rating) VALUES (1,2,'Russel is best', 2)"
    )
    await testdb.commit()

    client = TestClient(app)

    response = client.get("/api/plants/1/notes/1")
    notes = Notes.validate_python(response.json())

    # Only Goödel's notes
    assert len(notes) == 0


async def insert_notes(db: Connection):
    await db.execute("INSERT INTO Users (ID, Username) VALUES (1, 'Jahamaha')")
    await db.execute("INSERT INTO Users (ID, Username) VALUES (2, 'Larpoon')")
    await db.execute("INSERT INTO Users (ID, Username) VALUES (3, 'Old Shed')")

    await db.execute("INSERT INTO Plants (ID, UserID, Name) VALUES (1, 1, 'Jim')")
    await db.execute("INSERT INTO Plants (ID, UserID, Name) VALUES (2, 1, 'Job')")
    await db.execute("INSERT INTO Plants (ID, UserID, Name) VALUES (3, 2, 'Jab')")
    await db.execute("INSERT INTO Plants (ID, UserID, Name) VALUES (4, 3, 'Joggilin')")

    await db.execute(
        "INSERT INTO Notes (ID, PlantID, Note, Rating) VALUES (1, 1, 'pain', 1)"
    )
    await db.execute(
        "INSERT INTO Notes (ID, PlantID, Note, Rating) VALUES (2, 1, 'spain', 5)"
    )

    await db.execute(
        "INSERT INTO Notes (ID, PlantID, Note, Rating) VALUES (3, 2, 'portugal', 4)"
    )

    await db.execute(
        "INSERT INTO Notes (ID, PlantID, Note, Rating) VALUES (4, 3, 'poland', 6)"
    )
    await db.commit()


@pytest.mark.parametrize("user_id, plant_id", [(1, 1), (1, 2), (2, 3), (3, 4)])
async def test_get_all_notes(
    user_id: int, plant_id: int, testdb: Connection, test_server: None
) -> None:
    await insert_notes(testdb)
    client = TestClient(app)
    client.cookies.set("auth-token", mangle_cookie(user_id))
    for response_note in Notes.validate_python(
        client.get(f"api/plants/{plant_id}/notes").json()
    ):
        note_row = await testdb.execute_fetchall(
            "SELECT PlantID, Note, Rating FROM Notes WHERE ID = ?", (response_note.id,)
        )
        assert (true_note := note_row.__iter__().__next__()) is not None

        assert response_note.plant_id == true_note["PlantID"]
        assert response_note.note == true_note["Note"]
        assert response_note.rating == true_note["Rating"]


async def test_delete_notes(testdb: Connection, test_server: None):
    await testdb.execute("INSERT INTO Users (ID, Username) VALUES (1, 'Foo')")
    await testdb.execute("INSERT INTO Plants (ID, UserID, Name) VALUES (1, 1, 'Bar')")

    await testdb.execute(
        "INSERT INTO Notes (ID, PlantID, Note, Rating) VALUES (1, 1, 'fargle', 1)"
    )

    client = TestClient(app)
    client.cookies.set("auth-token", mangle_cookie(1))

    delete_response = client.delete("/api/plants/1/notes/1")
    assert delete_response.is_success

    cursor = await testdb.execute("SELECT EXISTS (SELECT 1 FROM Notes WHERE ID = 1)")
    note_row = await cursor.fetchone()
    assert note_row is not None and not note_row[0]


async def test_insert_note(testdb: Connection, test_server: None):
    await testdb.execute("INSERT INTO Users (ID, Username) VALUES (1, 'Foo')")
    await testdb.execute("INSERT INTO Plants (ID, UserID, Name) VALUES (1, 1, 'Bar')")

    client = TestClient(app)
    client.cookies.set("auth-token", mangle_cookie(1))

    post_response = client.post(
        "/api/plants/1/notes", data={"note": "This is a great note", "rating": "2"}
    )
    assert post_response.is_success
    response_plant = NoteSchema.model_validate(post_response.json())

    cursor = await testdb.execute(
        "SELECT PlantID, Note, Rating FROM Notes WHERE ID = ?", (response_plant.id,)
    )
    note_row = await cursor.fetchone()
    assert note_row is not None

    assert response_plant.plant_id == note_row["PlantID"]
    assert response_plant.note == note_row["Note"]
    assert response_plant.rating == note_row["Rating"]
