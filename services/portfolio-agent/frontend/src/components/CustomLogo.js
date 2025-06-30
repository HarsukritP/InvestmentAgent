import React from 'react';
import './CustomLogo.css';
import procogiaIcon from '../assets/images/custom/procogia-icon-only.png';

const CustomLogo = ({ size = 'medium' }) => {
  return (
    <div className={`custom-logo ${size}`}>
      <div className="logo-container">
        <img src={procogiaIcon} alt="ProCogia Icon" className="logo-icon" />
        <div className="logo-text">PROCOGIA</div>
      </div>
    </div>
  );
};

export default CustomLogo; 