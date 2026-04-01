import "./App.css";
import {Routes, Route} from "react-router-dom"
import Home from "./Pages/Home/Home"
import SensorPage from "./Pages/Dev/SensorPage";

function App() {
    return (
        <>
            <Routes>
                <Route path="/dev/sensors" element={<SensorPage />} />
                <Route path="/" element={<Home />} />
            </Routes>
        </>
    )

}

export default App