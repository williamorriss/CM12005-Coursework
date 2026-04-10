import {useParams} from "react-router-dom";
import type { components } from "../../api/types";
import { useEffect, useState } from "react";
import { api } from "../../api/api";
import { useAuth, type User } from "../../AuthContext";
import {type NavigateFunction, useNavigate} from 'react-router-dom'



type UserID = number;
type UserData = components["schemas"]["UserSession"]

api.GET("/api/auth/session")


export default function UserPage ({ session, deleteUser }: {session: User, deleteUser: () => void}) {
    return (
        <div id="Profile">
            <h1>Welcome {session?.username}</h1>
            <h4>Your current stats are: </h4>
            <p>Stat1: <br/>
                Stat2: <br/>
                Stat3: <br/>
            </p>

            <button onClick={deleteUser}>delete</button>
        </div>
    )
}