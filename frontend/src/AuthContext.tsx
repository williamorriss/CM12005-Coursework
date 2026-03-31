import {createContext, useContext, useEffect, useState} from 'react'
import * as React from "react";
import { api } from './api/api';
import type { components } from './api/types';

export type User = components["schemas"]["UserSession"];

const AuthContext = createContext<AuthContextType | null>(null);

interface AuthContextType {
    isLoggedIn: () => boolean;
    session: User | null;
    login: () => void;
    getSession: () => Promise<User | null>;
    logout: () => void;
    refreshSession: () => Promise<boolean>;
    deleteUser: () => void;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [session, setSession] = useState<User | null>(null);
    const getSession = async () => {
        const { data, error } = await api.GET("/api/auth/session", {});
        if (error) {
            console.error(error);
            setSession(null);
            return null;
        }
        
        setSession(data);
        return data;
    };

    useEffect(() => {
        getSession().then();
    }, []);

    const login = () => {
        location.href =`/api/auth/login?redirect=${location.origin}`;
    };

    const isLoggedIn = () => session != null;

    const refreshSession = async () => {
        const { response } = await api.GET("/api/auth/refresh", {});
        return response.ok;
    }

    const deleteUser = async () => {
        setSession(null);
        location.href =`/api/auth/delete`;
    }

    const logout = async () => {
        setSession(null);
        location.href =`/api/auth/logout`;
    }

    return (
    <AuthContext.Provider value={{ session, login, isLoggedIn, getSession, logout, refreshSession, deleteUser }}>
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