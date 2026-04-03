import {type JSX, useEffect, useState} from "react";
import { api } from "../../api/api";
import type { components } from "../../api/types";
import { useNavigate, type NavigateFunction} from "react-router-dom";

type PlantView = components["schemas"]["PlantView"];

function PlantPanel(): JSX.Element {
    const [plants, setPlants] = useState<PlantView[]>([]);
    const navigate = useNavigate();

    const deletePlant = (id: number) => {
        setPlants(plants.filter(plant => plant.id !== id));
    }

    const fetchPlants = async () => {
        const { data, error } = await api.GET("/api/plants", {});
        if (error) alert(error);
        if (data) setPlants(data);
    };

    useEffect(() => {fetchPlants().then()}, []);

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            <AddPlantForm plants={plants} setPlants={setPlants}/>
            <section>
                {plants.map((plant) => (
                    <PlantViewComponent key={plant.id} plant={plant} deletePlant={deletePlant} navigation={navigate}/>
                ))}

            </section>
        </div>
    );
}

function PlantViewComponent({ plant, navigation, deletePlant }: { plant: PlantView, navigation: NavigateFunction, deletePlant: (id: number) => void }): JSX.Element {
    const deleteMe = async () => {
        const { error } = await api.DELETE("/api/plants/{plant_id}", {
            params : {
                path : {
                    plant_id : plant.id
                }
            }
        });
        if (error) {
            alert(error);
            return;
        }

        deletePlant(plant.id);
    }

    return (
        <div>
            <p><strong>Name:</strong> {plant.name} </p>
            <img src={plant.image_url ?? `https://picsum.photos/seed/${plant.id}/200`} alt={plant.name} style={{ width: "200px", height: "auto" }}/>
            <button onClick={() => navigation(`/plants/${plant.id}`)}> Goto Page </button>
            <button onClick={deleteMe}> Delete </button>
        </div>
    );
}

function AddPlantForm({ plants, setPlants } : { plants: PlantView[], setPlants: ( plants: PlantView[]) => void}): JSX.Element {
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

        setPlants([...plants, data as PlantView]);
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
export default PlantPanel