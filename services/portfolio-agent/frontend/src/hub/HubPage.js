import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './HubPage.css';

const HubPage = () => {
  const [agents, setAgents] = useState([]);
  const [hubStatus, setHubStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/');
      return;
    }

    // Fetch user info
    fetchUserInfo(token);
    
    // Fetch hub status and agents
    fetchHubData(token);
  }, [navigate]);

  const fetchUserInfo = async (token) => {
    try {
      const response = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData.user);
      }
    } catch (error) {
      console.error('Error fetching user info:', error);
    }
  };

  const fetchHubData = async (token) => {
    try {
      // Fetch hub status
      const statusResponse = await fetch('/api/hub/status', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (statusResponse.ok) {
        const status = await statusResponse.json();
        setHubStatus(status);
      }

      // Fetch available agents
      const agentsResponse = await fetch('/api/hub/agents', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (agentsResponse.ok) {
        const agentsData = await agentsResponse.json();
        setAgents(agentsData);
      } else {
        // If hub is not configured, show portfolio agent manually
        setAgents([{
          id: 'portfolio-agent',
          name: 'Portfolio Management Agent',
          slug: 'portfolio-agent',
          description: 'AI-powered portfolio management with real-time market data and intelligent trading recommendations.',
          icon_url: '/assets/portfolio-icon.png',
          frontend_route: '/portfolio-agent',
          status: 'active'
        }]);
      }
    } catch (error) {
      console.error('Error fetching hub data:', error);
      // Fallback to show portfolio agent
      setAgents([{
        id: 'portfolio-agent',
        name: 'Portfolio Management Agent',
        slug: 'portfolio-agent',
        description: 'AI-powered portfolio management with real-time market data and intelligent trading recommendations.',
        frontend_route: '/portfolio-agent',
        status: 'active'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleAgentClick = (agent) => {
    if (agent.slug === 'portfolio-agent') {
      // Navigate to existing portfolio app
      navigate('/portfolio');
    } else if (agent.frontend_route) {
      // Navigate to agent-specific route
      navigate(agent.frontend_route);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  if (loading) {
    return (
      <div className="hub-page loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading ProCogia AI Hub...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="hub-page">
      <header className="hub-header">
        <div className="header-content">
          <div className="logo-section">
            <img src="/assets/procogia-logo.png" alt="ProCogia" className="logo" />
            <h1>ProCogia AI Hub</h1>
            <p className="tagline">Your Gateway to AI-Powered Business Solutions</p>
          </div>
          
          {user && (
            <div className="user-section">
              <div className="user-info">
                {user.picture && <img src={user.picture} alt="Profile" className="user-avatar" />}
                <span className="user-name">{user.name}</span>
              </div>
              <button onClick={handleLogout} className="logout-btn">Logout</button>
            </div>
          )}
        </div>
      </header>

      <main className="hub-main">
        <div className="hub-content">
          <section className="welcome-section">
            <h2>Welcome to ProCogia AI Hub</h2>
            <p>Explore our suite of AI-powered agents designed to enhance your business operations.</p>
            
            {hubStatus && (
              <div className={`hub-status ${hubStatus.hub_configured ? 'configured' : 'basic'}`}>
                <span className="status-indicator"></span>
                <span className="status-text">
                  {hubStatus.hub_configured ? 'Full Hub Mode' : 'Portfolio Mode'}
                </span>
                <span className="agent-count">{hubStatus.agents_configured.length} agent(s) available</span>
              </div>
            )}
          </section>

          <section className="agents-section">
            <h3>Available AI Agents</h3>
            <div className="agents-grid">
              {agents.map((agent) => (
                <div key={agent.id || agent.slug} className="agent-card" onClick={() => handleAgentClick(agent)}>
                  <div className="agent-icon">
                    {agent.icon_url ? (
                      <img src={agent.icon_url} alt={agent.name} />
                    ) : (
                      <div className="default-icon">🤖</div>
                    )}
                  </div>
                  <div className="agent-info">
                    <h4 className="agent-name">{agent.name}</h4>
                    <p className="agent-description">{agent.description}</p>
                    <div className="agent-status">
                      <span className={`status-badge ${agent.status}`}>
                        {agent.status === 'active' ? 'Available' : 'Coming Soon'}
                      </span>
                    </div>
                  </div>
                  <div className="agent-arrow">→</div>
                </div>
              ))}
            </div>
          </section>

          {agents.length === 0 && (
            <section className="no-agents">
              <div className="no-agents-content">
                <h3>No Agents Available</h3>
                <p>The hub is being set up. Please check back soon for available AI agents.</p>
              </div>
            </section>
          )}
        </div>
      </main>

      <footer className="hub-footer">
        <div className="footer-content">
          <p>&copy; 2024 ProCogia AI. Empowering businesses with intelligent solutions.</p>
          <div className="footer-links">
            <a href="/about">About</a>
            <a href="/support">Support</a>
            <a href="/docs">Documentation</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HubPage; 