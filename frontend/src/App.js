import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';
import Dashboard from './Dashboard';
import Billing from './Billing';
import Admin from './Admin';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [memberId, setMemberId] = useState(null);

  const handleLogin = (id) => {
    setIsLoggedIn(true);
    setMemberId(id);
  };

  return (
    <Router>
      <Routes>
        <Route 
          path="/" 
          element={
            isLoggedIn ? 
            <Navigate to="/dashboard" /> : 
            <Login onLogin={handleLogin} />
          } 
        />
        <Route 
          path="/dashboard" 
          element={
            isLoggedIn ? 
            <Dashboard memberId={memberId} /> : 
            <Navigate to="/" />
          } 
        />
        <Route 
          path="/billing" 
          element={
            isLoggedIn ? 
            <Billing memberId={memberId} /> : 
            <Navigate to="/" />
          } 
        />
        {/* Admin Route - No authentication for demo */}
        <Route path="/admin" element={<Admin />} />
      </Routes>
    </Router>
  );
}

export default App;