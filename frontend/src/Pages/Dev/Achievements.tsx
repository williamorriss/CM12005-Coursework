import {type JSX, useEffect, useState} from "react";
import { api, APICONFIG } from "../../api/api";

export default function Achievements(): JSX.Element {
    const [lastFetch, setLastFetch] = useState<string | null>();
    const [watching, setWatching] = useState<boolean>(true);


    useEffect(() => {
        if (!watching) {
            return
        }

        const source = new EventSource(`${APICONFIG.baseUrl}/api/achievements/stream`, {withCredentials: true});

        source.onmessage = (e) => {
            setLastFetch(e.data);
        };

        source.onerror = (err) => {
            console.error("EventSource failed:", err);
            source.close();
        };

        return () => {
            console.log("Closing connection...");
            source.close();
        };
    }, [watching]);

    const testSubscribe = async () => {
        const {error} = await api.POST("/api/achievements/test", {} as any);
        if (error) throw error;
    }

    return (
        <>
            <button onClick={testSubscribe}> TEST</button>
            <button onClick={() => setWatching(!watching)}> WATCH </button>
            {lastFetch}
        </>
    )
}