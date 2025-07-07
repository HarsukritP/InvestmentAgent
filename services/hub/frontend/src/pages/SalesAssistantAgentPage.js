import React from 'react';
import { Link } from 'react-router-dom';
import './AgentInfoPage.css';

const SalesAssistantAgentPage = () => {
  const handleContactForEarlyAccess = () => {
    window.location.href = '/contact';
  };

  return (
    <div className="agent-info-page">
      <div className="container">
        {/* Breadcrumb */}
        <div className="breadcrumb">
          <Link to="/agents">All Agents</Link>
          <span>/</span>
          <span>Sales Assistant Agent</span>
        </div>

        {/* Agent Header */}
        <div className="agent-hero">
          <div className="agent-hero-content">
            <div className="agent-icon-large">💼</div>
            <div className="agent-info">
              <span className="agent-category">SALES</span>
              <h1>Sales Assistant Agent</h1>
              <p className="agent-tagline">
                Accelerate sales processes with lead scoring, proposal generation, and pipeline management.
              </p>
              <div className="agent-actions">
                <button className="btn-primary large" onClick={handleContactForEarlyAccess}>
                  Contact for Early Access
                </button>
                <Link to="/demos" className="btn-secondary large">
                  Book Demo
                </Link>
              </div>
            </div>
          </div>
          <div className="agent-status">
            <span className="status-badge coming-soon">Coming Soon</span>
          </div>
        </div>

        {/* Overview Section */}
        <section className="overview-section">
          <h2>Overview</h2>
          <div className="overview-grid">
            <div className="overview-card">
              <h3>What it does</h3>
              <p>
                Our Sales Assistant Agent supercharges your sales team with intelligent lead scoring, 
                automated proposal generation, and predictive pipeline management. It analyzes prospect 
                behavior and market data to optimize sales strategies and improve conversion rates.
              </p>
            </div>
            <div className="overview-card">
              <h3>How it works</h3>
              <p>
                The agent uses machine learning algorithms to analyze customer interactions, sales patterns, 
                and market trends. It integrates with your CRM and sales tools to provide real-time insights, 
                automate repetitive tasks, and predict sales outcomes.
              </p>
            </div>
            <div className="overview-card">
              <h3>Key Benefits</h3>
              <ul>
                <li>Higher conversion rates</li>
                <li>Improved lead qualification</li>
                <li>Automated proposal generation</li>
                <li>Predictive sales forecasting</li>
                <li>Enhanced sales productivity</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Capabilities Section */}
        <section className="capabilities-section">
          <h2>Capabilities</h2>
          <div className="capabilities-grid">
            <div className="capability-card">
              <div className="capability-icon">🎯</div>
              <h3>Lead Qualification & Scoring</h3>
              <p>Automatically score and prioritize leads based on behavior, demographics, and engagement patterns.</p>
            </div>
            <div className="capability-card">
              <div className="capability-icon">📝</div>
              <h3>Proposal Automation</h3>
              <p>Generate personalized proposals and sales materials based on prospect needs and preferences.</p>
            </div>
            <div className="capability-card">
              <div className="capability-icon">📈</div>
              <h3>Pipeline Forecasting</h3>
              <p>Predict sales outcomes and identify at-risk deals with advanced analytics and trend analysis.</p>
            </div>
            <div className="capability-card">
              <div className="capability-icon">🔍</div>
              <h3>Competitive Analysis</h3>
              <p>Monitor competitor activities and provide strategic insights for competitive positioning.</p>
            </div>
          </div>
        </section>

        {/* Best For Section */}
        <section className="best-for-section">
          <h2>Best for</h2>
          <div className="best-for-grid">
            <div className="best-for-card">
              <h3>Sales Teams</h3>
              <p>Empower sales representatives with AI-driven insights and automated workflows.</p>
              <ul>
                <li>Lead prioritization</li>
                <li>Sales process automation</li>
                <li>Performance optimization</li>
              </ul>
            </div>
            <div className="best-for-card">
              <h3>Business Development</h3>
              <p>Accelerate business growth with intelligent prospecting and market analysis.</p>
              <ul>
                <li>Market opportunity identification</li>
                <li>Prospect research automation</li>
                <li>Outreach optimization</li>
              </ul>
            </div>
            <div className="best-for-card">
              <h3>Account Managers</h3>
              <p>Maximize account value with predictive insights and relationship management tools.</p>
              <ul>
                <li>Account health monitoring</li>
                <li>Upsell opportunity identification</li>
                <li>Customer lifecycle management</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Integration Section */}
        <section className="integration-section">
          <h2>Integrations & Connectors</h2>
          <div className="integration-grid">
            <div className="integration-category">
              <h3>CRM Systems</h3>
              <div className="integration-tags">
                <span className="integration-tag">Salesforce</span>
                <span className="integration-tag">HubSpot</span>
                <span className="integration-tag">Pipedrive</span>
                <span className="integration-tag">Microsoft Dynamics</span>
              </div>
            </div>
            <div className="integration-category">
              <h3>Email Platforms</h3>
              <div className="integration-tags">
                <span className="integration-tag">Gmail</span>
                <span className="integration-tag">Outlook</span>
                <span className="integration-tag">Mailchimp</span>
                <span className="integration-tag">Constant Contact</span>
              </div>
            </div>
            <div className="integration-category">
              <h3>Sales Tools</h3>
              <div className="integration-tags">
                <span className="integration-tag">LinkedIn Sales Navigator</span>
                <span className="integration-tag">ZoomInfo</span>
                <span className="integration-tag">Outreach</span>
                <span className="integration-tag">SalesLoft</span>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="cta-section">
          <div className="cta-content">
            <h2>Ready to Supercharge Your Sales?</h2>
            <p>Get early access to our AI-powered sales assistant and transform your sales performance.</p>
            <div className="cta-actions">
              <button className="btn-primary large" onClick={handleContactForEarlyAccess}>
                Get Early Access
              </button>
              <Link to="/contact" className="btn-secondary large">
                Contact Sales
              </Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default SalesAssistantAgentPage; 