import { useEffect, useRef } from "react";
import CloseButtonImg from "./assets/close.svg";
import "./Popup.css"

export default function Popup({isOpen, onRequestClose, children}: {isOpen: boolean, onRequestClose: () => void, children: React.ReactNode}) {
    const popupRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: Event) => {
            if (popupRef.current && !popupRef.current.contains(event.target)) {
                onRequestClose();
            }
        };

        if (isOpen) {
            document.addEventListener("mousedown", handleClickOutside);
        }

        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [isOpen, onRequestClose]);

    if (!isOpen) {
        return null
    }


    return (
        <div className="popup-overlay">
            <div className="popup-content" ref={popupRef}>
                <button className="popup-close" onClick={onRequestClose}>
                    <img src={CloseButtonImg}></img>
                </button>
                {children}
            </div>
        </div>
    )
}
