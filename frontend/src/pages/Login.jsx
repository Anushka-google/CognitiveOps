import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Login.css';

const Login = () => {
    const [isLoginMode, setIsLoginMode] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    
    const { login, signup } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);
        
        try {
            if (isLoginMode) {
                await login(email, password);
            } else {
                await signup(email, password);
            }
            // Once successful, navigate to the Dashboard (or requested route)
            navigate('/dashboard');
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <h2>{isLoginMode ? 'Welcome Back' : 'Create an Account'}</h2>
                <p className="subtitle">
                    {isLoginMode 
                        ? 'Sign in to CognitiveOps to continue' 
                        : 'Sign up for CognitiveOps'}
                </p>
                
                {error && <div className="error-message">{error}</div>}
                
                <form onSubmit={handleSubmit} className="login-form">
                    <div className="form-group">
                        <label>Email</label>
                        <input 
                            type="email" 
                            required 
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="agent@cognitiveops.ai"
                        />
                    </div>
                    
                    <div className="form-group">
                        <label>Password</label>
                        <input 
                            type="password" 
                            required 
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                        />
                    </div>
                    
                    <button type="submit" disabled={loading} className="submit-btn">
                        {loading 
                            ? 'Processing...' 
                            : (isLoginMode ? 'Sign In' : 'Sign Up')}
                    </button>
                </form>
                
                <div className="toggle-mode">
                    {isLoginMode ? "Don't have an account? " : "Already have an account? "}
                    <button 
                        className="toggle-btn"
                        onClick={() => setIsLoginMode(!isLoginMode)}
                        type="button"
                    >
                        {isLoginMode ? 'Sign Up' : 'Sign In'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Login;
