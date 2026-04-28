import "./App.css";
import {Routes, Route} from "react-router-dom"
import Home from "./Pages/Home/Home"
import SensorPage from "./Pages/Dev/SensorPage";
import DevPage from "./Pages/Dev/DevPage.tsx";
import PlantPage from "./Pages/PlantPage/PlantPage.tsx";
import GoalPage from "./Pages/GoalPage/GoalPage.tsx";
import LogPage from "./Pages/Dev/LogPage.tsx"
import Achievements from "./Pages/Dev/Achievements.tsx";

function App() {
    return (
        <>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/plants/:id" element={<PlantPage />} />
                <Route path="/dev" element={<DevPage />} />
                <Route path="/dev/sensors" element={<SensorPage />} />
                <Route path="/goals" element={<GoalPage />} />
                <Route path="/dev/logs" element={<LogPage />} />
                <Route path="dev/achievements" element={<Achievements/>} />
            </Routes>
        </>
    )

}

export default App