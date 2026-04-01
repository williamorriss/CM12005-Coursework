import { useAuth, type User } from "../../AuthContext";
import {type JSX, useEffect} from "react";

import { Notes } from "../PlantPage/Notes";
import { useNavigate } from 'react-router-dom'

<<<<<<< HEAD
function Home() : JSX.Element {
=======
export function Home() : JSX.Element {
>>>>>>> 13e1dc504d87b0fa4288ec041312f01c468236f7
    const { session, isLoggedIn, logout, deleteUser, login, getSession } = useAuth();
    const navigate = useNavigate();


    useEffect(() => {getSession().then()}, []);
    console.log(session);
    return (
        <>
            {isLoggedIn()
                ?  <LoggedIn session={session!} deleteUser={deleteUser} navigate={navigate} logout={logout} />
                : <LoggedOut login={login}/>
            }
        </>
    )

}

<<<<<<< HEAD

function LoggedIn({logout, session, deleteUser, navigate} :
{
=======
type LoginProps = {
>>>>>>> 13e1dc504d87b0fa4288ec041312f01c468236f7
    logout: () => void,
    session: User,
    deleteUser: () => void,
    navigate: (destination: string) => void,
<<<<<<< HEAD
}) : JSX.Element {
=======
}

function LoggedIn({logout, session, deleteUser, navigate} : LoginProps) : JSX.Element {
>>>>>>> 13e1dc504d87b0fa4288ec041312f01c468236f7
    return (
        <>
            <button onClick={logout}>logout</button>
            <p>{`Hello ${session?.username}`}</p>
            id = {session?.user_id}

            <button onClick={deleteUser}>Delete</button>

            <Notes notes={[]} />
<<<<<<< HEAD
            <button onClick={() => navigate("/dev/sensors")}> dev </button>
=======
            <button onClick={() => navigate("/dev/sensors")}> wacky-silly </button>
>>>>>>> 13e1dc504d87b0fa4288ec041312f01c468236f7
        </>
    )
}

<<<<<<< HEAD
function LoggedOut({login}: { login: () => void }) : JSX.Element {
=======
type LogoutProps = {
    login: () => void,
}

function LoggedOut({login}: LogoutProps) : JSX.Element {
>>>>>>> 13e1dc504d87b0fa4288ec041312f01c468236f7
    return (
        <>
            <button onClick={login}>login</button>
        </>
    )
<<<<<<< HEAD
}

export default Home;
=======
}
>>>>>>> 13e1dc504d87b0fa4288ec041312f01c468236f7
