<<<<<<< HEAD
import createClient, {type ClientOptions} from "openapi-fetch";
import type { paths } from "./types";

export const APICONFIG: ClientOptions = {
    baseUrl: "http://localhost:8000",
    credentials: "include"
}

export const api = createClient<paths>(APICONFIG);
=======
import createClient from "openapi-fetch";
import type { paths } from "./types";

export const api = createClient<paths>({
    baseUrl: "http://localhost:8000",
    credentials: "include"
});
>>>>>>> 13e1dc504d87b0fa4288ec041312f01c468236f7
