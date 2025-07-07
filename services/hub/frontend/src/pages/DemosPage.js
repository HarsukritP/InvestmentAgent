import React from 'react';
import { Link } from 'react-router-dom';
import './DemosPage.css';

const DemosPage = () => {
  return (
    <div className="demos-page">
      <div className="container">
        <div className="page-header">
          <h1>Book a Demo</h1>
          <p>Experience our AI agents in action with a personalized demonstration.</p>
        </div>

        <div className="demo-content">
          <div className="demo-form-section">
            <h2>Schedule Your Demo</h2>
            <form className="demo-form">
              <div className="form-group">
                <label>Full Name *</label>
                <input type="text" required />
              </div>
              <div className="form-group">
                <label>Email *</label>
                <input type="email" required />
              </div>
              <div className="form-group">
                <label>Company</label>
                <input type="text" />
              </div>
              <div className="form-group">
                <label>Role</label>
                <input type="text" />
              </div>
              <div className="form-group">
                <label>Interested Agent</label>
                <select>
                  <option>Portfolio Management Agent</option>
                  <option>Document Review Agent</option>
                  <option>Customer Support Agent</option>
                  <option>Sales Assistant Agent</option>
                  <option>Custom Solution</option>
                </select>
              </div>
              <div className="form-group">
                <label>Message</label>
                <textarea rows="4" placeholder="Tell us about your specific needs..."></textarea>
              </div>
              <button type="submit" className="btn-primary">
                Book Demo
              </button>
            </form>
          </div>

          <div className="demo-info-section">
            <h3>What to Expect</h3>
            <ul className="demo-features">
              <li>✓ 30-minute personalized demonstration</li>
              <li>✓ Live Q&A with our AI experts</li>
              <li>✓ Custom use case exploration</li>
              <li>✓ Integration discussion</li>
              <li>✓ Next steps planning</li>
            </ul>

            <div className="demo-cta">
              <h3>Ready to Explore?</h3>
              <p>Browse our available agents first</p>
              <Link to="/agents" className="btn-secondary">
                View Agents
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DemosPage; 