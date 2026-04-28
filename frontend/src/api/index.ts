import type { components } from "./types.ts";
export { api, APICONFIG } from "./api.ts";

export type Achievement = components["schemas"]["AchievementSchema"];
export type Plant = components["schemas"]["PlantSchema"];
export type Note = components["schemas"]["NoteSchema"];