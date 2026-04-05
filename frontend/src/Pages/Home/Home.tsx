import { useAuth, type User } from "../../AuthContext";
import {type JSX, useEffect, useState } from "react";
import "./Home.css";
import Plants from "./PlantBar"
import {type NavigateFunction, useNavigate} from 'react-router-dom'
import { api } from "../../api/api";
import type { components } from "../../api/types"

type PlantView = components["schemas"]["PlantView"];

function Home() : JSX.Element {
    const { session, isLoggedIn, logout, deleteUser, login, getSession } = useAuth();
    const navigate = useNavigate();

    useEffect(() => { getSession().then() }, []);
    console.log(session);
    return (
        <div id="login">
            {isLoggedIn()
                ? <LoggedIn session={session!} deleteUser={deleteUser} navigate={navigate} logout={logout} />
                : <LoggedOut login={login} />
            }
        </div>
    )

}

type LoginProps = {
    logout: () => void,
    session: User,
    deleteUser: () => void,
    navigate: NavigateFunction,
}

function LoggedIn({logout, session, deleteUser, navigate} : LoginProps) : JSX.Element {
    const [plants, setPlants] = useState<PlantView[]>([]);
    const deletePlant = (id: number) => {
        setPlants(plants.filter(plant => plant.id !== id));
    }

    const addPlant = (plant: PlantView) => {
        setPlants([...plants, plant]);
    }

    const fetchPlants = async () => {
        const { data, error } = await api.GET("/api/plants", {});
        if (error) alert(error);
        if (data) setPlants(data);
    };

    useEffect(() => {fetchPlants().then()}, []);


    return (
        <>
            {fetchPlants}

            <button onClick={logout}>logout</button>
            <p>{`Hello ${session?.username}`}</p>
            {/* id = {session?.user_id} */}

            <button onClick={deleteUser} id="DeleteUser">Delete</button>
            <AddPlantForm addPlant={addPlant} />

            <Plants plants={plants} deletePlant={deletePlant} navigate={navigate} />

            <button onClick={() => navigate("/dev")}> dev </button>
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


function AddPlantForm({ addPlant } : { addPlant: ( plants: PlantView) => void}): JSX.Element {
    const handleSubmit = async (form: FormData) => {
        const pictureFile = form.get("picture")! as File;
        const formData = new FormData();
        formData.append(
            "picture",
            pictureFile,
            pictureFile.name
        );
        formData.append("name", form.get("name") as string);

        const { data, error } = await api.POST("/api/plants", {
            body: formData as any,
        });

        if (error) {
            alert(error);
        }

        addPlant(data as PlantView);
    };

    return (
        <form action={handleSubmit}>
            <h4>Add Plant</h4>
            <input type="text" name="name" placeholder="Plant Name"/>
            <input type="file" name="picture"/>
            <button type="submit">Add Plant</button>
        </form>
    );
}

export default Home;