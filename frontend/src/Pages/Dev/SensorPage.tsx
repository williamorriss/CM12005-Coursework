import { type JSX, useState } from "react";
import { api } from "../../api/api";

function SensorPage(): JSX.Element {
    const [activateSensorId, setActivateSensorId] = useState(1);
    const [deactivateSensorId, setDeactivateSensorId] = useState(1);
    const [addName, setAddName] = useState("");
    const [addPlantId, setAddPlantId] = useState("");
    const [deleteSensorId, setDeleteSensorId] = useState(1);
    const [updateSensorId, setUpdateSensorId] = useState(1);
    const [updateName, setUpdateName] = useState("");
    const [updatePlantId, setUpdatePlantId] = useState("");
    const [sensors, setSensors] = useState<unknown>(null);

    return (
        <>
            DEV PAGE

            <form onSubmit={e => { e.preventDefault(); api.POST("/api/sensors/{sensor_id}/session", {
                params: { path: { sensor_id: activateSensorId } }
            })}}>
                <label>Sensor ID: <input type="number" value={activateSensorId} onChange={e => setActivateSensorId(Number(e.target.value))} /></label>
                <button type="submit">Activate Sensor</button>
            </form>

            <form onSubmit={e => { e.preventDefault(); api.DELETE("/api/{sensor_id}/session", {
                params: { path: { sensor_id: deactivateSensorId } }
            })}}>
                <label>Sensor ID: <input type="number" value={deactivateSensorId} onChange={e => setDeactivateSensorId(Number(e.target.value))} /></label>
                <button type="submit">Deactivate Sensor</button>
            </form>

            <form onSubmit={e => { e.preventDefault(); api.POST("/api/sensors", {
                params: { query: { name: addName, plant_id: addPlantId ? Number(addPlantId) : undefined } }
            })}}>
                <label>Name: <input type="text" value={addName} onChange={e => setAddName(e.target.value)} /></label>
                <label>Plant ID: <input type="number" value={addPlantId} onChange={e => setAddPlantId(e.target.value)} /></label>
                <button type="submit">Add Sensor</button>
            </form>

            <form onSubmit={e => { e.preventDefault(); api.DELETE("/api/sensors/{sensor_id}", {
                params: { path: { sensor_id: deleteSensorId } }
            })}}>
                <label>Sensor ID: <input type="number" value={deleteSensorId} onChange={e => setDeleteSensorId(Number(e.target.value))} /></label>
                <button type="submit">Delete Sensor</button>
            </form>

            <form onSubmit={e => { e.preventDefault(); api.PATCH("/api/sensors/{sensor_id}", {
                params: {
                    path: { sensor_id: updateSensorId },
                    query: { name: updateName || undefined, plant_id: updatePlantId ? Number(updatePlantId) : undefined }
                }
            })}}>
                <label>Sensor ID: <input type="number" value={updateSensorId} onChange={e => setUpdateSensorId(Number(e.target.value))} /></label>
                <label>Name: <input type="text" value={updateName} onChange={e => setUpdateName(e.target.value)} /></label>
                <label>Plant ID: <input type="number" value={updatePlantId} onChange={e => setUpdatePlantId(e.target.value)} /></label>
                <button type="submit">Update Sensor</button>
            </form>

            <form onSubmit={async e => {
                e.preventDefault();
                const { data } = await api.GET("/api/sensors");
                setSensors(data);
            }}>
                <button type="submit">Get Sensors</button>
                {sensors && <pre>{JSON.stringify(sensors, null, 2)}</pre>}
            </form>
        </>
    );
}

export default SensorPage;