import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// Concept for Interview: Higher-Order Components (HOC) or Wrapper Components
// ProtectedRoute wraps around routes that require authentication.
// If the user isn't authenticated, it immediately redirects (Navigate) them to the login page.
// This is standard practice in Single Page Applications (SPAs) to enforce client-side routing protection.

const ProtectedRoute = () => {
    const { token, loading } = useAuth();

    if (loading) {
        return <div>Loading...</div>; // Show a spinner in real scenarios
    }

    // If no token exists, redirect to login page. Otherwise, render child routes (Outlet).
    return token ? <Outlet /> : <Navigate to="/login" />;
};

export default ProtectedRoute;
