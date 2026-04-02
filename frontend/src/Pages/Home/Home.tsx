import { useAuth, type User } from "../../AuthContext";
import { type JSX, useEffect } from "react";
import { Notes } from "../PlantPage/Notes";
import { useNavigate } from 'react-router-dom'

function Home() : JSX.Element {
    const { session, isLoggedIn, logout, deleteUser, login, getSession } = useAuth();
    const navigate = useNavigate();

    useEffect(() => { getSession().then() }, []);
    console.log(session);
    return (
        <>
            {isLoggedIn()
                ? <LoggedIn session={session!} deleteUser={deleteUser} navigate={navigate} logout={logout} />
                : <LoggedOut login={login} />
            }
        </>
    )
}


function LoggedIn({logout, session, deleteUser, navigate} :
{
    logout: () => void,
    session: User,
    deleteUser: () => void,
    navigate: (destination: string) => void,
}) : JSX.Element {
    return (
        <>
            <button onClick={logout}>logout</button>
            <p>{`Hello ${session?.username}`}</p>
            id = {session?.user_id}

            <button onClick={deleteUser}>Delete</button>

            <Notes plantID={1} />
            <button onClick={() => navigate("/dev/sensors")}> dev </button>
        </>
    )
}

function LoggedOut({login}: { login: () => void }) : JSX.Element {
    return (
        <>
            <button onClick={login}>login</button>
        </>
    )
}

export default Home;
