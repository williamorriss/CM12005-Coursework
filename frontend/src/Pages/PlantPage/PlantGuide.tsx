import "./PlantPage.css";

export function PlantGuide() {
    const linkGuide: string = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";

    return (
        <div className="plant-guide-div">
            <h3 className="plant-guide-text">Plant Guide</h3>
            <a href={linkGuide}>
                <p>{linkGuide}</p>
            </a>
        </div>
    )
}