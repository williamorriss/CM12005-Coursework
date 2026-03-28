import './App.css'
import "./App.css";
import { useAuth } from "./AuthContext";
import {useEffect} from "react";

function App() {
    const { session, isLoggedIn, getSession, login, logout, deleteUser } = useAuth();
    useEffect(() => {getSession().then()}, []);
    console.log(session);
    if (isLoggedIn()) {
        return (
            <>
                <button onClick={logout}>logout</button>
                <p>{`Hello ${session?.username}`}</p>
                id = {session?.userID}

                <button onClick={deleteUser}>Delete</button>
            </>
        )
    } else {
        return (
            <>
                <button onClick={login}>login</button>
            </>
        )
    }

}

export default App