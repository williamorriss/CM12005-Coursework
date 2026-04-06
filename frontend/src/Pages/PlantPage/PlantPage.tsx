import {useParams} from "react-router-dom";
import { Notes } from "./Notes";
import "./PlantPage.css";
import { PlantPicture } from "./PlantPicture";
import type { components } from "../../api/types";
import { useEffect, useState } from "react";
import { api } from "../../api/api";

type PlantID = number;
type PlantData = components["schemas"]["PlantView"];

// forgive me but i really want a working example
// TODO: update this when theres a plant/ endpoint /

const getPlantData = async (id: PlantID) : Promise<PlantData|null> => {
    const { data, error } = await api.GET("/api/plants/{plant_id}", {
        params: {
            path : {
                plant_id: id
            }
        }
    });

    if (error) {
        console.log(error);
        return null
    }

    console.log(data)


    return data as PlantData;
}

export default function PlantPage() {
    const [plantData, setPlantData] = useState<PlantData|null>(null);

    const { id } = useParams();
    if (id == null) return

    const plantId = parseInt(id);

    useEffect(() => {
        (async () => {
            setPlantData(await getPlantData(plantId))
        })()
    }, [plantId])

    // placeholder image
    const imageSrc = plantData?.image_url ?? "https://i.imgflip.com/7ia2aa.jpg";
    return (
        <>
            <PlantPicture name={plantData ? plantData.name : "loading..."} src={imageSrc} />
            <Notes plantID={plantId} />
        </>
    )
}