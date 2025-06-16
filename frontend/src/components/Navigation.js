import React from 'react';
import { NavLink } from 'react-router-dom';
import { MdDashboard, MdSmartToy, MdLogout, MdHistory } from 'react-icons/md';
import { IoChevronBack } from 'react-icons/io5';
import './Navigation.css';
import procogiaLogo from '../assets/images/custom/procogia-logo-white.png';
import procogiaIcon from '../assets/images/procogia-icon.png';

const Navigation = ({ user, onLogout, isCollapsed, onToggleCollapse }) => {

  const navItems = [
    {
      path: '/portfolio',
      label: 'Portfolio',
      description: 'View your investments',
      shortLabel: 'Portfolio',
      icon: MdDashboard
    },
    {
      path: '/chat',
      label: 'AI Assistant',
      description: 'Get investment insights',
      shortLabel: 'AI Chat',
      icon: MdSmartToy
    },
    {
      path: '/actions-log',
      label: 'Actions Log',
      description: 'View transaction history',
      shortLabel: 'Actions',
      icon: MdHistory
    }
  ];

  const toggleSidebar = () => {
    if (onToggleCollapse) {
      onToggleCollapse(!isCollapsed);
    }
  };

  return (
    <nav className={`navigation ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="nav-header">
        <div className="nav-brand">
          {!isCollapsed ? (
            <div className="brand-title">
              <img src={procogiaLogo} alt="ProCogia" className="brand-logo" />
            </div>
          ) : (
            <div className="brand-title-collapsed">
              <img src={procogiaIcon} alt="ProCogia" className="brand-icon" />
            </div>
          )}
        </div>
        <button 
          className="collapse-toggle"
          onClick={toggleSidebar}
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <IoChevronBack className={`toggle-icon ${isCollapsed ? 'collapsed' : ''}`} />
        </button>
      </div>

      <div className="nav-menu">
        {navItems.map((item) => {
          const IconComponent = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => 
                `nav-item ${isActive ? 'nav-item-active' : ''}`
              }
              title={isCollapsed ? item.label : ''}
            >
              <div className="nav-item-content">
                <div className="nav-item-main">
                  <IconComponent className="nav-item-icon" />
                  <div className="nav-item-text">
                    <div className="nav-item-label">
                      {isCollapsed ? item.shortLabel : item.label}
                    </div>
                    {!isCollapsed && (
                      <div className="nav-item-description">{item.description}</div>
                    )}
                  </div>
                </div>
              </div>
            </NavLink>
          );
        })}
      </div>

      <div className="nav-footer">
        {!isCollapsed ? (
          <>
            <div className="user-profile">
              {user?.picture && (
                <img 
                  src={user.picture} 
                  alt={user.name} 
                  className="user-avatar"
                />
              )}
              <div className="user-info">
                <div className="user-name">{user?.name}</div>
                <div className="user-email">{user?.email}</div>
              </div>
            </div>
            
            <button className="logout-button" onClick={onLogout}>
              <MdLogout className="logout-icon" />
              Sign Out
            </button>
          </>
        ) : (
          <div className="nav-footer-collapsed">
            <div className="user-profile-collapsed" title={user?.name}>
              {user?.picture && (
                <img 
                  src={user.picture} 
                  alt={user.name} 
                  className="user-avatar-small"
                />
              )}
            </div>
            <button 
              className="logout-button-collapsed" 
              onClick={onLogout}
              title="Sign Out"
            >
              <MdLogout />
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navigation; 