import "./App.css";
import {Routes, Route} from "react-router-dom"
import Home from "./Pages/Home/Home"
import SensorPage from "./Pages/Dev/SensorPage";
import DevPage from "./Pages/Dev/DevPage.tsx";
import PlantPage from "./Pages/PlantPage/PlantPage.tsx";
import UserDetails from "./Pages/UserDetails/UserDetails.tsx";

function App() {
    return (
        <>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/plants/:id" element={<PlantPage />} />
                <Route path="/dev" element={<DevPage />} />
                <Route path="/dev/sensors" element={<SensorPage />} />
                <Route path="/" element= {<UserDetails />} />
            </Routes>
        </>
    )

}

export default App