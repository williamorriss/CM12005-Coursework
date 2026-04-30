
import { type JSX, useState } from "react";

import { useNavigate} from 'react-router-dom'


import deleteUser from "../Home/Home.tsx"
import "./UserPage.css"


import image from "./skeleton left.png"







function UserPage () : JSX.Element {
    const [img, setImg] = useState(image)
    const navigate = useNavigate()

    function changeImage(e) {
        console.log(e.target.files)
        setImg(URL.createObjectURL(e.target.files[0]))
    } 
    return (
        <div id="Profile">
            <h1>Welcome</h1>
            <div>
                <img id="accountImage" src={ img }></img>
                <h2>Change profile picture:</h2>
                <input type="file" onChange={changeImage} />

                
            </div>
            <h4>Your current stats are: </h4>
            <p>Total Achievements: <br/>
                Total points: <br/>
                Total Number of Plants: <br/>
                Total Notes: <br/>
            </p>
            

            <br/>

            <button onClick={() => navigate("/")}>Home Page </button>
            <button onClick={deleteUser}>delete Account :(</button>
        </div>
    )
}

export default UserPage