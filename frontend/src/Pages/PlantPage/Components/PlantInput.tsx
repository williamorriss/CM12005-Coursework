import "../Styling/PlantInput.css";
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
            <div className="item-div">
                <h3 className="item-title">Mood:</h3>
                <form className="item-form" onSubmit={handleSubmit}>
                    <div className="input-container">
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
            <div className="item-div">
                <h3 className="item-title">Water:</h3>
                <form className="item-form" onSubmit={handleSubmit}>
                    <div className="input-container">
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
        <div className="background-div">
            <MoodPicker />
            <WaterSubmit />
        </div>
    )
}