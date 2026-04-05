import "../Styling/Notes.css";
import {useEffect, useState} from "react";
import { api } from "../../../api/api";
import type { components } from "../../../api/types";

type NoteView = components["schemas"]["NoteView"];

const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${day}/${month}/${year} ${hours}:${minutes}`;
}

export function Notes({plantID}: {plantID: number}) {
    // States
    const [newNote, setNewNote] = useState("");
    const [currentNotes, setCurrentNotes] = useState<NoteView[]>([]);

    const fetchNotes = async () => {
        const { data, error } = await api.GET("/api/plants/{plant_id}/notes", {
            params: { path: { plant_id: plantID } },
        });
        if (error) alert(error);
        if (data) setCurrentNotes(data);
    }
    useEffect(() => {
        if(plantID){
            fetchNotes();
        }
    }, [plantID]);

    const addNoteBackend = async (note: NoteView) => {
        try {
            await api.POST("/api/plants/{plant_id}/notes", {
                params: {
                    path: { plant_id: plantID },
                    query: {
                        note: note.note,
                        rating: note.rating,
                    },
                },
            });
        } catch (error) {
            console.error("Error adding note to backend", error);
        }
    }

    const addNote = async () => {
        // Checks to see if new note is empty
        if(!newNote.trim()){
            return;
        }

        const highestID = currentNotes.reduce((max, note) => Math.max(max, note.id), 0);
        const newID = highestID + 1;

        const newNoteView: NoteView = {
            id: newID,
            note: newNote,
            rating: 5,
            timestamp: new Date().toISOString().replace("T", " ").slice(0, 23),
        }
        const newNotes = [newNoteView, ...currentNotes];

        setCurrentNotes(newNotes);
        setNewNote("");

        try {
            await addNoteBackend(newNoteView);
        } catch (error) {
            console.error("Error adding note to backend", error);
        }
    }

    // Displaying each note in the list as a div
    const noteList = currentNotes.map((note) => {
        return (
            <div key={note.id} className="note-panel">
                <strong className="text">{formatDateTime(note.timestamp)}</strong>
                <p className="text">{note.note}</p>
            </div>
        )
    })

    return (
        <div className="notes-container">
            <div className="note-box">
                {currentNotes.length == 0 ? (
                    <div className="text">
                        No notes yet. Add one below!
                    </div>
                ) :(
                    noteList
                )}
            </div>

            <div className="note-input-container">
                <textarea
                    className="note-input"
                    placeholder="Add a note..."
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                    rows={2}
                />
                <button 
                    className="note-button" 
                    onClick={addNote}
                    disabled={!newNote.trim()}
                >
                    Submit
                </button>
            </div>
        </div>
    )
}
