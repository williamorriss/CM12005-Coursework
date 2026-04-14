import { useRef, useState, type ChangeEventHandler, type DragEventHandler, type ReactEventHandler } from "react";
import "./AddPlantWidget.css"

const handleDragOver: ReactEventHandler<HTMLDivElement> = (e) => e.preventDefault();

const fileHoverBGColor = "rgb(133 141 148)";
const noFileHoverBGColor = "rgb(148 148 148)";

export default function FileInputBox({ file, onFileSelected }: { file: File | null, onFileSelected: (file: File) => void }) {
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDragEnter = () => setIsDragging(true);
    const handleDragLeave = () => setIsDragging(false);

    const handleDrop: DragEventHandler<HTMLDivElement> = (e) => {
        e.preventDefault();

        if (e.dataTransfer.files.length != 1) return;

        onFileSelected(e.dataTransfer.files[0]);
    };

    const onSubmitFile: ChangeEventHandler<HTMLInputElement> = (e) => {
        if (e.target.files && e.target.files.length == 1) {
            onFileSelected(e.target.files[0]);
        }
    }

    const onClick = (e: Event) => {
        fileInputRef.current!.click()
        e.stopPropagation();
    }

    if (file) {
        console.log(URL.createObjectURL(file));
    }
    const sectionContents = file ? 
    (
        <>
            <img className="file-image-preview" src={URL.createObjectURL(file)} />
        </>
    ) : (
        <>
             Upload files here! <br/>
             Click here to upload a file!
        </>
    )

    return (
        <>
            <input hidden ref={fileInputRef} type="file" onChange={onSubmitFile}/>
            <div
                className="file-drag-box"
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onClick={onClick}
                style={{
                    backgroundColor: isDragging ? fileHoverBGColor : noFileHoverBGColor,
                }}
            >
                {sectionContents}

            </div>
        </>
    )
}
