import "./PlantPage.css";
import {useState} from "react";

export type NoteEntry = [string, string];
export type NoteEntries = NoteEntry[];

export function Notes({notes}: {notes: NoteEntries}) {
    const [newNote, setNewNote] = useState("");
    const [currentNotes, setCurrentNotes] = useState<NoteEntries>(notes);

    const getCurrentDate = () => {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        return `${day}/${month}/${year}`;
    }

    const getCurrentTime = () => {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        return `${hours}:${minutes}`;
    }

    //Placeholder till we get endpoint
    const addNoteBackend = async (date: string, content: string) => {
        console.log("Adding note to backend ", {date, content});
        return true;
    }

    const addNote = async () => {
        if(!newNote.trim()){
            return;
        }

        const date = getCurrentDate();
        const time = getCurrentTime();
        const dateTime = `${date} ${time}`;

        const newNotes: NoteEntries = [...currentNotes, [dateTime, newNote]];
        setCurrentNotes(newNotes);
        setNewNote("");

        try {
            await addNoteBackend(date, newNote);
        } catch (error) {
            console.error("Error adding note to backend", error);
        }
    }

    const handleKeyPress = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            addNote();
        }
    };

    const noteList = currentNotes.map((note, index) => {
        return (
            <div key={index} style={{marginBottom: "12px", textAlign: "left"}}>
                <strong className="text">{note[0]}</strong>
                <p className="text">{note[1]}</p>
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
                    onKeyDown={handleKeyPress}
                    rows={1}
                />
                <button 
                    className="note-button" 
                    onClick={addNote}
                    disabled={!newNote.trim()}
                >
                    Add Note
                </button>
            </div>
        </div>
    )
}
