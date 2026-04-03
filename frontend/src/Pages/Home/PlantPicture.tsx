import "./PlantPicture.css";

export function PlantPicture({name, src}: {name: string, src: string}) {
    return (
        <div className="counter-box">
            <p>{name}</p>
            <img src={src} />
        </div>
    )
}