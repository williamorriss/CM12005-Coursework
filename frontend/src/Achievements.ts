import {useEffect, useRef} from "react";
import { APICONFIG, type Achievement } from "./api";

export function useAchievementEffect(onAchievement: (achievement: Achievement) => void) : void {
    const handlerRef = useRef(onAchievement);
    handlerRef.current = onAchievement; // allows func to be swapped out
    useEffect(() => {
        const source = new EventSource(`${APICONFIG.baseUrl}/api/achievements/stream`, {withCredentials: true});

        source.onmessage = (e) => {
            const achievement = JSON.parse(e.data);
            handlerRef.current(achievement);
        };

        source.onerror = (err) => {
            console.error("EventSource failed:", err);
            source.close();
        };

        return () => {
            console.log("Closing connection...");
            source.close();
        };
    }, []);
}