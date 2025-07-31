import React from 'react';
import './GlobalLoadingIndicator.css';

const GlobalLoadingIndicator = ({ isVisible, message = "Updating..." }) => {
  if (!isVisible) return null;

  return (
    <div className="global-loading-indicator">
      <div className="loading-content">
        <div className="mini-spinner"></div>
        <span className="loading-message">{message}</span>
      </div>
    </div>
  );
};

export default GlobalLoadingIndicator;