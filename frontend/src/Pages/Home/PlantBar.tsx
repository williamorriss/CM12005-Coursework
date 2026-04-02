import { PlantPicture } from "./PlantPicture";
import "./PlantBar.css";


interface Plant {
    name: string;
    src: string;
}


const Plants = ({ plants }: { plants: Plant[] }) => {
    return (
        <ul>
        {plants.map((plant) => (
            <li key={plant.name}>
            <PlantPicture name={plant.name} src={plant.src} />
            </li>
        ))}
    </ul>
    );
}

export default Plants