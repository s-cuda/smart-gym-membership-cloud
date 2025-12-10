import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Dashboard.css';


function Dashboard({ memberId = 1 }) {
  const [member, setMember] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [weeklySchedule, setWeeklySchedule] = useState({});
  const [loading, setLoading] = useState(true);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);
  const [loadingSchedule, setLoadingSchedule] = useState(false);
  const [showRecommendations, setShowRecommendations] = useState(false);
  const [showSchedule, setShowSchedule] = useState(false);

  useEffect(() => {
    fetchMemberData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [memberId]);
  const fetchMemberData = async () => {
    try {
      const response = await fetch(`http://172.176.96.72:8000/members/${memberId}`);
      const data = await response.json();
      setMember(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching member:', error);
      setLoading(false);
    }
  };

  const handleGenerateRecommendations = async () => {
    setLoadingRecommendations(true);
    try {
      const response = await fetch(`http://172.176.96.72:8000/members/${memberId}/recommendations?top_n=5`);
      const data = await response.json();
      setRecommendations(data.recommendations || []);
      setShowRecommendations(true);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    } finally {
      setLoadingRecommendations(false);
    }
  };

  const handleGenerateSchedule = async () => {
    setLoadingSchedule(true);
    try {
      const response = await fetch(`http://172.176.96.72:8000/members/${memberId}/weekly-schedule`);
      const data = await response.json();
      setWeeklySchedule(data.weekly_schedule || {});
      setShowSchedule(true);
    } catch (error) {
      console.error('Error fetching schedule:', error);
    } finally {
      setLoadingSchedule(false);
    }
  };

  const calculateBMI = () => {
    if (!member?.height_cm || !member?.weight_kg) return 0;
    const heightM = member.height_cm / 100;
    return (member.weight_kg / (heightM * heightM)).toFixed(1);
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">Loading your personalized dashboard...</div>
      </div>
    );
  }

  const bmi = calculateBMI();

  return (
    <div className="dashboard-container">
      <nav className="dashboard-nav">
        <div className="nav-brand">
          <h2>Smart Gym</h2>
        </div>
          <div className="nav-links">
            <Link to="/dashboard" className="nav-link active">Dashboard</Link>
            <Link to="/billing" className="nav-link">Billing</Link>
          </div>
        <div className="nav-user">
          <span>Welcome, {member?.first_name}</span>
          <div className="user-avatar">{member?.first_name?.charAt(0)}</div>
        </div>
      </nav>

      <div className="dashboard-content">
        <div className="dashboard-header">
          <h1>Your Dashboard</h1>
          <p>Personalized fitness tracking powered by AI</p>
        </div>

        <div className="profile-section">
          <div className="profile-header">
            <div className="profile-avatar-large">
              {member?.first_name?.charAt(0)}{member?.last_name?.charAt(0)}
            </div>
            <div className="profile-info">
              <h2>Welcome back, {member?.first_name}!</h2>
              <p>{member?.membership_level} Member • {member?.gender}</p>
            </div>
          </div>
          
          <div className="bio-stats">
            <div className="bio-stat-row">
              <div className="bio-stat">
                <div className="bio-icon">📏</div>
                <div className="bio-data">
                  <span className="bio-value">{member?.height_cm}</span>
                  <span className="bio-label">Height (cm)</span>
                </div>
              </div>
              <div className="bio-stat">
                <div className="bio-icon">⚖️</div>
                <div className="bio-data">
                  <span className="bio-value">{member?.weight_kg}</span>
                  <span className="bio-label">Weight (kg)</span>
                </div>
              </div>
              <div className="bio-stat">
                <div className="bio-icon">💪</div>
                <div className="bio-data">
                  <span className="bio-value">{bmi}</span>
                  <span className="bio-label">BMI</span>
                </div>
              </div>
              <div className="bio-stat">
                <div className="bio-icon">🎂</div>
                <div className="bio-data">
                  <span className="bio-value">{member?.age}</span>
                  <span className="bio-label">Age (years)</span>
                </div>
              </div>
            </div>
            
            <div className="bio-stat-row">
              <div className="bio-stat">
                <div className="bio-icon">⏰</div>
                <div className="bio-data">
                  <span className="bio-value">{member?.preferred_time_slot}</span>
                  <span className="bio-label">Preferred Time</span>
                </div>
              </div>
              <div className="bio-stat">
                <div className="bio-icon">💎</div>
                <div className="bio-data">
                  <span className="bio-value">{member?.membership_level}</span>
                  <span className="bio-label">Membership</span>
                </div>
              </div>
              <div className="bio-stat">
                <div className="bio-icon">⏱️</div>
                <div className="bio-data">
                  <span className="bio-value">52</span>
                  <span className="bio-label">Avg Session (min)</span>
                </div>
              </div>
              <div className="bio-stat">
                <div className="bio-icon">🔥</div>
                <div className="bio-data">
                  <span className="bio-value">5</span>
                  <span className="bio-label">Day Streak</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="section">
          <h2>AI Recommendations For You</h2>
          
          {!showRecommendations ? (
            <div className="generate-section">
              <div className="generate-card">
                <div className="generate-icon">🤖</div>
                <h3>Discover Your Perfect Classes</h3>
                <p>Our AI will analyze your profile, fitness goals, and preferences to recommend classes tailored specifically for you.</p>
                <button 
                  className="generate-button" 
                  onClick={handleGenerateRecommendations}
                  disabled={loadingRecommendations}
                >
                  {loadingRecommendations ? (
                    <>
                      <span className="spinner"></span>
                      Analyzing Your Profile...
                    </>
                  ) : (
                    <>
                      ✨ Generate AI Recommendations
                    </>
                  )}
                </button>
                {loadingRecommendations && (
                  <div className="loading-steps">
                    <p>🤔 Analyzing your fitness profile...</p>
                    <p>⚡ Calculating match scores...</p>
                    <p>✨ Generating personalized suggestions...</p>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <>
              <div className="recommendations-grid">
                {recommendations?.map((rec, index) => (
                  <div className="recommendation-card" key={index}>
                    <div className="rec-header">
                      <h3>{rec.class_name}</h3>
                      <div className="match-badge">{rec.match_percentage}% Match</div>
                    </div>
                    <p className="rec-instructor">👤 {rec.instructor}</p>
                    <p className="rec-difficulty">📊 {rec.difficulty} • {rec.duration} min</p>
                    <p className="rec-description">{rec.description}</p>
                    <div className="rec-reasons">
                      {rec.reasons?.map((reason, i) => (
                        <span key={i} className="reason-tag">✓ {reason}</span>
                      ))}
                    </div>
                    <button className="book-button">Book Now</button>
                  </div>
                ))}
              </div>
              <button 
                className="refresh-button" 
                onClick={handleGenerateRecommendations}
              >
                🔄 Refresh Recommendations
              </button>
            </>
          )}
        </div>

        <div className="section">
          <h2>Your Weekly Schedule Builder</h2>
          
          {!showSchedule ? (
            <div className="generate-section">
              <div className="generate-card">
                <div className="generate-icon">📅</div>
                <h3>Build Your Perfect Week</h3>
                <p>Let AI create an optimized weekly schedule based on your top recommendations, preferred days, and time slots.</p>
                <button 
                  className="generate-button" 
                  onClick={handleGenerateSchedule}
                  disabled={loadingSchedule}
                >
                  {loadingSchedule ? (
                    <>
                      <span className="spinner"></span>
                      Building Your Schedule...
                    </>
                  ) : (
                    <>
                      🗓️ Generate Weekly Schedule
                    </>
                  )}
                </button>
                {loadingSchedule && (
                  <div className="loading-steps">
                    <p>📋 Reviewing available time slots...</p>
                    <p>🎯 Matching to your preferences...</p>
                    <p>✨ Optimizing your weekly plan...</p>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <>
              <div className="schedule-grid">
                {Object.entries(weeklySchedule || {}).map(([day, classes]) => (
                  <div className="day-card" key={day}>
                    <h3>{day}</h3>
                    <div className="day-classes">
                      {classes?.map((cls, index) => (
                        <div className="schedule-item" key={index}>
                          <div className="schedule-time">{cls.time}</div>
                          <div className="schedule-class">
                            <strong>{cls.class_name}</strong>
                            <small>{cls.room}</small>
                          </div>
                          <div className="schedule-spots">{cls.spots_left} spots</div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
              <button 
                className="refresh-button" 
                onClick={handleGenerateSchedule}
              >
                🔄 Rebuild Schedule
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;