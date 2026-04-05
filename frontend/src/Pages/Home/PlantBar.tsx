import { PlantPicture } from "./PlantPicture";
import { type JSX } from "react";
import "./PlantBar.css";
import type {components} from "../../api/types.ts";
import type {NavigateFunction} from "react-router-dom";
import { api } from "../../api/api";

type Plant = components["schemas"]["PlantView"];

function Plants({ plants, deletePlant, navigate }: { plants: Plant[], deletePlant: (id: number) => void, navigate: NavigateFunction }) : JSX.Element {
    return (
        <div id="Plants">
            <ul>
                {plants.map((plant) => <Plant plant={plant} deletePlant={deletePlant} navigate={navigate} />)}
            </ul>
        </div>
    );
}

function Plant({ plant, deletePlant, navigate }: { plant: Plant, deletePlant: (id: number) => void, navigate: NavigateFunction }) : JSX.Element {
    const deleteMe = async () => {
        const { error } = await api.DELETE("/api/plants/{plant_id}", {
            params : {
                path : {
                    plant_id : plant.id
                }
            }
        });
        if (error) {
            alert(error);
            return;
        }

        deletePlant(plant.id);
    }
    return (
        <li key={plant.id} id="PlantImage">
            <PlantPicture name={plant.name} src={plant.image_url ?? `https://picsum.photos/seed/${plant.id}/200`} />
            <button onClick={() => navigate(`/plants/${plant.id}`)}> Goto Page </button>
            <button onClick={deleteMe}> Delete </button>
        </li>
    )
}

export default Plants