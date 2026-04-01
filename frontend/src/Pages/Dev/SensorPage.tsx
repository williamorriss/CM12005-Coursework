import {type JSX, useEffect, useState} from "react";
import { api, APICONFIG } from "../../api/api";
import type { components } from "../../api/types"

type SensorView = components["schemas"]["SensorView"];



function SensorPage(): JSX.Element {
    const [sensorID, setSensorID] = useState<number>(0);
    const [plantID, setPlantID] = useState<number>(0);
    const [lastFetch, setLastFetch] = useState<number | null>();
    const [sensors, setSensors] = useState<SensorView[]>([]);
    const [watching, setWatching] = useState<boolean>(false);

    const fetchSensors = async () => {
        const { data, error } = await api.GET("/api/sensors", {})
        if (error) {
            alert(error);
        }
        console.log(data);

        setSensors(data);
    }


    useEffect(() => {
        if (!watching || !sensorID) {
            return
        }

        const source = new EventSource(`${APICONFIG.baseUrl}/api/sensors/${sensorID}/stream`, {withCredentials: true});

        source.onmessage = (e) => {
            setLastFetch(e.data);
        };

        source.onerror = (err) => {
            console.error("EventSource failed:", err);
            source.close();
        };

        return () => {
            console.log("Closing connection...");
            source.close();
        };
    }, [watching, sensorID]);

    return (
        <>
            <InputSensor setSensorID={setSensorID} />
            <InputPlantID setPlantID={setPlantID} />
            SensorID: {sensorID}, plantID: {plantID}

            Found: {lastFetch}

            <button onClick={
                () => api.POST("/api/sensors/{sensor_id}/session", {
                    params: {
                    path: { sensor_id: sensorID! }
            }})}> Activate Session </button>

            <button onClick={
                () => api.DELETE("/api/sensors/{sensor_id}/session", {
                    params: {
                        path: { sensor_id: sensorID! }
                    }
                })
            }> Deactivate Session </button>

            <button onClick={() => setWatching(true)}> watch </button>
            <button onClick={() => setWatching(false)}> unwatch </button>

            <button onClick={fetchSensors}> get sensors </button>
            Sensors: {sensors.map((sensor) => <SensorViewComponent key={sensor.sensor_id} sensor = {sensor}/>)}
        </>
    )
}

function InputSensor( {setSensorID } : { setSensorID: (id: number) => void } ) : JSX.Element {
    return (
        <form>
            <input name="sensorID" type="number" onChange={(event) => setSensorID(parseInt(event.target.value)) } />
        </form>
    )
}

function InputPlantID ( {setPlantID } : { setPlantID: (id: number) => void } ) : JSX.Element {
    return (
        <form>
            <input name="sensorID" type="number" onChange={(event) => setPlantID(parseInt(event.target.value)) } />
        </form>
    )
}

function SensorViewComponent({sensor}: { sensor :SensorView}) : JSX.Element {
    return (
        <>
            Name: {sensor.name}
            ID: {sensor.sensor_id} Target: {sensor.plant_id}
        </>
    )

}









export default SensorPage;