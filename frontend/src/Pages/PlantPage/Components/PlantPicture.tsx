import "../Styling/PlantPicture.css"

export function PlantPicture({name, src}: {name: string, src: string}) {
    return (
        <div className="background-div">
            <h1 className="plant-name">{name}</h1>
            <img className="plant-image" src={src} />
        </div>
    )
}