import { useParams } from "react-router-dom";
import { Notes } from "./Notes";
import "./PlantPage.css";
import { PlantPicture } from "./PlantPicture";
import type { components } from "../../api/types";
import { useEffect, useState } from "react";
import { api } from "../../api/api";
import { TimeSeriesChart } from "./Graph";
import { PlantGuide } from "./PlantGuide";

type PlantID = number;
type PlantData = components["schemas"]["PlantView"];

interface DataPoint {
  datetime: Date;
  value: number;
}

// Will be replaced with sensor data
// TODO: also need to wait for manual data endpoints
const sampleData: DataPoint[] = [
  { datetime: new Date('2024-01-01 10:00'), value: 10 },
  { datetime: new Date('2024-01-01 11:00'), value: 15 },
  { datetime: new Date('2024-01-01 12:00'), value: 7 },
  { datetime: new Date('2024-01-01 13:00'), value: 12 },
];

// forgive me but i really want a working example
// TODO: update this when theres a plant/ endpoint
const getPlantData = async (id: PlantID) => {
    const { data, error } = await api.GET("/api/plants", { });

    if (error) console.log(error);

    return data.find(x => x.id == id);
}

export default function PlantPage() {
    const [plantData, setPlantData] = useState(undefined as PlantData | undefined);

    const { id } = useParams();
    if (id == null) return

    const plantId = parseInt(id);

    useEffect(() => {
        (async () => {
            setPlantData(await getPlantData(plantId))
        })()
    }, [plantId])

    // placeholder image
    const imageSrc = "https://i.imgflip.com/7ia2aa.jpg";
    return (
        <>
            <PlantPicture name={plantData ? plantData.name : "loading..."} src={imageSrc} />
            <Notes plantID={plantId} />
            <TimeSeriesChart data={sampleData} title = "sample data" yAxisLabel="testY" xAxisLabel="Time"/>
            <PlantGuide />

        </>
    )
}
