import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import './Admin.css';
import { API_BASE_URL } from './config';

function Admin() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAdminStats();
  }, []);

  const fetchAdminStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/stats`);
      const data = await response.json();
      setStats(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching admin stats:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="admin-container">
        <div className="loading">Loading admin dashboard...</div>
      </div>
    );
  }

  // Chart colors
  const COLORS = ['#3498db', '#e74c3c', '#f39c12', '#2ecc71', '#9b59b6'];
  
  // Prepare data for membership distribution pie chart
  const membershipData = stats?.membership_tiers?.map((tier, index) => ({
    name: tier.name,
    value: tier.count,
    color: COLORS[index % COLORS.length]
  })) || [];

  // Prepare data for revenue chart (mock monthly data)
  const revenueData = [
    { month: 'Jul', revenue: 7200 },
    { month: 'Aug', revenue: 7800 },
    { month: 'Sep', revenue: 8100 },
    { month: 'Oct', revenue: 7900 },
    { month: 'Nov', revenue: 8300 },
    { month: 'Dec', revenue: stats?.monthly_revenue || 8500 },
  ];

  // Active vs Inactive members
  const statusData = [
    { name: 'Active', value: stats?.active_members || 0, color: '#2ecc71' },
    { name: 'Inactive', value: (stats?.total_members || 0) - (stats?.active_members || 0), color: '#95a5a6' }
  ];

  // Azure Functions status - UPDATED: Billing is Deployed, others are Planned
  const azureFunctions = [
    { 
      name: 'Monthly Billing Generator', 
      status: 'Deployed',
      icon: '💰',
      description: 'Automatically generates monthly billing for all active members',
      schedule: '1st of every month at 12:00 AM',
      lastRun: 'Dec 10, 2025',
      nextRun: 'Jan 1, 2026'
    },
    { 
      name: 'Daily Stats Aggregator', 
      status: 'Planned',
      icon: '📊',
      description: 'Calculates and caches daily statistics for faster dashboard loading',
      schedule: 'Daily at midnight'
    },
    { 
      name: 'Membership Expiration Alerts', 
      status: 'Planned',
      icon: '⚠️',
      description: 'Sends email alerts for memberships expiring within 7 days',
      schedule: 'Weekly on Mondays at 9:00 AM'
    },
    { 
      name: 'Class Capacity Monitor', 
      status: 'Planned',
      icon: '👥',
      description: 'Monitors class capacities and sends alerts for under-utilized classes',
      schedule: 'Hourly'
    }
  ];

  return (
    <div className="admin-container">
      <nav className="admin-nav">
        <div className="nav-brand">
          <h2>🏋️ Smart Gym Admin</h2>
        </div>
        <div className="nav-links">
          <Link to="/admin" className="nav-link active">Dashboard</Link>
          <Link to="/" className="nav-link">Back to Login</Link>
        </div>
        <div className="nav-user">
          <span>Admin</span>
          <div className="user-avatar">A</div>
        </div>
      </nav>

      <div className="admin-content">
        <div className="dashboard-header">
          <h1>Analytics Dashboard</h1>
          <p>Real-time gym metrics and insights</p>
        </div>

        {/* Key Metrics Cards */}
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-icon">👥</div>
            <div className="metric-data">
              <h3>{stats?.total_members || 0}</h3>
              <p>Total Members</p>
              <span className="metric-change positive">+{stats?.new_this_month || 0} this month</span>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">💰</div>
            <div className="metric-data">
              <h3>${stats?.monthly_revenue || 0}</h3>
              <p>Monthly Revenue</p>
              <span className="metric-change negative">${stats?.outstanding || 0} pending</span>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">🏋️</div>
            <div className="metric-data">
              <h3>{stats?.total_classes || 0}</h3>
              <p>Active Classes</p>
              <span className="metric-change positive">{stats?.avg_attendance || 0}% attendance</span>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">📈</div>
            <div className="metric-data">
              <h3>{stats?.active_members ? 
                ((stats.active_members / stats.total_members) * 100).toFixed(1) : 0}%</h3>
              <p>Active Rate</p>
              <span className="metric-change positive">{stats?.active_members || 0} active</span>
            </div>
          </div>
        </div>

        {/* Charts Row 1 */}
        <div className="charts-row">
          {/* Membership Distribution Pie Chart */}
          <div className="chart-card">
            <h2>Membership Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={membershipData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {membershipData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Active vs Inactive Pie Chart */}
          <div className="chart-card">
            <h2>Member Status</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Charts Row 2 */}
        <div className="charts-row">
          {/* Revenue Trend */}
          <div className="chart-card full-width">
            <h2>Revenue Trend (Last 6 Months)</h2>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={revenueData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#34495e" />
                <XAxis dataKey="month" stroke="#ecf0f1" />
                <YAxis stroke="#ecf0f1" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#2c3e50', border: '1px solid #34495e' }}
                  labelStyle={{ color: '#ecf0f1' }}
                />
                <Area type="monotone" dataKey="revenue" stroke="#3498db" fill="#3498db" fillOpacity={0.6} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Popular Classes Bar Chart */}
        <div className="chart-card full-width">
          <h2>Most Popular Classes</h2>
          {stats?.popular_classes && stats.popular_classes.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.popular_classes}>
                <CartesianGrid strokeDasharray="3 3" stroke="#34495e" />
                <XAxis dataKey="name" stroke="#ecf0f1" />
                <YAxis stroke="#ecf0f1" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#2c3e50', border: '1px solid #34495e' }}
                  labelStyle={{ color: '#ecf0f1' }}
                />
                <Bar dataKey="bookings" fill="#e74c3c" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p style={{color: '#95a5a6', textAlign: 'center', padding: '2rem'}}>
              No class booking data available
            </p>
          )}
        </div>

        {/* Azure Functions Status */}
        <div className="section-card">
          <div className="section-header">
            <h2>⚡ Azure Functions Status</h2>
            <p className="section-subtitle">Automated background tasks and serverless computing</p>
          </div>
          <div className="functions-grid">
            {azureFunctions.map((func, index) => (
              <div className="function-card" key={index}>
                <div className="function-header">
                  <span className="function-icon">{func.icon}</span>
                  <div className="function-info">
                    <h3>{func.name}</h3>
                    <span className={`function-status ${func.status === 'Deployed' ? 'deployed' : 'planned'}`}>
                      {func.status}
                    </span>
                  </div>
                </div>
                <p className="function-description">{func.description}</p>
                <div className="function-schedule">
                  <span className="schedule-icon">⏰</span>
                  <span>{func.schedule}</span>
                </div>
                {func.status === 'Deployed' && (
                  <div className="function-execution">
                    <div className="execution-info">
                      <span>✓ Last Run: {func.lastRun}</span>
                      <span>→ Next Run: {func.nextRun}</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="section-card">
          <h2>Recent Activity</h2>
          {stats?.recent_activity && stats.recent_activity.length > 0 ? (
            <div className="activity-list">
              {stats.recent_activity.map((activity, index) => (
                <div className="activity-item" key={index}>
                  <div className="activity-icon">{activity.icon}</div>
                  <div className="activity-details">
                    <strong>{activity.title}</strong>
                    <small>{activity.description}</small>
                  </div>
                  <div className="activity-time">{activity.time}</div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{color: '#95a5a6', textAlign: 'center', padding: '2rem'}}>
              No recent activity found
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default Admin;