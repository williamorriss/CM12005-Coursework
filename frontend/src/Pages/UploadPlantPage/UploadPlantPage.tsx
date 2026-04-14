import Popup from "../../Popup.tsx";
import { api } from "../../api/api";
import "../PlantPage/PlantPage.css";
import FileInputBox from "./FileInputBox";
import { useState, type ChangeEventHandler } from "react";

export default function UploadPlantPage(_: {}) {
    const [popUpOpen, setPopUpOpen] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [name, setName] = useState("")

    const uploadPlant = async () => {
        const formData = new FormData();
        formData.append("name", name);
        formData.append("picture", file!);

        console.log(await api.POST("/api/plants", {
            body: formData as any
        }));
    }

    const onTextboxChange: ChangeEventHandler<HTMLInputElement> = (e) => {setName(e.target.value)};

    return (
        <>
            <button onClick={() => setPopUpOpen(true)}>Open popup test</button>
            <Popup isOpen={popUpOpen} onRequestClose={() => setPopUpOpen(false)}>
                <h2>Add Plant</h2>
                <label className="upload-plant-widget-section flex-right">
                    Name:  
                    <input type="text" value={name} onChange={onTextboxChange} placeholder="Plant Name"/>
                </label>

                <label className="upload-plant-widget-section flex-down">
                    Image File: {file ? file.name : "None"}
                    <FileInputBox onFileSelected={setFile} file={file}/>
                </label>
                <button type="submit" onClick={uploadPlant} disabled={file == null}>Add Plant</button>
                {/* <div className="upload-plant-widget"> */}
                {/* </div> */}
            </Popup>
        </>
    )
}
