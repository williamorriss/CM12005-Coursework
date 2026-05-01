from aiosqlite import Connection
from fastapi import status
from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from api.notes import NoteSchema
from api.plants import PlantSchema
from main import app
from tests.conftest import mangle_cookie

Notes = TypeAdapter(list[NoteSchema])


async def test_plant_flow(testdb: Connection, test_server: None) -> None:
    await testdb.execute("INSERT INTO Users (ID, Username) VALUES (1, 'Bolek')")
    client = TestClient(app)
    client.cookies.set("auth-token", mangle_cookie(1))

    # make new
    make_plant_request = client.post("/api/plants", data={"name": "bartholomew"})
    plant = PlantSchema.model_validate(make_plant_request.json())

    get_plant_request = client.get(f"/api/plants/{plant.id}")
    get_plant = PlantSchema.model_validate(get_plant_request.json())

    assert plant.id == get_plant.id
    assert plant.image_url == get_plant.image_url
    assert plant.name == get_plant.name

    make_note_request = client.post(
        f"api/plants/{plant.id}/notes", data={"note": "In vino veritas", "rating": "3"}
    )
    note = NoteSchema.model_validate(make_note_request.json())
    get_note_request = client.get(f"/api/plants/{plant.id}/notes")
    get_notes = Notes.validate_python(get_note_request.json())
    get_note = [n for n in get_notes if n.id == note.id][0]

    assert note.id == get_note.id
    assert note.note == get_note.note
    assert note.plant_id == get_note.plant_id
    assert note.rating == get_note.rating
    assert note.timestamp == get_note.timestamp

    # remove
    remove_note_request = client.delete(f"/api/plants/{plant.id}/notes/{note.id}")
    assert remove_note_request.is_success

    remove_note_request = client.delete(f"/api/plants/{plant.id}/notes/{note.id}")
    assert remove_note_request.status_code == status.HTTP_404_NOT_FOUND

    remove_plant_request = client.delete(f"/api/plants/{plant.id}")
    assert remove_plant_request.is_success
    remove_plant_request = client.delete(f"/api/plants/{plant.id}")
    assert remove_plant_request.status_code == status.HTTP_404_NOT_FOUND


async def test_dependence(testdb: Connection, test_server: None) -> None:
    await testdb.execute("INSERT INTO Users (ID, Username) VALUES (1, 'Bartholomew')")
    client = TestClient(app)
    client.cookies.set("auth-token", mangle_cookie(1))

    # make new
    make_plant_request = client.post("/api/plants", data={"name": "Freedle"})
    plant = PlantSchema.model_validate(make_plant_request.json())

    get_plant_request = client.get(f"/api/plants/{plant.id}")
    get_plant = PlantSchema.model_validate(get_plant_request.json())

    assert plant.id == get_plant.id
    assert plant.image_url == get_plant.image_url
    assert plant.name == get_plant.name

    make_note_request = client.post(
        f"api/plants/{plant.id}/notes", data={"note": "In vino veritas", "rating": "3"}
    )
    note = NoteSchema.model_validate(make_note_request.json())
    get_note_request = client.get(f"/api/plants/{plant.id}/notes")
    get_notes = Notes.validate_python(get_note_request.json())
    get_note = [n for n in get_notes if n.id == note.id][0]

    assert note.id == get_note.id
    assert note.note == get_note.note
    assert note.plant_id == get_note.plant_id
    assert note.rating == get_note.rating
    assert note.timestamp == get_note.timestamp

    # remove

    remove_plant_request = client.delete(f"/api/plants/{plant.id}")
    assert remove_plant_request.is_success
    remove_plant_request = client.delete(f"/api/plants/{plant.id}")
    assert remove_plant_request.status_code == status.HTTP_404_NOT_FOUND

    # deleted when plant is deleted
    remove_note_request = client.delete(f"/api/plants/{plant.id}/notes/{note.id}")
    assert remove_note_request.status_code == status.HTTP_404_NOT_FOUND
