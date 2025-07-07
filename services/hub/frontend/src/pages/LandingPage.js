import React from 'react';
import { Link } from 'react-router-dom';
import './LandingPage.css';

const LandingPage = () => {
  return (
    <div className="landing-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-container">
          <div className="hero-content">
            <h1 className="hero-title">
              Custom AI Solutions for
              <span className="hero-highlight"> Enterprise Integration</span>
            </h1>
            <p className="hero-subtitle">
              Experience the power of tailored AI solutions through our interactive demos.
              Built for your specific needs, integrated seamlessly with your systems.
            </p>
            <div className="hero-actions">
              <Link to="/agents" className="btn-primary large">
                View Agents
              </Link>
              <Link to="/contact" className="btn-secondary large">
                Contact Us
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Why Choose Section */}
      <section className="why-choose-section">
        <div className="container">
          <div className="section-header">
            <h2>Why Choose ProCogia AI</h2>
            <p>We deliver cutting-edge AI solutions that drive real business value</p>
          </div>
          
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">💡</div>
              <h3>Smart Solutions</h3>
              <p>Custom AI solutions tailored to your business needs and industry requirements.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔗</div>
              <h3>Seamless Integration</h3>
              <p>Effortlessly integrate AI capabilities into your existing systems and workflows.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Rapid Deployment</h3>
              <p>Quick implementation with immediate results and continuous optimization.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Industries Section */}
      <section className="industries-section">
        <div className="container">
          <div className="section-header">
            <h2>Industries We Serve</h2>
            <p>Our AI solutions are tailored for various industries</p>
          </div>
          
          <div className="industries-grid">
            <div className="industry-item">Healthcare</div>
            <div className="industry-item">Finance</div>
            <div className="industry-item">Manufacturing</div>
            <div className="industry-item">Retail</div>
            <div className="industry-item">Technology</div>
            <div className="industry-item">Energy</div>
            <div className="industry-item">Transportation</div>
            <div className="industry-item">Education</div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-content">
            <h2>Ready to Transform Your Business?</h2>
            <p>Explore our AI agents and see how they can revolutionize your operations.</p>
            <div className="cta-actions">
              <Link to="/agents" className="btn-primary large">
                View AI Agents
              </Link>
              <Link to="/demos" className="btn-secondary large">
                Book a Demo
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage; 