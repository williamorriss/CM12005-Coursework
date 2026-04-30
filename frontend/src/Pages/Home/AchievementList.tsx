import { useEffect, useState, type JSX } from "react";
import { api, type Achievement } from "../../api/index.ts";
import "./AchievementList.css";


export default function AchievementList({}) : JSX.Element {
    const [achievements, setAchievement] = useState<Achievement[]>([]);

    useEffect(() => {
        api.GET("/api/achievements").then((res) => {
            if (res.data) {
                setAchievement(res.data)
            }
        });
    })

    return (
        <div id="achievements">
            <h2> Achievements: </h2>
            <ul>
                {achievements.map((achievement) => <Achievement code={achievement.code}/>)}
            </ul>
        </div>
    );
}

function Achievement({code}: {code: string}): JSX.Element {
    return (
        <li key={code} id="achievement">
            You got {code}!
        </li>
    )
}