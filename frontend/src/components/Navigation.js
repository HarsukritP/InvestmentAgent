import React from 'react';
import { NavLink } from 'react-router-dom';
import { MdDashboard, MdSmartToy, MdLogout, MdHistory, MdMenu, MdClose, MdHome } from 'react-icons/md';
import { IoChevronBack } from 'react-icons/io5';
import './Navigation.css';
// Direct link to logo
import procogiaIcon from '../assets/images/procogia-icon.png';

const Navigation = ({ 
  user, 
  onLogout, 
  isCollapsed, 
  onToggleCollapse,
  isMobile,
  mobileNavOpen,
  toggleMobileNav
}) => {

  const navItems = [
    {
      path: '/dashboard',
      label: 'Dashboard',
      description: 'Overview and quick access',
      shortLabel: 'Dashboard',
      icon: MdHome
    },
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

  // For mobile, we'll use a different navigation style
  if (isMobile) {
    return (
      <>
        {/* Mobile Menu Button */}
        <button 
          className="mobile-menu-button"
          onClick={toggleMobileNav}
          aria-label={mobileNavOpen ? "Close menu" : "Open menu"}
        >
          {mobileNavOpen ? <MdClose /> : <MdMenu />}
        </button>
        
        {/* Mobile Navigation Overlay */}
        <div className={`mobile-nav-overlay ${mobileNavOpen ? 'open' : ''}`} onClick={toggleMobileNav}></div>
        
        {/* Mobile Navigation Drawer */}
        <nav className={`mobile-navigation ${mobileNavOpen ? 'open' : ''}`}>
          <div className="mobile-nav-header">
            <div className="mobile-nav-brand">
              <img 
                src="https://procogia.com/wp-content/uploads/2024/03/procogia-horizontal-light-bg-1.png" 
                alt="ProCogia" 
                className="mobile-brand-logo" 
              />
            </div>
            <button 
              className="mobile-close-button"
              onClick={toggleMobileNav}
              aria-label="Close menu"
            >
              <MdClose />
            </button>
          </div>
          
          <div className="mobile-nav-menu">
            {navItems.map((item) => {
              const IconComponent = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) => 
                    `mobile-nav-item ${isActive ? 'mobile-nav-item-active' : ''}`
                  }
                  onClick={toggleMobileNav}
                >
                  <IconComponent className="mobile-nav-item-icon" />
                  <div className="mobile-nav-item-text">
                    <div className="mobile-nav-item-label">{item.label}</div>
                    <div className="mobile-nav-item-description">{item.description}</div>
                  </div>
                </NavLink>
              );
            })}
          </div>
          
          <div className="mobile-nav-footer">
            <div className="mobile-user-profile">
              {user?.picture && (
                <img 
                  src={user.picture} 
                  alt={user.name} 
                  className="mobile-user-avatar"
                />
              )}
              <div className="mobile-user-info">
                <div className="mobile-user-name">{user?.name}</div>
                <div className="mobile-user-email">{user?.email}</div>
              </div>
            </div>
            
            <button className="mobile-logout-button" onClick={onLogout}>
              <MdLogout className="mobile-logout-icon" />
              Sign Out
            </button>
          </div>
        </nav>
      </>
    );
  }

  // Desktop navigation
  return (
    <nav className={`navigation ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="nav-header">
        <div className="nav-brand">
          {!isCollapsed ? (
            <div className="brand-title">
              <img src="https://procogia.com/wp-content/uploads/2024/03/procogia-horizontal-light-bg-1.png" alt="ProCogia" className="brand-logo" />
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