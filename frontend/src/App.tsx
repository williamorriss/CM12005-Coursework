import "./App.css";
import {Routes, Route} from "react-router-dom"
import Home from "./Pages/Home/Home"
import SensorPage from "./Pages/Dev/SensorPage";
import DevPage from "./Pages/Dev/DevPage.tsx";
import PlantPage from "./Pages/PlantPage/PlantPage.tsx";

function App() {
    return (
        <>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/plants/:id" element={<PlantPage />} />
                <Route path="/dev" element={<DevPage />} />
                <Route path="/dev/api.sensors" element={<SensorPage />} />
            </Routes>
        </>
    )

}

export default App