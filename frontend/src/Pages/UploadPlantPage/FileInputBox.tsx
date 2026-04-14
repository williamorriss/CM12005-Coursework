import { useRef, useState, type ChangeEventHandler, type DragEventHandler, type ReactEventHandler } from "react";
import "./AddPlantWidget.css"

const handleDragOver: ReactEventHandler<HTMLDivElement> = (e) => e.preventDefault();

export default function FileInputBox({ onFileSelected }: { onFileSelected: (file: File) => void }) {
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

    const onClick = () => {
        fileInputRef.current!.click()
    }

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
                backgroundColor: isDragging ? "#f0f8ff" : "#fff",
            }}
            >
                Hey hi there.
            </div>
        </>
    )
}
