import { PlantPicture } from "./PlantPicture.tsx";
import { type JSX } from "react";
import "./AchievementBar.css";
import type {components} from "../../api/types.ts";
import type {NavigateFunction} from "react-router-dom";
import { api } from "../../api/api.ts";

type Achievement = components["schemas"]["PlantView"];

function Achievements({ achievements, deleteAchievement, navigate }: { achievements: [], deleteAchievement: (id: number) => void, navigate: NavigateFunction }) : JSX.Element {
    return (
        <div id="Achievements">
            <ul>
                {achievements.map((achievement) => <Achievement achievement={achievement} deleteAchievement={deleteAchievement} navigate={navigate} />)}
            </ul>
        </div>
    );
}

function Achievement({ achievement, deleteAchievement, navigate }: { achievement: Achievement, deleteAchievement: (id: number) => void, navigate: NavigateFunction }) : JSX.Element {
    const deleteMe = async () => {
        const { error } = await api.DELETE("/api/plants/{plant_id}", {
            params : {
                path : {
                    achievement_id : achievement.id
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