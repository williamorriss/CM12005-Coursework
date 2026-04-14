import CloseButtonImg from "./assets/close.svg";
import "./Popup.css"

export default function Popup({isOpen, onRequestClose, children}: {isOpen: boolean, onRequestClose: () => void, children: React.ReactNode}) {
    if (!isOpen) {
        return null
    }

    return (
        <div className="popup-overlay">
            <div className="popup-content">
                <button className="popup-close" onClick={onRequestClose}>
                    <img src={CloseButtonImg}></img>
                </button>
                {children}
            </div>
        </div>
    )
}
