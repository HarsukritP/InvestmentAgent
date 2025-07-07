import React from 'react';
import { Link } from 'react-router-dom';
import './AgentInfoPage.css';

const CustomerSupportAgentPage = () => {
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
          <span>Customer Support Agent</span>
        </div>

        {/* Agent Header */}
        <div className="agent-hero">
          <div className="agent-hero-content">
            <div className="agent-icon-large">🎧</div>
            <div className="agent-info">
              <span className="agent-category">SUPPORT</span>
              <h1>Customer Support Agent</h1>
              <p className="agent-tagline">
                Enhance customer service with intelligent ticket routing, automated responses, and sentiment analysis.
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
                Our Customer Support Agent revolutionizes customer service by intelligently routing tickets, 
                providing automated responses, and analyzing customer sentiment. It integrates with existing 
                support systems to enhance efficiency and improve customer satisfaction.
              </p>
            </div>
            <div className="overview-card">
              <h3>How it works</h3>
              <p>
                Using advanced natural language processing and machine learning, the agent understands 
                customer inquiries, categorizes issues, and either provides instant solutions or routes 
                tickets to the most appropriate support representative.
              </p>
            </div>
            <div className="overview-card">
              <h3>Key Benefits</h3>
              <ul>
                <li>Faster response times</li>
                <li>Improved customer satisfaction</li>
                <li>Reduced workload for support teams</li>
                <li>24/7 availability</li>
                <li>Consistent service quality</li>
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
              <h3>Intelligent Ticket Classification</h3>
              <p>Automatically categorize and prioritize customer inquiries based on content and urgency.</p>
            </div>
            <div className="capability-card">
              <div className="capability-icon">🤖</div>
              <h3>Automated Response Generation</h3>
              <p>Generate personalized responses and solutions based on knowledge base and past interactions.</p>
            </div>
            <div className="capability-card">
              <div className="capability-icon">😊</div>
              <h3>Sentiment Analysis</h3>
              <p>Analyze customer emotions and escalate frustrated customers to human agents when needed.</p>
            </div>
            <div className="capability-card">
              <div className="capability-icon">⬆️</div>
              <h3>Escalation Management</h3>
              <p>Smart escalation to appropriate team members based on issue complexity and customer needs.</p>
            </div>
          </div>
        </section>

        {/* Best For Section */}
        <section className="best-for-section">
          <h2>Best for</h2>
          <div className="best-for-grid">
            <div className="best-for-card">
              <h3>Support Teams</h3>
              <p>Streamline support operations and reduce response times while maintaining quality service.</p>
              <ul>
                <li>Ticket management automation</li>
                <li>Response time optimization</li>
                <li>Quality assurance</li>
              </ul>
            </div>
            <div className="best-for-card">
              <h3>Customer Success</h3>
              <p>Proactively identify at-risk customers and improve overall customer experience.</p>
              <ul>
                <li>Customer health monitoring</li>
                <li>Proactive outreach</li>
                <li>Experience optimization</li>
              </ul>
            </div>
            <div className="best-for-card">
              <h3>Service Managers</h3>
              <p>Gain insights into support performance and optimize team efficiency.</p>
              <ul>
                <li>Performance analytics</li>
                <li>Resource optimization</li>
                <li>Quality monitoring</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Integration Section */}
        <section className="integration-section">
          <h2>Integrations & Connectors</h2>
          <div className="integration-grid">
            <div className="integration-category">
              <h3>Help Desk Software</h3>
              <div className="integration-tags">
                <span className="integration-tag">Zendesk</span>
                <span className="integration-tag">ServiceNow</span>
                <span className="integration-tag">Freshdesk</span>
                <span className="integration-tag">Jira Service Desk</span>
              </div>
            </div>
            <div className="integration-category">
              <h3>CRM Systems</h3>
              <div className="integration-tags">
                <span className="integration-tag">Salesforce</span>
                <span className="integration-tag">HubSpot</span>
                <span className="integration-tag">Microsoft Dynamics</span>
                <span className="integration-tag">Pipedrive</span>
              </div>
            </div>
            <div className="integration-category">
              <h3>Chat Platforms</h3>
              <div className="integration-tags">
                <span className="integration-tag">Slack</span>
                <span className="integration-tag">Microsoft Teams</span>
                <span className="integration-tag">Intercom</span>
                <span className="integration-tag">Discord</span>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="cta-section">
          <div className="cta-content">
            <h2>Ready to Transform Customer Support?</h2>
            <p>Join the waitlist for our AI-powered customer support solution and revolutionize your service operations.</p>
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

export default CustomerSupportAgentPage; 