import React from 'react';
import { Link } from 'react-router-dom';
import './AgentInfoPage.css';

const DocumentReviewAgentPage = () => {
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
          <span>Document Review Agent</span>
        </div>

        {/* Agent Header */}
        <div className="agent-hero">
          <div className="agent-hero-content">
            <div className="agent-icon-large">📄</div>
            <div className="agent-info">
              <span className="agent-category">LEGAL</span>
              <h1>Document Review Agent</h1>
              <p className="agent-tagline">
                Streamline document reviews with automated feedback, context, and compliance alignment.
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
                Our Document Review Agent leverages advanced natural language processing to analyze contracts, 
                legal documents, and compliance materials. It identifies key clauses, potential risks, and 
                ensures alignment with regulatory requirements while significantly reducing review time.
              </p>
            </div>
            <div className="overview-card">
              <h3>How it works</h3>
              <p>
                The agent uses sophisticated AI models trained on legal documents to understand context, 
                extract important information, and flag potential issues. It integrates with document 
                management systems and provides detailed annotations and recommendations.
              </p>
            </div>
            <div className="overview-card">
              <h3>Key Benefits</h3>
              <ul>
                <li>Faster document review process</li>
                <li>Improved accuracy and consistency</li>
                <li>Risk identification and mitigation</li>
                <li>Compliance monitoring</li>
                <li>Cost reduction for legal teams</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Capabilities Section */}
        <section className="capabilities-section">
          <h2>Capabilities</h2>
          <div className="capabilities-grid">
            <div className="capability-card">
              <div className="capability-icon">🔍</div>
              <h3>Contract Analysis & Review</h3>
              <p>Comprehensive analysis of contract terms, conditions, and potential legal implications.</p>
            </div>
            <div className="capability-card">
              <div className="capability-icon">✅</div>
              <h3>Compliance Checking</h3>
              <p>Automated verification against regulatory requirements and company policies.</p>
            </div>
            <div className="capability-card">
              <div className="capability-icon">⚠️</div>
              <h3>Risk Identification</h3>
              <p>Proactive identification of potential legal risks and liability issues.</p>
            </div>
            <div className="capability-card">
              <div className="capability-icon">✏️</div>
              <h3>Automated Redlining</h3>
              <p>Intelligent redlining suggestions with explanations for proposed changes.</p>
            </div>
          </div>
        </section>

        {/* Best For Section */}
        <section className="best-for-section">
          <h2>Best for</h2>
          <div className="best-for-grid">
            <div className="best-for-card">
              <h3>Legal Teams</h3>
              <p>Streamline document review workflows and improve accuracy across legal operations.</p>
              <ul>
                <li>Contract review automation</li>
                <li>Legal research assistance</li>
                <li>Risk assessment</li>
              </ul>
            </div>
            <div className="best-for-card">
              <h3>Compliance Officers</h3>
              <p>Ensure regulatory compliance and maintain audit trails for all document reviews.</p>
              <ul>
                <li>Regulatory compliance checking</li>
                <li>Policy verification</li>
                <li>Audit trail maintenance</li>
              </ul>
            </div>
            <div className="best-for-card">
              <h3>Contract Managers</h3>
              <p>Accelerate contract lifecycle management with intelligent review capabilities.</p>
              <ul>
                <li>Contract lifecycle management</li>
                <li>Terms analysis</li>
                <li>Renewal management</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Integration Section */}
        <section className="integration-section">
          <h2>Integrations & Connectors</h2>
          <div className="integration-grid">
            <div className="integration-category">
              <h3>Document Management</h3>
              <div className="integration-tags">
                <span className="integration-tag">SharePoint</span>
                <span className="integration-tag">Box</span>
                <span className="integration-tag">Dropbox</span>
                <span className="integration-tag">Google Drive</span>
              </div>
            </div>
            <div className="integration-category">
              <h3>Legal Databases</h3>
              <div className="integration-tags">
                <span className="integration-tag">Westlaw</span>
                <span className="integration-tag">LexisNexis</span>
                <span className="integration-tag">Bloomberg Law</span>
                <span className="integration-tag">Thomson Reuters</span>
              </div>
            </div>
            <div className="integration-category">
              <h3>Workflow Systems</h3>
              <div className="integration-tags">
                <span className="integration-tag">DocuSign</span>
                <span className="integration-tag">ContractWorks</span>
                <span className="integration-tag">Ironclad</span>
                <span className="integration-tag">Agiloft</span>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="cta-section">
          <div className="cta-content">
            <h2>Ready to Revolutionize Document Review?</h2>
            <p>Be among the first to experience AI-powered document analysis and compliance checking.</p>
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

export default DocumentReviewAgentPage; 