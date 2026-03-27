import './App.css'
import "./App.css";
import { useAuth } from "./AuthContext";
import {useEffect} from "react";


function App() {
    const { session, getSession, login, logout } = useAuth();
    useEffect(() => {getSession().then()}, []);
    console.log(session);
    if (session != null) {
        return (
            <>
                <button onClick={logout}>logout</button>
                <p>{`Hello ${session?.username}`}</p>
                id = {session?.userID}
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