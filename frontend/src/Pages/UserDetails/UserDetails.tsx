import {type JSX, useEffect, useState} from "react";
import { api } from "../../api/api";
import type { components } from "../../api/types"
import "./UserDetails.css"
import image from "./skeleton left.png"

function UserDetails() : JSX.Element {
    return (
            <div>
                <img id="accountImage" src={ image }></img>
                <button onClick = {changeImage}>Change profile image</button>
                
            </div>
    )


}

function changeImage() {
    //this does nothing for now until backend does some stuff
}

export default UserDetails;