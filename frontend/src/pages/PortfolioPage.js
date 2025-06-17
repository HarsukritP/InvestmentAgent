import React, { useState, useEffect } from 'react';
import { MdMenu } from 'react-icons/md';
import './PortfolioPage.css';

const PortfolioPage = ({ 
  portfolio, 
  healthStatus, 
  isRefreshing, 
  onRefresh, 
  onBuyStock, 
  onAdjustHolding,
  isMobile,
  toggleMobileNav
}) => {
  const [loading] = useState(false);
  const [error] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    if (portfolio) {
      setLastUpdated(new Date().toLocaleTimeString());
    }
  }, [portfolio]);

  const formatCurrency = (amount) => {
    if (amount === undefined || amount === null || isNaN(amount)) {
      return '$0.00';
    }
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatPercent = (percent) => {
    if (percent === undefined || percent === null || isNaN(percent)) {
      return '0.00%';
    }
    const formatted = percent.toFixed(2);
    return percent >= 0 ? `+${formatted}%` : `${formatted}%`;
  };

  const getPerformanceClass = (value) => {
    if (value === undefined || value === null || isNaN(value)) {
      return 'neutral';
    }
    return value >= 0 ? 'positive' : 'negative';
  };

  const getStatusDisplay = () => {
    if (!healthStatus) return { text: 'Loading...', class: 'loading' };
    
    const { configuration } = healthStatus;
    
    if (!configuration) return { text: 'Loading...', class: 'loading' };
    
    if (!configuration.twelvedata_key_configured && !configuration.openai_key_configured && !configuration.oauth_configured) {
      return { text: 'Demo Mode (No API Keys)', class: 'warning' };
    }
    
    if (!configuration.twelvedata_key_configured) {
      return { text: 'Using Mock Market Data', class: 'warning' };
    }
    
    if (!configuration.openai_key_configured) {
      return { text: 'AI Assistant Unavailable', class: 'warning' };
    }
    
    if (healthStatus.status === 'healthy') {
      return { text: 'All Systems Operational', class: 'success' };
    }
    
    return { text: 'Some Services Degraded', class: 'warning' };
  };

  if (loading) {
    return (
      <div className="portfolio-page">
        <div className="portfolio-loading">
          <div className="loading-spinner"></div>
          <p>Loading your portfolio...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="portfolio-page">
        <div className="portfolio-error">
          <h2>Unable to load portfolio</h2>
          <p>{error}</p>
          <button onClick={onRefresh} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!portfolio || !portfolio.portfolio) {
    return (
      <div className="portfolio-page">
        <div className="portfolio-empty">
          <h2>No portfolio data available</h2>
          <p>Your portfolio information will appear here once loaded.</p>
          <button onClick={onRefresh} className="refresh-button">
            Refresh Portfolio
          </button>
        </div>
      </div>
    );
  }

  // Extract portfolio data
  const portfolioData = portfolio.portfolio;
  const holdings = portfolio.holdings || [];
  
  // Calculate summary values
  const portfolioValue = portfolioData.total_market_value || 0;
  const cashBalance = portfolioData.cash_balance || 0;
  const totalAccountValue = portfolioValue + cashBalance;
  
  // Calculate total P&L
  const totalCost = holdings.reduce((sum, holding) => {
    return sum + (holding.shares || holding.quantity || 0) * (holding.average_cost || holding.purchase_price || 0);
  }, 0);
  const totalPnl = portfolioValue - totalCost;
  const totalPnlPercent = totalCost > 0 ? (totalPnl / totalCost) * 100 : 0;

  const statusDisplay = getStatusDisplay();

  return (
    <div className="portfolio-page">
      {/* Mobile Header */}
      {isMobile && (
        <div className="mobile-header">
          <button 
            className="mobile-menu-toggle" 
            onClick={toggleMobileNav}
            aria-label="Open menu"
          >
            <MdMenu />
          </button>
          <h1 className="mobile-title">Portfolio</h1>
        </div>
      )}
      
      {/* Page Header */}
      {!isMobile && <h1 className="page-title">Portfolio</h1>}
      
      <div className="header-actions">
        <div className={`status-badge ${statusDisplay.class}`}>
          <div className="status-dot"></div>
          <span>{statusDisplay.text}</span>
        </div>
        <button 
          className="buy-stock-btn"
          onClick={onBuyStock}
        >
          <span className="btn-icon">💰</span>
          Buy Stock
        </button>
        <button 
          className="refresh-btn"
          onClick={onRefresh}
          disabled={isRefreshing}
        >
          <span className={`btn-icon ${isRefreshing ? 'spinning' : ''}`}>🔄</span>
          {isRefreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
      
      {lastUpdated && (
        <p className="last-updated">Updated {lastUpdated}</p>
      )}

      {/* Configuration Notice */}
      {healthStatus && healthStatus.configuration && (
        !healthStatus.configuration.twelvedata_key_configured || 
        !healthStatus.configuration.openai_key_configured
      ) && (
        <div className="config-notice">
          <div className="notice-content">
            <span className="notice-icon">⚠️</span>
            <div className="notice-text">
              <strong>Configuration Notice:</strong>
              {!healthStatus.configuration.twelvedata_key_configured && (
                <span> Market data is using mock values. </span>
              )}
              {!healthStatus.configuration.openai_key_configured && (
                <span> AI assistant features are unavailable. </span>
              )}
              Configure API keys for full functionality.
            </div>
          </div>
        </div>
      )}

      {/* Portfolio Summary Cards */}
      <div className="portfolio-summary">
        <div className="summary-card">
          <div className="summary-label">Total Portfolio Value</div>
          <div className="summary-value primary">
            {formatCurrency(portfolioValue)}
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-label">Cash Balance</div>
          <div className="summary-value">
            {formatCurrency(cashBalance)}
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-label">Total Account Value</div>
          <div className="summary-value">
            {formatCurrency(totalAccountValue)}
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-label">Total Return</div>
          <div className={`summary-value ${getPerformanceClass(totalPnl)}`}>
            {formatCurrency(totalPnl)}
            <div className={`summary-percent ${getPerformanceClass(totalPnlPercent)}`}>
              {formatPercent(totalPnlPercent)}
            </div>
          </div>
        </div>
      </div>

      {/* Holdings Section */}
      <div className="holdings-section">
        <div className="section-header">
          <h2 className="section-title">Current Holdings</h2>
          <div className="section-subtitle">
            {holdings.length} {holdings.length === 1 ? 'position' : 'positions'}
          </div>
        </div>

        {holdings.length === 0 ? (
          <div className="empty-holdings">
            <div className="empty-icon">📈</div>
            <h3>No holdings yet</h3>
            <p>Start building your portfolio by buying your first stock.</p>
            <button className="buy-first-stock-btn" onClick={onBuyStock}>
              Buy Your First Stock
            </button>
          </div>
        ) : (
          <div className="holdings-table-wrapper">
            <table className="holdings-table">
              <thead>
                <tr className="table-header">
                  <th>Symbol</th>
                  <th>Shares</th>
                  <th>Avg. Cost</th>
                  <th>Current Price</th>
                  <th>Market Value</th>
                  <th>Profit/Loss</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {holdings.map((holding, index) => {
                  const shares = holding.shares || holding.quantity || 0;
                  const avgCost = holding.average_cost || holding.purchase_price || 0;
                  const currentPrice = holding.current_price || 0;
                  const marketValue = shares * currentPrice;
                  const costBasis = shares * avgCost;
                  const pnl = marketValue - costBasis;
                  const pnlPercent = costBasis > 0 ? (pnl / costBasis) * 100 : 0;
                  
                  return (
                    <tr key={index} className="table-row">
                      <td className="table-cell">
                        <div className="symbol-info">
                          <div className="symbol-text">
                            <strong>{holding.symbol}</strong>
                          </div>
                        </div>
                      </td>
                      <td className="table-cell">{shares.toFixed(2)}</td>
                      <td className="table-cell">{formatCurrency(avgCost)}</td>
                      <td className="table-cell">{formatCurrency(currentPrice)}</td>
                      <td className="table-cell">{formatCurrency(marketValue)}</td>
                      <td className="table-cell">
                        <div className={`pnl-value ${getPerformanceClass(pnl)}`}>
                          {formatCurrency(pnl)}
                          <div className={`pnl-percent ${getPerformanceClass(pnlPercent)}`}>
                            {formatPercent(pnlPercent)}
                          </div>
                        </div>
                      </td>
                      <td className="table-cell">
                        <button 
                          className="adjust-btn"
                          onClick={() => onAdjustHolding(holding)}
                        >
                          Adjust
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default PortfolioPage; 