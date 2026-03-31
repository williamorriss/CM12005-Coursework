import './box.css';

export function PlantPicture({name, src}: {name: string, src: string}) {
    return (
        <div className="counter-box">
            <h1>{name}</h1>
            <img src={src} />
        </div>
    )
}