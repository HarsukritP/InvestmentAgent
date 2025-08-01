import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';

import './App.css';
import { API_URL } from './config';

// Import page components
import LandingPage from './LandingPage';
import AuthSuccess from './AuthSuccess';
import DashboardPage from './pages/DashboardPage';
import PortfolioPage from './pages/PortfolioPage';
import ChatPage from './pages/ChatPage';
import ActionsLogPage from './pages/ActionsLogPage';
import StockDetailPage from './pages/StockDetailPage';
import Navigation from './components/Navigation';
import BuyStock from './BuyStock';

// Configure axios with base URL
console.log('Configuring axios with API_URL:', API_URL);
axios.defaults.baseURL = API_URL;
axios.defaults.withCredentials = true; // Enable sending cookies with cross-origin requests

// Add request interceptor for debugging
axios.interceptors.request.use(
  config => {
    console.log(`🚀 Request: ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  error => {
    console.error('❌ Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging
axios.interceptors.response.use(
  response => {
    console.log(`✅ Response: ${response.status} from ${response.config.url}`);
    return response;
  },
  error => {
    if (error.response) {
      console.error(`❌ Response error: ${error.response.status} from ${error.config?.url}`, error.response.data);
    } else {
      console.error('❌ Response error:', error.message);
    }
    return Promise.reject(error);
  }
);

function App() {
  const [user, setUser] = useState(null);
  const [portfolio, setPortfolio] = useState(null);

  const [isLoading, setIsLoading] = useState(true);
  const [showBuyStock, setShowBuyStock] = useState(false);
  const [selectedHolding, setSelectedHolding] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  // For debugging
  useEffect(() => {
    console.log('App initialized with:');
    console.log('- API_URL:', API_URL);
    console.log('- Axios baseURL:', axios.defaults.baseURL);
    console.log('- withCredentials:', axios.defaults.withCredentials);
  }, []);

  // Check screen size on mount and resize
  useEffect(() => {
    const checkIsMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    // Initial check
    checkIsMobile();
    
    // Add resize listener
    window.addEventListener('resize', checkIsMobile);
    
    // Clean up
    return () => window.removeEventListener('resize', checkIsMobile);
  }, []);

  // Collapse sidebar by default on mobile
  useEffect(() => {
    if (isMobile) {
      setSidebarCollapsed(true);
    }
  }, [isMobile]);

  // Check for existing authentication on app load
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('auth_token');
      
      if (token) {
        try {
          console.log('Found token in localStorage, verifying...');
          // Set authorization header
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // Verify token with backend
          const response = await axios.get('/auth/me');
          
          if (response.data.user) {
            console.log('Token verified, user authenticated:', response.data.user);
            setUser(response.data.user);
            setIsAuthenticated(true);
          }
        } catch (error) {
          console.error('Token verification failed:', error);
          // Clear invalid token
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_header');
          delete axios.defaults.headers.common['Authorization'];
        }
      } else {
        console.log('No authentication token found');
      }
      
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  // Fetch health status when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      fetchHealthStatus();
      fetchPortfolio();
    }
  }, [isAuthenticated]);

  const fetchHealthStatus = async () => {
    try {
      console.log('Fetching health status...');
      const response = await axios.get('/health');
      console.log('Health status received:', response.data);
    } catch (error) {
      console.error('Failed to fetch health status:', error);
    }
  };

  const fetchPortfolio = async () => {
    try {
      console.log('🔄 Fetching portfolio data...');
      const response = await axios.get('/portfolio');
      console.log('Portfolio API response:', response);
      
      // Create a new object with timestamp to ensure React detects the change
      const portfolioWithTimestamp = {
        ...response.data,
        _lastUpdated: Date.now()
      };
      setPortfolio(portfolioWithTimestamp);
      console.log('✅ Portfolio data updated:', portfolioWithTimestamp);
    } catch (error) {
      console.error('Failed to fetch portfolio:', error);
    }
  };

  const handleAuthenticated = (token) => {
    console.log('User authenticated with token');
    // Set axios authorization header
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    
    // Verify and get user info
    axios.get('/auth/me')
      .then(response => {
        console.log('User info retrieved:', response.data);
        setUser(response.data.user);
        setIsAuthenticated(true);
      })
      .catch(error => {
        console.error('Failed to get user info:', error);
        handleLogout();
      });
  };

  const handleLogout = () => {
    console.log('Logging out user');
    // Clear local storage
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_header');
    
    // Clear axios header
    delete axios.defaults.headers.common['Authorization'];
    
    // Reset state
    setUser(null);
    setIsAuthenticated(false);
    setPortfolio(null);
    
    // Call logout endpoint
    axios.post('/auth/logout').catch(console.error);
  };

  const handleBuySuccess = async (buyResult) => {
    console.log('🎉 Buy operation successful:', buyResult);
    
    // Add a small delay to ensure backend has fully processed the transaction
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Refresh portfolio after successful purchase
    console.log('🔄 Refreshing portfolio after buy success...');
    await fetchPortfolio();
  };



  const toggleMobileNav = () => {
    setMobileNavOpen(!mobileNavOpen);
  };

  if (isLoading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner"></div>
        <p>Loading Portfolio Agent...</p>
      </div>
    );
  }

  // Element for protected routes with navigation
  const ProtectedLayout = ({ children }) => (
    <div className={`app-layout ${sidebarCollapsed ? 'sidebar-collapsed' : ''} ${isMobile ? 'mobile' : ''} ${mobileNavOpen ? 'mobile-nav-open' : ''}`}>
      <Navigation 
        user={user} 
        onLogout={handleLogout}
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={setSidebarCollapsed}
        isMobile={isMobile}
        mobileNavOpen={mobileNavOpen}
        toggleMobileNav={toggleMobileNav}
      />
      <main className="main-content">
        {children}
      </main>
    </div>
  );

  return (
    <Router>
      <div className={`App ${isMobile ? 'mobile' : ''}`}>
        <Routes>
          {/* Public routes */}
          <Route 
            path="/" 
            element={
              !isAuthenticated ? (
                <LandingPage onAuthenticated={handleAuthenticated} />
              ) : (
                <Navigate to="/dashboard" replace />
              )
            } 
          />
          <Route 
            path="/auth/success" 
            element={<AuthSuccess onAuthenticated={handleAuthenticated} />} 
          />
          
          {/* Protected routes */}
          <Route 
            path="/dashboard" 
            element={
              isAuthenticated ? (
                <ProtectedLayout>
                  <DashboardPage />
                </ProtectedLayout>
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          <Route 
            path="/portfolio" 
            element={
              isAuthenticated ? (
                <ProtectedLayout>
                  <PortfolioPage 
                    onTransactionSuccess={handleBuySuccess}
                  />
                </ProtectedLayout>
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          <Route 
            path="/chat" 
            element={
              isAuthenticated ? (
                <ProtectedLayout>
                  <ChatPage 
                    portfolio={portfolio} 
                    user={user} 
                    isMobile={isMobile} 
                    toggleMobileNav={toggleMobileNav} 
                  />
                </ProtectedLayout>
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          <Route 
            path="/actions-log" 
            element={
              isAuthenticated ? (
                <ProtectedLayout>
                  <ActionsLogPage 
                    isMobile={isMobile} 
                    toggleMobileNav={toggleMobileNav} 
                  />
                </ProtectedLayout>
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          <Route 
            path="/stock/:symbol" 
            element={
              isAuthenticated ? (
                <ProtectedLayout>
                  <StockDetailPage />
                </ProtectedLayout>
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          <Route path="*" element={<Navigate to={isAuthenticated ? "/dashboard" : "/"} replace />} />
        </Routes>

        {/* Global Modals */}
        {showBuyStock && (
          <BuyStock
            isOpen={showBuyStock}
            onClose={() => {
              setShowBuyStock(false);
              setSelectedHolding(null);
            }}
            onSuccess={handleBuySuccess}
            isMobile={isMobile}
            existingHolding={selectedHolding}
          />
        )}
      </div>
    </Router>
  );
}

export default App; 