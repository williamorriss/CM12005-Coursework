import { useAuth, type User } from "../../AuthContext";
import {type JSX, useEffect} from "react";
import "./Home.css";
import Plants from "./PlantBar"
import { useNavigate } from 'react-router-dom'




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
}

let plants: Plant[] = [];
let newPlant1 = { name: "plant1", src: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR9o9NlESDJDZsD51LdGdMt1miatn40Ktfxnw&s"}
plants.push(newPlant1);

let newPlant2 = { name: "plant2", src: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR9o9NlESDJDZsD51LdGdMt1miatn40Ktfxnw&s"}
plants.push(newPlant2);

let newPlant3 = { name: "plant3", src: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR9o9NlESDJDZsD51LdGdMt1miatn40Ktfxnw&s"}
plants.push(newPlant3);

let newPlant4 = { name: "plant4", src: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR9o9NlESDJDZsD51LdGdMt1miatn40Ktfxnw&s"}
plants.push(newPlant4);

let newPlant5 = { name: "plant5", src: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR9o9NlESDJDZsD51LdGdMt1miatn40Ktfxnw&s"}
plants.push(newPlant5);

let newPlant6 = { name: "plant6", src: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR9o9NlESDJDZsD51LdGdMt1miatn40Ktfxnw&s"}
plants.push(newPlant6);

function LoggedIn({logout, session, deleteUser, navigate} : LoginProps) : JSX.Element {
    return (
        <>
            <button onClick={logout}>logout</button>
            <p>{`Hello ${session?.username}`}</p>
            id = {session?.user_id}

            <button onClick={deleteUser} id="DeleteUser">Delete</button>

            {/* placeholder till endpoints from backend*/}

            <Plants plants={plants} />
            <button onClick={() => navigate("/dev/sensors")}> dev </button>
            <button onClick={() => navigate("/dev/sensors")}> wacky-silly </button>
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


