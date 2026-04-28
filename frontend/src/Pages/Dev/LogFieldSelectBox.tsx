import { useState } from "react";

const LOG_FIELDS = ["temperature", "ph", "inserted_timestamp"] as const;

interface MultiSelectBoxesProps {
    value?: string[];
    onChange?: (selected: string[]) => void;
}

export default function MultiSelectBoxes({ value, onChange }: MultiSelectBoxesProps) {
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

    const selectAll = () => updateSelected(new Set(LOG_FIELDS));
    const clearAll = () => updateSelected(new Set());

    return (
        <div>
            <div>
                {LOG_FIELDS.map((option) => (
                    <label key={option}>
                        <input
                            type="checkbox"
                            checked={selectedSet.has(option)}
                            onChange={() => toggle(option)}
                        />
                        {option}
                    </label>
                ))}
            </div>
            <div>{[...selectedSet].join(", ") || "Nothing selected"}</div>
            <div>
                <button onClick={selectAll}>Select all</button>
                <button onClick={clearAll}>Clear all</button>
            </div>
        </div>
    );
}