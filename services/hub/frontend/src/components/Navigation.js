import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navigation.css';

const Navigation = () => {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navigation">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          <div className="logo-placeholder">P</div>
          <span className="logo-text">PROCOGIA</span>
        </Link>
        
        <div className="nav-links">
          <Link 
            to="/" 
            className={`nav-link ${isActive('/') ? 'active' : ''}`}
          >
            Home
          </Link>
          <Link 
            to="/agents" 
            className={`nav-link ${isActive('/agents') || isActive('/hub') ? 'active' : ''}`}
          >
            Agents
          </Link>
          <Link 
            to="/demos" 
            className={`nav-link ${isActive('/demos') ? 'active' : ''}`}
          >
            Demos
          </Link>
          <Link 
            to="/faqs" 
            className={`nav-link ${isActive('/faqs') ? 'active' : ''}`}
          >
            FAQs
          </Link>
          <Link 
            to="/contact" 
            className={`nav-link ${isActive('/contact') ? 'active' : ''}`}
          >
            Contact
          </Link>
        </div>
        
        <div className="nav-actions">
          <Link to="/contact" className="btn-secondary">
            Sign in
          </Link>
          <Link to="/demos" className="btn-primary">
            Get a demo
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navigation; 