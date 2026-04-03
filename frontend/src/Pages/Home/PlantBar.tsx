import { PlantPicture } from "./PlantPicture";
import "./PlantBar.css";


interface Plant {
    name: string;
    src: string;
}


const Plants = ({ plants }: { plants: Plant[] }) => {
    return (
        <div id="Plants">
        <ul>
        {plants.map((plant) => (
            <li key={plant.name} id="PlantImage">
            <PlantPicture name={plant.name} src={plant.src} />
            </li>
        ))}
    </ul>
    </div>
    );
}

export default Plants