import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './AgentsPage.css';

const AgentsPage = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Mock agents data - in production this would come from API
    const mockAgents = [
      {
        id: 'portfolio-agent',
        name: 'Portfolio Management Agent',
        category: 'Finance',
        description: 'AI-powered portfolio management with real-time market data and intelligent trading recommendations.',
        capabilities: [
          'Real-time market analysis',
          'Risk assessment and management', 
          'Automated portfolio rebalancing',
          'Performance tracking and reporting'
        ],
        bestFor: ['Financial Advisors', 'Investment Managers', 'Individual Investors'],
        connectors: ['Market Data APIs', 'Trading Platforms', 'Banking Systems'],
        status: 'active',
        infoRoute: '/agents/info/portfolio-agent',
        agentRoute: 'https://portfolio-agent-frontend-production.up.railway.app',
        icon: '📊'
      },
      {
        id: 'document-review',
        name: 'Document Review Agent',
        category: 'Legal',
        description: 'Streamline document reviews with automated feedback, context, and compliance alignment.',
        capabilities: [
          'Contract analysis and review',
          'Compliance checking',
          'Risk identification',
          'Automated redlining'
        ],
        bestFor: ['Legal Teams', 'Compliance Officers', 'Contract Managers'],
        connectors: ['Document Management', 'Legal Databases', 'Workflow Systems'],
        status: 'coming-soon',
        infoRoute: '/agents/info/document-review',
        agentRoute: null,
        icon: '📄'
      },
      {
        id: 'customer-support',
        name: 'Customer Support Agent',
        category: 'Support',
        description: 'Enhance customer service with intelligent ticket routing, automated responses, and sentiment analysis.',
        capabilities: [
          'Intelligent ticket classification',
          'Automated response generation',
          'Sentiment analysis',
          'Escalation management'
        ],
        bestFor: ['Support Teams', 'Customer Success', 'Service Managers'],
        connectors: ['Help Desk Software', 'CRM Systems', 'Chat Platforms'],
        status: 'coming-soon',
        infoRoute: '/agents/info/customer-support',
        agentRoute: null,
        icon: '🎧'
      },
      {
        id: 'sales-assistant',
        name: 'Sales Assistant Agent',
        category: 'Sales',
        description: 'Accelerate sales processes with lead scoring, proposal generation, and pipeline management.',
        capabilities: [
          'Lead qualification and scoring',
          'Proposal automation',
          'Pipeline forecasting',
          'Competitive analysis'
        ],
        bestFor: ['Sales Teams', 'Business Development', 'Account Managers'],
        connectors: ['CRM Systems', 'Email Platforms', 'Sales Tools'],
        status: 'coming-soon',
        infoRoute: '/agents/info/sales-assistant',
        agentRoute: null,
        icon: '💼'
      }
    ];

    // Simulate API call delay
    setTimeout(() => {
      setAgents(mockAgents);
      setLoading(false);
    }, 500);
  }, []);

  const handleViewClick = (agent) => {
    // Navigate to agent info page
    window.location.href = agent.infoRoute;
  };

  if (loading) {
    return (
      <div className="agents-page loading">
        <div className="container">
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Loading AI Agents...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="agents-page">
      <div className="container">
        {/* Header */}
        <div className="page-header">
          <h1>All agents</h1>
          <p>Explore our comprehensive suite of AI agents designed to transform your business operations.</p>
        </div>

        {/* Agents Grid */}
        <div className="agents-grid">
          {agents.map((agent) => (
            <div key={agent.id} className={`agent-card ${agent.status}`}>
              <div className="agent-header">
                <div className="agent-icon">{agent.icon}</div>
                <div className="agent-meta">
                  <h3 className="agent-name">{agent.name}</h3>
                  <span className="agent-category">{agent.category}</span>
                </div>
                <button 
                  className="view-btn"
                  onClick={() => handleViewClick(agent)}
                >
                  View
                </button>
              </div>
              
              <p className="agent-description">{agent.description}</p>
              
              {/* Capabilities */}
              <div className="agent-section">
                <h4>Capabilities</h4>
                <ul className="capabilities-list">
                  {agent.capabilities.map((capability, index) => (
                    <li key={index}>{capability}</li>
                  ))}
                </ul>
              </div>

              {/* Best For */}
              <div className="agent-section">
                <h4>Best for</h4>
                <div className="tags">
                  {agent.bestFor.map((role, index) => (
                    <span key={index} className="tag best-for">{role}</span>
                  ))}
                </div>
              </div>

              {/* Connectors */}
              <div className="agent-section">
                <h4>Connectors</h4>
                <div className="tags">
                  {agent.connectors.map((connector, index) => (
                    <span key={index} className="tag connector">{connector}</span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* CTA Section */}
        <div className="agents-cta">
          <h2>Need a Custom Agent?</h2>
          <p>We can build specialized AI agents tailored to your unique business requirements.</p>
          <Link to="/contact" className="btn-primary">
            Contact Our Team
          </Link>
        </div>
      </div>
    </div>
  );
};

export default AgentsPage; 