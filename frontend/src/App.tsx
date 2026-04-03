import "./App.css";
import {Routes, Route} from "react-router-dom"
import Home from "./Pages/Home/Home"
import SensorPage from "./Pages/Dev/SensorPage";
import PlantPage from "./Pages/Dev/PlantPage.tsx";
import DevPage from "./Pages/Dev/DevPage.tsx";

function App() {
    return (
        <>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/dev" element={<DevPage />} />
                <Route path="/dev/sensors" element={<SensorPage />} />
                <Route path="/dev/plants" element={<PlantPage />} />
            </Routes>
        </>
    )
}

export default App