import React, { createContext, useContext, useState, useEffect } from 'react';

// Concept for Interview: React Context API & State Management
// The Context API allows us to share state (like the current user and token) 
// across the entire component tree without having to pass props down manually (prop drilling).
// This is essential for authentication state since many components need to know if a user is logged in.

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(localStorage.getItem('token') || null);
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Here we could add logic to decode the JWT or fetch user details from /api/users/me
        // For now, if we have a token, we assume logged in.
        if (token) {
            setUser({ email: 'user@example.com' }); // Mocked for simplicity until /users/me is implemented
        } else {
            setUser(null);
        }
        setLoading(false);
    }, [token]);

    const login = async (email, password) => {
        // Concept for Interview: OAuth2 Form Data format requirement
        // Notice we are sending URLSearchParams, not a JSON payload.
        // This is mandated by the OAuth2 spec for password credentials.
        const response = await fetch('http://localhost:8000/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({
                username: email,
                password: password,
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await response.json();
        setToken(data.access_token);
        localStorage.setItem('token', data.access_token);
    };

    const signup = async (email, password) => {
        const response = await fetch('http://localhost:8000/api/auth/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Signup failed');
        }
        
        // After signup, automatically login
        await login(email, password);
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('token');
    };

    return (
        <AuthContext.Provider value={{ user, token, login, signup, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};
