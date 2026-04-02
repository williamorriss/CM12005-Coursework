import "./App.css";
import {Routes, Route} from "react-router-dom"
import Home from "./Pages/Home/Home"
import SensorPage from "./Pages/Dev/SensorPage";
import DevPlantPage from "./Pages/Dev/DevPlants.tsx";
import PlantPage from "./Pages/PlantPage/PlantPage.tsx";

function App() {
    return (
        <>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/dev/sensors" element={<SensorPage />} />
                <Route path="/plants/:id" element={<PlantPage />} />
                <Route path="/dev/plants" element={<DevPlantPage />} />
            </Routes>
        </>
    )

}

export default App