import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import {AuthProvider} from "./AuthContext.tsx";

// @ts-ignore
createRoot(document.getElementById('root')).render(
    <AuthProvider>
      <StrictMode>
        <App />
      </StrictMode>
    </AuthProvider>
)