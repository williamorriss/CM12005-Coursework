import { type JSX } from "react";

import {useNavigate} from "react-router-dom";


function DevPage() : JSX.Element {
    const navigate = useNavigate();
   return (
       <>
           <p> Welcome to the dev page!  :) </p>
           <p> These endpoints are used for dev, but take a look to see examples for the endpoints</p>
           <button onClick={() => navigate("/dev/plants")}> Plant Dev</button>
           <button onClick={() => navigate("/dev/sensors")}> Sensor Dev</button>
       </>
   )
}



export default DevPage