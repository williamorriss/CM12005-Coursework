import {useParams} from "react-router-dom";
import type { components } from "../../api/types";
import { useEffect, useState } from "react";
import { api } from "../../api/api";
import { useAuth, type User } from "../../AuthContext";
import {type NavigateFunction, useNavigate} from 'react-router-dom'

import session from "../Home/Home.tsx"
import deleteUser from "../Home/Home.tsx"
import "./UserPage.css"


import image from "./skeleton left.png"







function UserPage () {
    return (
        <div id="Profile">
            <h1>Welcome</h1>
            <h4>Your current stats are: </h4>
            <p>Total Achievements: <br/>
                Total points: <br/>
                Total Number of Plants: <br/>
                Total Notes: <br/>
            </p>

            <textarea name="username" placeholder="PlaceHolder" />
            <br/>


            <button onClick={deleteUser}>delete Account :(</button>
        </div>
    )
}

export default function UserDetails() : JSX.Element {
    return (
            <div>
                <img id="accountImage" src={ image }></img>
                <button onClick = {changeImage}>Change profile image</button>
                <UserPage />
            </div>
    )


}

function changeImage() {
    //this does nothing for now until backend does some stuff
}
