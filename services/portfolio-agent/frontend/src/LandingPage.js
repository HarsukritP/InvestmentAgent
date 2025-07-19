import React, { useState } from 'react';
import './LandingPage.css';
// Direct link to logo

const LandingPage = ({ onLogin }) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async () => {
    setIsLoading(true);
    try {
      // Import API_URL and AUTH_URL from config
      const { AUTH_URL } = await import('./config');
      
      console.log('🔒 Using AUTH_URL for login:', AUTH_URL);
      console.log('📍 Current location:', window.location.href);
      console.log('🔄 Starting OAuth login flow...');
      
      // Get OAuth URL from backend
      console.log('🔌 Fetching from:', `${AUTH_URL}/login`);
      const response = await fetch(`${AUTH_URL}/login`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
          'X-Debug-Info': 'portfolio-agent-login'
        },
        credentials: 'include'
      });
      
      console.log('📡 Response status:', response.status);
      console.log('📡 Response headers:', Object.fromEntries([...response.headers.entries()]));
      
      const data = await response.json();
      
      console.log('🔗 Received OAuth data:', data);
      console.log('🔗 Received OAuth URL:', data.oauth_url);
      
      if (data.oauth_url) {
        // Redirect to Google OAuth
        console.log('🔄 Redirecting to OAuth URL...');
        window.location.href = data.oauth_url;
      } else {
        console.error('❌ Failed to get OAuth URL:', data);
        setIsLoading(false);
      }
    } catch (error) {
      console.error('❌ Login error:', error);
      console.error('❌ Login error details:', {
        message: error.message,
        stack: error.stack,
        name: error.name
      });
      setIsLoading(false);
    }
  };

  return (
    <div className="landing-page">
      {/* Header */}
      <header className="landing-header">
        <div className="container">
          <div className="header-content">
            <div className="logo">
              <img src="https://procogia.com/wp-content/uploads/2024/03/procogia-horizontal-light-bg-1.png" alt="ProCogia" className="logo-image" />
            </div>
            <button 
              className="header-login-btn"
              onClick={handleLogin}
              disabled={isLoading}
            >
              {isLoading ? 'Connecting...' : 'Sign In'}
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="container">
          <div className="hero-content">
            <div className="hero-text">
              <h1 className="hero-title">
                AI-Powered Portfolio Intelligence
              </h1>
              <p className="hero-description">
                Transform your investment strategy with ProCogia's advanced AI assistant. 
                Get real-time market insights, intelligent portfolio analysis, and 
                personalized investment recommendations.
              </p>
              <div className="hero-stats">
                <div className="stat">
                  <span className="stat-number">Real-time</span>
                  <span className="stat-label">Market Data</span>
                </div>
                <div className="stat">
                  <span className="stat-number">AI-Driven</span>
                  <span className="stat-label">Insights</span>
                </div>
                <div className="stat">
                  <span className="stat-number">24/7</span>
                  <span className="stat-label">Portfolio Monitoring</span>
                </div>
              </div>
            </div>
            <div className="hero-visual">
              <div className="portfolio-preview">
                <div className="preview-header">
                  <div className="preview-title">Your Portfolio</div>
                  <div className="preview-value">$28,400</div>
                </div>
                <div className="preview-chart">
                  <div className="chart-bar" style={{height: '60%'}}></div>
                  <div className="chart-bar" style={{height: '80%'}}></div>
                  <div className="chart-bar" style={{height: '45%'}}></div>
                  <div className="chart-bar" style={{height: '70%'}}></div>
                  <div className="chart-bar" style={{height: '85%'}}></div>
                  <div className="chart-bar" style={{height: '55%'}}></div>
                </div>
                <div className="preview-stocks">
                  <div className="stock-item">
                    <span>AAPL</span>
                    <span className="positive">+2.4%</span>
                  </div>
                  <div className="stock-item">
                    <span>GOOGL</span>
                    <span className="positive">+1.8%</span>
                  </div>
                  <div className="stock-item">
                    <span>MSFT</span>
                    <span className="negative">-0.5%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="container">
          <h2 className="section-title">Powerful Features</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Real-time Analytics</h3>
              <p>Track your portfolio performance with live market data and comprehensive analytics dashboard.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h3>AI Assistant</h3>
              <p>Chat with our intelligent AI agent for personalized investment insights and market analysis.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📈</div>
              <h3>Performance Tracking</h3>
              <p>Monitor gains, losses, and portfolio allocation with detailed performance metrics.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔒</div>
              <h3>Secure & Private</h3>
              <p>Bank-level security with Google OAuth authentication and encrypted data protection.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📱</div>
              <h3>Responsive Design</h3>
              <p>Access your portfolio anywhere with our fully responsive web application.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Lightning Fast</h3>
              <p>Built with modern technology for instant loading and real-time updates.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-content">
            <h2>Ready to Transform Your Portfolio?</h2>
            <p>Join thousands of investors using AI to make smarter investment decisions.</p>
            <button 
              className="cta-button"
              onClick={handleLogin}
              disabled={isLoading}
            >
              <span className="google-icon">G</span>
              {isLoading ? 'Connecting...' : 'Get Started with Google'}
            </button>
            <p className="cta-note">
              Free to start • No credit card required • Secure with Google
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-left">
              <div className="footer-logo">
                <img src="https://procogia.com/wp-content/uploads/2024/03/procogia-horizontal-light-bg-1.png" alt="ProCogia" className="logo-image-small" />
              </div>
              <p>© 2024 ProCogia. All rights reserved.</p>
            </div>
            <div className="footer-right">
              <p>Powered by advanced AI and real-time market data</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage; 