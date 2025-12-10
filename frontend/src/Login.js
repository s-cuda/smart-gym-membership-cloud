import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async () => {
    setError('');
    
    if (!email) {
      setError('Please enter your email');
      return;
    }

    try {
      const response = await fetch('http://172.176.96.72:8000/members/');
      const members = await response.json();
      
      const member = members.find(m => m.email.toLowerCase() === email.toLowerCase());
      
      if (member) {
        onLogin(member.member_id);
        navigate('/dashboard');
      } else {
        setError('Member not found. Try: member1@gym.com');
      }
    } catch (error) {
      setError('Connection error. Make sure backend is running.');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleLogin();
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <h1>Smart Gym</h1>
          <p>AI-Powered Fitness</p>
        </div>

        <div className="login-form">
          {error && <div className="error-message">{error}</div>}
          
          <div className="input-group">
            <label>Email</label>
            <input 
              type="email" 
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyPress={handleKeyPress}
            />
          </div>

          <div className="input-group">
            <label>Password</label>
            <input 
              type="password" 
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyPress={handleKeyPress}
            />
          </div>

          <button className="login-button" onClick={handleLogin}>
            Login
          </button>

          <p className="demo-hint">
            Demo: Use any member email (e.g., member1@gym.com)
          </p>

          <p className="signup-text">
            Don't have an account? <a href="#">Sign up</a>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;