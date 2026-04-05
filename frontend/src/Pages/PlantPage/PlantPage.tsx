import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { api } from "../../api/api";
import type { components } from "../../api/types";

import { Notes } from "./Components/Notes";
import { PlantPicture } from "./Components/PlantPicture";
import { TimeSeriesChart } from "./Components/Graph";
import { PlantGuide } from "./Components/PlantGuide";
import { PlantInput } from "./Components/PlantInput";

import "./Styling/PlantPage.css";

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

    const graphList = Array.from({ length: 3 }, (_, index) => ({
      id: index,
      data: sampleData,
      title: `Sample data ${index + 1}`,
      xAxisLabel: "Time",
      yAxisLabel: "Value"
    }));

    // placeholder image
    const imageSrc = "https://i.imgflip.com/7ia2aa.jpg";
    return (
        <>
            <div className="main-container">
                <div className="left-container">
                    <Notes plantID={plantId} />
                    <PlantGuide />
                </div>

                <div className="middle-container">
                    <PlantPicture name={plantData?.name || "Loading..."} src={imageSrc} />
                    <PlantInput />
                </div>

                <div className="right-container">
                    {graphList.map((graph) => (
                        <TimeSeriesChart
                            key={graph.id}
                            data={graph.data}
                            title={graph.title}
                            xAxisLabel={graph.xAxisLabel}
                            yAxisLabel={graph.yAxisLabel}
                        />
                    ))}
                </div>
            </div>
        </>
    )
}
