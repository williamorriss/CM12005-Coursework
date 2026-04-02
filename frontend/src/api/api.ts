import createClient, {type ClientOptions} from "openapi-fetch";
import type { paths } from "./types";

export const APICONFIG: ClientOptions = {
    baseUrl: "http://localhost:8000",
    credentials: "include"
}

export const api = createClient<paths>({
    baseUrl: "http://localhost:8000",
    credentials: "include"
});
