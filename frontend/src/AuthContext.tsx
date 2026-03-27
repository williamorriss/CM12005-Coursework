import {createContext, useContext, useEffect, useState} from 'react'
import * as React from "react";

// Would be better to use a client (openapi client!!!) for fetching but for now
// basic fetch will do

export type User = {
    userID: number,
    username: string,
}


const AuthContext = createContext<AuthContextType | null>(null);

interface AuthContextType {
    session: User | null;
    login: () => void;
    getSession: () => Promise<User | null>;
    logout: () => void;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [session, setSession] = useState<User | null>(null);
    const getSession = async () => {
        try {
            // we should probably use openapi fetch etc
            const response = await fetch(
                "/auth/session",
                {credentials: "include"}
            )
            if (!response.ok) {
                setSession(null);
                return null;
            }

            const data = await response.json();

            const user: User = {
                userID: data.user_id as number,
                username: data.username as string,
            };
            setSession(user);
            return user;
        } catch (error) {
            console.error(error);
            setSession(null);
            return null;
        }
    };

    useEffect(() => {
        getSession().then();
    }, []);

    const login = () => {
        location.href =`/auth/login?redirect=${location.origin}`;
    };

    const logout = async () => {
        setSession(null);
        location.href =`/auth/logout`;
    }

    return (
        <AuthContext.Provider value={{ session, login, getSession, logout }}>
    {children}
    </AuthContext.Provider>
);
}

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("Context was null");
    }
    return context;
}