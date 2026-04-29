import { useState, type ChangeEventHandler } from "react";
import FileInputBox from "./FileInputBox";
import Popup from "./Popup.tsx";
import { api } from "./api/api";
import "./AddPlantWidget.css";

export default function AddPlantPopup({isOpen, onRequestClose} : {isOpen: boolean, onRequestClose: () => void}) {
    const [file, setFile] = useState<File | null>(null);
    const [name, setName] = useState("")

    const uploadPlant = async () => {
        const formData = new FormData();
        formData.append("name", name);
        formData.append("picture", file!, file!.name);

        await api.POST("/api/plants", {
            body: formData as any
        });

        window.location.reload();
    }

    const onTextboxChange: ChangeEventHandler<HTMLInputElement> = (e) => {setName(e.target.value)};

    const shouldDisable = (file == null) || (name == null)

    return (
        <Popup isOpen={isOpen} onRequestClose={onRequestClose}>
            <h2>Add Plant</h2>

            <form action={uploadPlant} >
                <label className="upload-plant-widget-section flex-right">
                    Name:  
                    <input type="text" value={name} onChange={onTextboxChange} placeholder="Plant Name"/>
                </label>

                <label className="upload-plant-widget-section flex-down">
                    Image File: {file ? file.name : "None"}
                    <FileInputBox onFileSelected={setFile} file={file}/>
                </label>
                <button type="submit" disabled={shouldDisable}>Add Plant</button>
            </form>
        </Popup>
    )
}
