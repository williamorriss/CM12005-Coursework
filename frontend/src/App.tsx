import "./App.css";
import { useAuth } from "./AuthContext";
import {useEffect} from "react";

import { Notes } from "./PlantPage/Notes";

function App() {
    const { session, isLoggedIn, getSession, login, logout, deleteUser } = useAuth();
    useEffect(() => {getSession().then()}, []);
    console.log(session);
    if (isLoggedIn()) {
        return (
            <>
                <button onClick={logout}>logout</button>
                <p>{`Hello ${session?.username}`}</p>
                id = {session?.user_id}

                <button onClick={deleteUser}>Delete</button>

                <Notes notes={[]} />
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