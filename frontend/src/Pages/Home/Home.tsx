import { useAuth, type User } from "../../AuthContext";
import {type JSX, useEffect, useState } from "react";
import "./Home.css";
import Plants from "./PlantBar"
import { useNavigate } from 'react-router-dom'
import { api } from "../../api/api";
import type { components } from "../../api/types"
// import { PlantPage } from "../Dev/DevPlants"


type PlantView = components["schemas"]["PlantView"];




export function Home() : JSX.Element {
    const { session, isLoggedIn, logout, deleteUser, login, getSession } = useAuth();
    const navigate = useNavigate();


    useEffect(() => {getSession().then()}, []);
    console.log(session);
    return (
        <div id="login">
            {isLoggedIn()
                ?  <LoggedIn session={session!} deleteUser={deleteUser} navigate={navigate} logout={logout} />
                : <LoggedOut login={login}/>
            }
        </div>
    )

}


type LoginProps = {
    logout: () => void,
    session: User,
    deleteUser: () => void,
    navigate: (destination: string) => void,
}


interface Plant {
    name: string;
    src: string;
    id: number;
}

let plants: Plant[] = [];


function LoggedIn({logout, session, deleteUser, navigate} : LoginProps) : JSX.Element {
    const [Plant, setPlants] = useState<PlantView[]>([]);

    const fetchPlants = async () => {
        const { data, error } = await api.GET("/api/plants", {});
        if (error) alert(error);
        if (data) setPlants(data);
    };

    return (
        <>
            {fetchPlants}
            
            <button onClick={logout}>logout</button>
            <p>{`Hello ${session?.username}`}</p>
            {/* id = {session?.user_id} */}

            <button onClick={deleteUser} id="DeleteUser">Delete</button>

            {/* placeholder till endpoints from backend*/}
            <Plants plants={plants} />
            <button onClick={() => navigate("/dev/sensors")}> dev </button>
            <button onClick={() => navigate("/dev/plants")}> add-plants? </button>
            <button onClick={() => navigate("/Home/PlantPage")}> view-plants </button> 
            {/* <button onClick={() => navigate("dev")}> plantPage? </button> */}
        </>
    )
}

type LogoutProps = {
    login: () => void,
}

function LoggedOut({login}: LogoutProps) : JSX.Element {
    return (
        <div id="LoginButton">
            <button onClick={login}>login</button>
        </div>
    )
}

export default Home


