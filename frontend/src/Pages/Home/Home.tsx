import { useAuth, type User } from "../../AuthContext";
import {type JSX, useEffect} from "react";
import "./Home.css";
import { Notes } from "../PlantPage/Notes";
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

function LoggedIn({logout, session, deleteUser, navigate} : LoginProps) : JSX.Element {
    return (
        <>
            <button onClick={logout}>logout</button>
            <p>{`Hello ${session?.username}`}</p>
            id = {session?.user_id}

            <button onClick={deleteUser}>Delete</button>

            {/* <Notes notes={[]} /> */}
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


