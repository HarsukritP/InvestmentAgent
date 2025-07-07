import React from 'react';
import { Link } from 'react-router-dom';
import './AgentInfoPage.css';

const PortfolioAgentPage = () => {
  const handleTryAgent = () => {
    window.open('https://portfolio-agent-frontend-production.up.railway.app', '_blank');
  };

  return (
    <div className="agent-info-page">
      <div className="container">
        {/* Breadcrumb */}
        <div className="breadcrumb">
          <Link to="/agents">All Agents</Link>
          <span>/</span>
          <span>Portfolio Management Agent</span>
        </div>

        {/* Agent Header */}
        <div className="agent-hero">
          <div className="agent-hero-content">
            <div className="agent-icon-large">📊</div>
            <div className="agent-info">
              <span className="agent-category">FINANCE</span>
              <h1>Portfolio Management Agent</h1>
              <p className="agent-tagline">
                AI-powered portfolio management with real-time market data and intelligent trading recommendations.
              </p>
              <div className="agent-actions">
                <button className="btn-primary large" onClick={handleTryAgent}>
                  Try Agent
                </button>
                <Link to="/demos" className="btn-secondary large">
                  Book Demo
                </Link>
              </div>
            </div>
          </div>
          <div className="agent-status">
            <span className="status-badge active">Live & Ready</span>
          </div>
        </div>

        {/* Overview Section */}
        <section className="overview-section">
          <h2>Overview</h2>
          <div className="overview-grid">
            <div className="overview-card">
              <h3>What it does</h3>
              <p>
                Our Portfolio Management Agent combines advanced AI algorithms with real-time market data 
                to provide intelligent investment recommendations, automated portfolio rebalancing, and 
                comprehensive risk assessment. It continuously monitors market conditions and adjusts 
                strategies to optimize portfolio performance.
              </p>
            </div>
            <div className="overview-card">
              <h3>How it works</h3>
              <p>
                The agent analyzes market trends, processes news sentiment, evaluates risk metrics, 
                and applies machine learning models to generate actionable insights. It integrates 
                seamlessly with trading platforms and provides real-time alerts and recommendations 
                based on your investment goals and risk tolerance.
              </p>
            </div>
            <div className="overview-card">
              <h3>Key Benefits</h3>
              <ul>
                <li>24/7 market monitoring and analysis</li>
                <li>Reduced emotional decision-making</li>
                <li>Automated risk management</li>
                <li>Data-driven investment strategies</li>
                <li>Real-time performance tracking</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Capabilities Section */}
        <section className="capabilities-section">
          <h2>Capabilities</h2>
          <div className="capabilities-grid">
            <div className="capability-card">
              <div className="capability-icon">📈</div>
              <h3>Real-time Market Analysis</h3>
              <p>Continuous monitoring of market conditions, price movements, and trading volumes across multiple exchanges.</p>
            </div>
            <div className="capability-card">
              <div className="capability-icon">⚖️</div>
              <h3>Risk Assessment & Management</h3>
              <p>Advanced risk modeling and automated risk management strategies to protect your investments.</p>
            </div>
            <div className="capability-card">
              <div className="capability-icon">🔄</div>
              <h3>Automated Portfolio Rebalancing</h3>
              <p>Intelligent rebalancing based on market conditions and your investment objectives.</p>
            </div>
            <div className="capability-card">
              <div className="capability-icon">📊</div>
              <h3>Performance Tracking & Reporting</h3>
              <p>Comprehensive analytics and detailed reports on portfolio performance and market insights.</p>
            </div>
          </div>
        </section>

        {/* Best For Section */}
        <section className="best-for-section">
          <h2>Best for</h2>
          <div className="best-for-grid">
            <div className="best-for-card">
              <h3>Financial Advisors</h3>
              <p>Enhance client services with AI-powered insights and automated portfolio management tools.</p>
              <ul>
                <li>Client portfolio optimization</li>
                <li>Risk assessment automation</li>
                <li>Performance reporting</li>
              </ul>
            </div>
            <div className="best-for-card">
              <h3>Investment Managers</h3>
              <p>Scale your investment operations with intelligent automation and real-time market analysis.</p>
              <ul>
                <li>Multi-portfolio management</li>
                <li>Market trend analysis</li>
                <li>Automated rebalancing</li>
              </ul>
            </div>
            <div className="best-for-card">
              <h3>Individual Investors</h3>
              <p>Make smarter investment decisions with professional-grade AI tools and insights.</p>
              <ul>
                <li>Personal portfolio tracking</li>
                <li>Investment recommendations</li>
                <li>Risk monitoring</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Integration Section */}
        <section className="integration-section">
          <h2>Integrations & Connectors</h2>
          <div className="integration-grid">
            <div className="integration-category">
              <h3>Market Data</h3>
              <div className="integration-tags">
                <span className="integration-tag">Alpha Vantage</span>
                <span className="integration-tag">Yahoo Finance</span>
                <span className="integration-tag">IEX Cloud</span>
                <span className="integration-tag">Polygon</span>
              </div>
            </div>
            <div className="integration-category">
              <h3>Trading Platforms</h3>
              <div className="integration-tags">
                <span className="integration-tag">Interactive Brokers</span>
                <span className="integration-tag">TD Ameritrade</span>
                <span className="integration-tag">Alpaca</span>
                <span className="integration-tag">E*TRADE</span>
              </div>
            </div>
            <div className="integration-category">
              <h3>Banking & Finance</h3>
              <div className="integration-tags">
                <span className="integration-tag">Plaid</span>
                <span className="integration-tag">Yodlee</span>
                <span className="integration-tag">Finicity</span>
                <span className="integration-tag">Open Banking APIs</span>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="cta-section">
          <div className="cta-content">
            <h2>Ready to Transform Your Investment Strategy?</h2>
            <p>Experience the power of AI-driven portfolio management and take your investments to the next level.</p>
            <div className="cta-actions">
              <button className="btn-primary large" onClick={handleTryAgent}>
                Try Portfolio Agent
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

export default PortfolioAgentPage; 