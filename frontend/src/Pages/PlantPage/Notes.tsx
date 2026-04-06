import "./PlantPage.css";
import {useEffect, useState} from "react";
import { api } from "../../api/api";
import type { components } from "../../api/types";
import * as React from "react";

type NoteView = components["schemas"]["NoteView"];

type NewNote = {
    note: string;
    rating: number;
}

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
    const [newText, setNewText] = useState("");
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
            fetchNotes().then();
        }
    }, [plantID]);

    const addNoteBackend = async (plantID: number, note: NewNote) : Promise<NoteView | null> => {
        const sendForm = new FormData();
        sendForm.append("note", note.note)
        sendForm.append("rating", "5")
        const { data, error } = await api.POST("/api/plants/{plant_id}/notes", {
            params: {
                path: {plant_id: plantID},
            },
            body: sendForm as any,
        });

        if (error) {
            alert(error);
            return null;
        }

        return data as NoteView;
    }

    const addNote = async () => {
        // Checks to see if new note is empty
        if(!newText.trim()){
            return;
        }

        const newNote: NewNote = {
            note: newText,
            rating: 5,
        }

        const newNoteView = await addNoteBackend(plantID, newNote);
        if (newNoteView != null) {
            setCurrentNotes([...currentNotes, newNoteView]);
            setNewText("");

        }

        try {

        } catch (error) {
            console.error("Error adding note to backend", error);
        }
    }

    // Add note on enter
    const handleKeyPress = async (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            await addNote();
        }
    };

    const deleteNote = async (id: number) => {
        const { error} = await api.DELETE("/api/plants/{plant_id}/notes/{note_id}", {
            params : {
                path : {
                    plant_id : plantID,
                    note_id: id,
                }
            }
        });
        if (error) {
            alert(error);
            return null;
        }

        setCurrentNotes(currentNotes.filter(note => note.id !== id));
    }

    // Displaying each note in the list as a div
    const noteList = currentNotes.map((note) => {
        return (
            <div key={note.id} style={{marginBottom: "12px", textAlign: "left"}}>
                <strong className="text">{formatDateTime(note.timestamp)}</strong>
                <p className="text">{note.note}</p>
                <button onClick={() => deleteNote(note.id)}> Delete </button>
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
                    value={newText}
                    onChange={(e) => setNewText(e.target.value)}
                    onKeyDown={handleKeyPress}
                    rows={1}
                />
                <button 
                    className="note-button" 
                    onClick={addNote}
                    disabled={!newText.trim()}
                >
                    Add Note
                </button>
            </div>
        </div>
    )
}