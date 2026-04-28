import {type JSX, useEffect, useState} from "react";
import { api, APICONFIG } from "../../api/api";
import type { components } from "../../api/types"
import MultiSelectBox from "./LogFieldSelectBox.tsx";

type LogView = components["schemas"]["LogView"];
type LogField = components["schemas"]["LogField"];

export default function LogPage() {
    const [sensorID, setSensorId] = useState<number>();
    const [plantID, setPlantID] = useState<number>();
    const [logs, setLogs] = useState<LogView[]>([]);
    const [logFields, setLogFields] = useState<string[]>([])

    return (
        <>
            <InputSensor setSensorID={setSensorId} />
            <InputPlantID setPlantID={setPlantID} />
            <p> sensor: {sensorID}</p>
            <p> plant: {plantID}</p>

            <MultiSelectBox onChange={setLogFields} />

        </>
    )
}

function InputSensor( {setSensorID } : { setSensorID: (id: number) => void } ) : JSX.Element {
    return (
        <form>
            <input name="sensorID" type="number" onChange={(event) => setSensorID(parseInt(event.target.value)) } />
        </form>
    )
}

function InputPlantID ( {setPlantID } : { setPlantID: (id: number) => void } ) : JSX.Element {
    return (
        <form>
            <input name="sensorID" type="number" onChange={(event) => setPlantID(parseInt(event.target.value)) } />
        </form>
    )
}

interface Option {
    id: string;
    label: string;
}

interface MultiSelectBoxesProps {
    options: Option[];
    value?: string[];
    onChange?: (selected: string[]) => void;
}

function MultiSelectBoxes({
     options,
     value,
     onChange,
 }: MultiSelectBoxesProps) {
    const [internalSelected, setInternalSelected] = useState<Set<string>>(new Set());

    const isControlled = value !== undefined;
    const selectedSet = isControlled ? new Set(value) : internalSelected;

    const updateSelected = (next: Set<string>) => {
        if (!isControlled) setInternalSelected(new Set(next));
        onChange?.([...next]);
    };

    const toggle = (id: string) => {
        const next = new Set(selectedSet);
        next.has(id) ? next.delete(id) : next.add(id);
        updateSelected(next);
    };

    const selectAll = () => updateSelected(new Set(options.map((o) => o.id)));
    const clearAll = () => updateSelected(new Set());

    return (
        <div>
            <div>
                {options.map((option) => {
                    const isSelected = selectedSet.has(option.id);
                    return (
                        <label key={option.id}>
                            <input
                                type="checkbox"
                                checked={isSelected}
                                onChange={() => toggle(option.id)}
                            />
                            {option.label}
                        </label>
                    );
                })}
            </div>

            <div>
                {[...selectedSet].join(", ") || "Nothing selected"}
            </div>

            <div>
                <button onClick={selectAll}>Select all</button>
                <button onClick={clearAll}>Clear all</button>
            </div>
        </div>
    );
}