import { type JSX, useState } from "react";
import { api } from "../../api/api";
import type { components } from "../../api/types";

type PlantView = components["schemas"]["PlantView"];
type NoteView = components["schemas"]["NoteView"];

function PlantPage(): JSX.Element {
    const [plantID, setPlantID] = useState<number>(0);
    const [plants, setPlants] = useState<PlantView[]>([]);
    const [notes, setNotes] = useState<NoteView[]>([]);

    const fetchPlants = async () => {
        const { data, error } = await api.GET("/api/plants", {});
        if (error) alert(error);
        if (data) setPlants(data);
    };

    const fetchNotes = async () => {
        const { data, error } = await api.GET("/api/plants/{plant_id}/notes", {
            params: { path: { plant_id: plantID } },
        });
        if (error) alert(error);
        if (data) setNotes(data);
    };

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            <section>
                <h3>Search/View</h3>
                <InputPlant setPlantID={setPlantID} />
                <button onClick={fetchPlants}> get plants </button>
                <button onClick={fetchNotes}> get notes </button>
            </section>

            <section>
                {plants.map((plant) => (
                    <PlantViewComponent key={plant.id} plant={plant} />
                ))}
                {notes.map((note) => (
                    <NoteViewComponent key={note.id} note={note} />
                ))}
            </section>

            <hr />
            <AddPlantForm />
            <AddNoteForm plantID={plantID} />
        </div>
    );
}

function InputPlant({ setPlantID }: { setPlantID: (id: number) => void }): JSX.Element {
    return (
        <input
            name="sensorID"
            type="number"
            placeholder="Enter Plant ID"
            onChange={(e) => setPlantID(parseInt(e.target.value) || 0)}
        />
    );
}

function PlantViewComponent({ plant }: { plant: PlantView }): JSX.Element {
    return (
        <div>
            <strong>Name:</strong> {plant.name} | <strong>ID:</strong> {plant.id}
        </div>
    );
}

function NoteViewComponent({ note }: { note: NoteView }): JSX.Element {
    return (
        <div>
            <strong>Note:</strong> {note.note} | <strong>ID:</strong> {note.id}
        </div>
    );
}

function AddPlantForm(): JSX.Element {
    const handleSubmit = async (form: FormData) => {
        const { error } = await api.POST("/api/plants", {
            params: {
                query: {
                    name: form.get("name") as string,
                },
            },
        });

        if (error) alert(error);
        else alert("Plant added!");
    };

    return (
        <form action={handleSubmit}>
            <h4>Add Plant</h4>
            <input type="text" name="name" placeholder="Plant Name" />
            <button type="submit">Add Plant</button>
        </form>
    );
}

function AddNoteForm({ plantID }: { plantID: number }): JSX.Element {
    const handleSubmit = async (form: FormData) => {

        const { error } = await api.POST("/api/plants/{plant_id}/notes", {
            params: {
                path: { plant_id: plantID },
                query: {
                    note: form.get("note") as string,
                    rating: 5,
                },
            },
        });

        if (error) alert(error);
        else alert("Note added!");
    };

    return (
        <form action={handleSubmit}>
            <h4>Add Note for Plant {plantID}</h4>
            <input type="text" name="note" placeholder="Write a note..." />
            <button type="submit">Add Note</button>
        </form>
    );
}

export default PlantPage;