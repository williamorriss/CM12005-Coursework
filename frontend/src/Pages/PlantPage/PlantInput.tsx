import "./PlantPage.css"
import { useState } from "react";

function MoodPicker() {
    const [mood, setMood] = useState(3);

    // TODO: add functionality once there's an endpoint
    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        console.log(mood);
    };

    return (
        <>
            <div>
                <h3>Mood:</h3>
                <form onSubmit={handleSubmit}>
                    <div>
                        <select
                            value={mood}
                            onChange={(event) => setMood(parseInt(event.target.value))}
                        >
                            <option value="1">1 - Sad</option>
                            <option value="2">2</option>
                            <option value="3">3</option>
                            <option value="4">4</option>
                            <option value="5">5 - Happy</option>
                        </select>
                        <button type="submit">
                            Submit
                        </button>
                    </div>
                </form>
            </div>
        </>
    )
}

function WaterSubmit() {
    // TODO: add functionality once there's an endpoint
    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        console.log("Watered Plant");
    };

    return (
        <>
            <div>
                <h3>Water:</h3>
                <form onSubmit={handleSubmit}>
                    <div>
                        <button type="submit">
                            Watered Plant
                        </button>
                    </div>
                </form>
            </div>
        </>
    )
}

export function PlantInput() {


    return (
        <div className="counter-box">
            <MoodPicker />
            <WaterSubmit />
        </div>
    )
}