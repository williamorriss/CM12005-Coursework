import { useState, useEffect } from "react";
import { format } from 'date-fns';
import "./Styling/GoalPage.css";

interface TabProps {
    title: string
    colour: string
    onClick: () => void
}
function Tab({title, colour, onClick}: TabProps) {
    return (
        <button className="tab-button" style={{background: colour}} onClick={onClick}>
            {title}
        </button>
    )
}

interface GoalPanelProps {
    index: number
    content: string
    onComplete: (key: number) => void
    onDelete: (key: number) => void
}
function GoalPanel({index, content, onComplete, onDelete}: GoalPanelProps) {
    return (
        <div className="goal-panel">
            <div className="goal-content">
                {content}
            </div>
            <button className="goal-complete-button" onClick={() => onComplete(index)}>✓</button>
            <button className="goal-delete-button" onClick={() => onDelete(index)}>X</button>
        </div>
    )
}

interface CompletedPanelProps {
    content: string
    date: string
}
function CompletedPanel({content, date}: CompletedPanelProps) {
    return (
        <div className="goal-panel">
            <div className="goal-content">
                <p>Date Completed: {date}</p>
                <p>{content}</p>
            </div>
        </div>
    )
}


interface InputGoalBarProps {
    content: string
    onChange: (event: React.ChangeEvent<HTMLInputElement>) => void
    onSubmit: () => void
}
function InputGoalBar({content, onChange, onSubmit}: InputGoalBarProps) {
    return (
        <div className="input-goal-bar">
            <input className="input-goal-bar-content" type="text" value={content} onChange={onChange}></input>
            <button className="input-goal-bar-button" onClick={onSubmit}>Submit</button>
        </div>
    )
}

interface TabData{
    title: string
    colour: string
}
const tabs: TabData[] = [
    {
        title: "Current",
        colour: "rgb(0, 255, 200)",
    },
    {
        title: "Completed",
        colour: "rgb(0, 255, 0)",
    },
];

// Example goal data from endpoint
// TODO: replace with endpoint schema when available
interface GoalData{
    id: number
    content: string
}
interface CompletedData{
    id: number
    content: string
    date: string
}
const goalsExample: string[] = ["Goal 1", "Goal 2", "Goal 3", "Goal 4", "Goal 5", "Goal 6", "Goal 7", "Goal 8", "Goal 9", "Goal 10", "Goal 11", "Goal 12"];
const completedExample: string[] = ["Completed 1", "Completed 2", "Completed 3"];

export default function GoalPage() {
    const [currentTab, setCurrentTab] = useState(0);
    const [goals , setGoals] = useState<GoalData[]>(goalsExample.map((goal, index) => ({id: index, content: goal})));
    const [completed, setCompleted] = useState<CompletedData[]>(completedExample.map((goal, index) => ({id: index, content: goal, date: Date().toString()})));
    const [goalInput, setGoalInput] = useState("");

    const fetchGoals = async () => {
        console.log("Fetching goals")
        // TODO: replace with endpoint when available
    }
    const fetchCompleted = async () => {
        console.log("Fetching completed")
        // TODO: replace with endpoint when available
    }

    const addGoal = async () => {
        if (goalInput.trim() == "") return

        const nextId = Math.max(...goals.map((goal) => goal.id), 0) + 1;
        setGoals([...goals, {id: nextId, content: goalInput}]);
        setGoalInput("");

        console.log("Adding goal")
        // TODO: replace with endpoint when available
    }
    const deleteGoal = async (index: number) => {
        setGoals(goals.filter((goal) => goal.id != index));
        console.log("Deleting goal")
        // TODO: replace with endpoint when available
    }

    const onComplete = (index: number) => {
        if (goals.find((goal) => goal.id == index) == undefined) return
        const goal = goals.find((goal) => goal.id == index)
        const nextId = Math.max(...completed.map((goal) => goal.id), 0) + 1;
        setCompleted([...completed, {id: nextId, content: goal?.content ?? "", date: new Date().toString()}]);
        setGoals(goals.filter((goal) => goal.id != index));
        
        console.log("Completing goal")
        // TODO: replace with endpoint when available
    }

    useEffect(() => {
        fetchGoals();
        fetchCompleted();
    }, [addGoal, deleteGoal, onComplete]);

    const goalPanels = goals.map((goal) => <GoalPanel key={goal.id} content={goal.content} index={goal.id} onComplete={onComplete} onDelete={deleteGoal} />);
    const completedPanels = completed.map((goal) => <CompletedPanel key={goal.id} content={goal.content} date={format(new Date(goal.date), "dd/MM/yyyy")} />);

    return (
        <div className="goal-page">
            <h1>Goals</h1>
            <div className="tab-bar">
                {tabs.map((tab, index) => (
                    <Tab key={index} title={tab.title} colour={tab.colour} onClick={() => setCurrentTab(index)} />
                ))}
            </div>

            <div className="feed-container" style={{background: tabs[currentTab].colour}}>
                <div className="feed-div">
                    {currentTab == 0 ? goalPanels : completedPanels}
                </div>
                <InputGoalBar content={goalInput} onChange={(event) => setGoalInput(event.target.value)} onSubmit={addGoal} />
            </div>
        </div>
    );
}