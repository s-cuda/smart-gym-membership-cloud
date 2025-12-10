import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Billing.css';

function Billing({ memberId = 1 }) {
  const [member, setMember] = useState(null);
  const [billing, setBilling] = useState([]);
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMemberData();
    fetchBillingData();
    fetchPlans();
  }, [memberId]);

  const fetchMemberData = async () => {
    try {
      const response = await fetch(`http://172.176.96.72:8000/members/${memberId}`);
      const data = await response.json();
      setMember(data);
    } catch (error) {
      console.error('Error fetching member:', error);
    }
  };

  const fetchBillingData = async () => {
    try {
      const response = await fetch(`http://172.176.96.72:8000/members/${memberId}/billing`);
      const data = await response.json();
      setBilling(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching billing:', error);
      setLoading(false);
    }
  };

  const fetchPlans = async () => {
    try {
      const response = await fetch(`http://172.176.96.72:8000/membership-plans/`);
      const data = await response.json();
      setPlans(data);
    } catch (error) {
      console.error('Error fetching plans:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const handleUpgrade = (planName) => {
    alert(`Upgrade to ${planName} - Feature coming soon!`);
  };

  if (loading) {
    return (
      <div className="billing-container">
        <div className="loading">Loading billing information...</div>
      </div>
    );
  }

  const latestBill = billing[0];
  const currentPlan = plans.find(p => p.plan_name === member?.membership_level);

  return (
    <div className="billing-container">
      <nav className="billing-nav">
        <div className="nav-brand">
            <h2>Smart Gym</h2>
        </div>
        <div className="nav-links">
            <Link to="/dashboard" className="nav-link">Dashboard</Link>
            <Link to="/billing" className="nav-link active">Billing</Link>
        </div>
        <div className="nav-user">
            <span>Welcome, {member?.first_name}</span>
            <div className="user-avatar">{member?.first_name?.charAt(0)}</div>
        </div>
        </nav>

      <div className="billing-content">
        <div className="billing-header">
          <h1>Billing & Membership</h1>
          <p>Manage your subscription and payment details</p>
        </div>

        <div className="billing-layout">
          <div className="billing-main">
            <div className="member-info-card">
              <h2>Account Information</h2>
              <div className="info-grid">
                <div className="info-item">
                  <span className="info-label">Full Name</span>
                  <span className="info-value">{member?.first_name} {member?.last_name}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Email</span>
                  <span className="info-value">{member?.email}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Phone</span>
                  <span className="info-value">{member?.phone}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Member Since</span>
                  <span className="info-value">{formatDate(member?.join_date)}</span>
                </div>
              </div>
            </div>

            <div className="current-plan-card">
              <div className="plan-header">
                <div>
                  <h2>Current Plan</h2>
                  <p className="plan-name">{member?.membership_level} Membership</p>
                </div>
                <div className="plan-price">
                  <span className="price">${currentPlan?.monthly_fee}</span>
                  <span className="period">/month</span>
                </div>
              </div>
              <div className="plan-features">
                <p>{currentPlan?.features}</p>
              </div>
            </div>

            <div className="billing-info-card">
              <h2>Payment Information</h2>
              <div className="billing-details">
                <div className="billing-row">
                  <span className="billing-label">Last Payment</span>
                  <span className="billing-value">
                    {latestBill ? formatDate(latestBill.billing_date) : 'N/A'}
                  </span>
                </div>
                <div className="billing-row">
                  <span className="billing-label">Amount Paid</span>
                  <span className="billing-value billing-amount">
                    ${latestBill?.amount || '0.00'}
                  </span>
                </div>
                <div className="billing-row">
                  <span className="billing-label">Payment Method</span>
                  <span className="billing-value">
                    {latestBill?.payment_method || 'Not Set'}
                  </span>
                </div>
                <div className="billing-row">
                  <span className="billing-label">Payment Status</span>
                  <span className={`billing-status ${latestBill?.payment_status?.toLowerCase()}`}>
                    {latestBill?.payment_status || 'N/A'}
                  </span>
                </div>
                <div className="billing-row highlight">
                  <span className="billing-label">Next Billing Date</span>
                  <span className="billing-value">
                    {latestBill ? formatDate(latestBill.next_billing_date) : 'N/A'}
                  </span>
                </div>
              </div>
            </div>

            <div className="billing-history-card">
              <h2>Billing History</h2>
              <div className="history-table">
                <div className="history-header">
                  <span>Date</span>
                  <span>Amount</span>
                  <span>Method</span>
                  <span>Status</span>
                </div>
                {billing.map((bill, index) => (
                  <div className="history-row" key={index}>
                    <span>{formatDate(bill.billing_date)}</span>
                    <span>${bill.amount}</span>
                    <span>{bill.payment_method}</span>
                    <span className={`status-badge ${bill.payment_status.toLowerCase()}`}>
                      {bill.payment_status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="billing-sidebar">
            <div className="upgrade-card">
              <h2>Available Plans</h2>
              <p className="upgrade-subtitle">Choose the plan that fits your goals</p>
              
              <div className="plans-list">
                {plans.map((plan, index) => (
                  <div 
                    key={index} 
                    className={`plan-option ${plan.plan_name === member?.membership_level ? 'current' : ''}`}
                  >
                    <div className="plan-option-header">
                      <h3>{plan.plan_name}</h3>
                      {plan.plan_name === member?.membership_level && (
                        <span className="current-badge">Current</span>
                      )}
                    </div>
                    <div className="plan-option-price">
                      <span className="plan-price-value">${plan.monthly_fee}</span>
                      <span className="plan-price-period">/month</span>
                    </div>
                    <div className="plan-option-features">
                      <p>{plan.features}</p>
                      {plan.class_access_limit ? (
                        <p className="feature-item">✓ {plan.class_access_limit} classes per week</p>
                      ) : (
                        <p className="feature-item">✓ Unlimited classes</p>
                      )}
                    </div>
                    {plan.plan_name !== member?.membership_level && (
                      <button 
                        className="upgrade-button"
                        onClick={() => handleUpgrade(plan.plan_name)}
                      >
                        {plans.findIndex(p => p.plan_name === member?.membership_level) < index ? 
                          'Upgrade' : 'Downgrade'}
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Billing;