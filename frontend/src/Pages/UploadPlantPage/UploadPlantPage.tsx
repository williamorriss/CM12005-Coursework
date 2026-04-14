import { api } from "../../api/api";
import "../PlantPage/PlantPage.css";
import FileInputBox from "./FileInputBox";
import { useState, type ChangeEventHandler } from "react";

export default function UploadPlantPage(_: {}) {
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
        <div className="upload-plant-widget">
            <h4>Add Plant</h4>
            <label className="upload-plant-widget-section">
                { "Name: " }
                <input type="text" value={name} onChange={onTextboxChange} placeholder="Plant Name"/>
            </label>
            <FileInputBox onFileSelected={setFile} />
            <button type="submit" onClick={uploadPlant} disabled={file == null}>Add Plant</button>
        </div>
    )
}
