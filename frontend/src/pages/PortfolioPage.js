import React, { useState, useEffect } from 'react';

import './PortfolioPage.css';

const PortfolioPage = ({ 
  portfolio, 
  healthStatus, 
  isRefreshing, 
  onRefresh, 
  onBuyStock, 
  onAdjustHolding 
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
    
    if (!configuration.twelvedata_key_configured && !configuration.gemini_key_configured && !configuration.oauth_configured) {
      return { text: 'Demo Mode (No API Keys)', class: 'warning' };
    }
    
    if (!configuration.twelvedata_key_configured) {
      return { text: 'Using Mock Market Data', class: 'warning' };
    }
    
    if (!configuration.gemini_key_configured) {
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
      {/* Page Header */}
      <h1 className="page-title">Portfolio</h1>
      
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
        !healthStatus.configuration.gemini_key_configured
      ) && (
        <div className="config-notice">
          <div className="notice-content">
            <span className="notice-icon">⚠️</span>
            <div className="notice-text">
              <strong>Configuration Notice:</strong>
              {!healthStatus.configuration.twelvedata_key_configured && (
                <span> Market data is using mock values. </span>
              )}
              {!healthStatus.configuration.gemini_key_configured && (
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
            <span className="summary-percent">
              {formatPercent(totalPnlPercent)}
            </span>
          </div>
        </div>
      </div>

      {/* Holdings Table */}
      <div className="holdings-section">
        <div className="section-header">
          <h2 className="section-title">Holdings</h2>
          <p className="section-subtitle">
            {holdings.length} position{holdings.length !== 1 ? 's' : ''}
          </p>
        </div>

        {holdings.length === 0 ? (
          <div className="empty-holdings">
            <div className="empty-icon">📊</div>
            <h3>No holdings yet</h3>
            <p>Start building your portfolio by buying your first stock.</p>
            <button className="buy-first-stock-btn" onClick={onBuyStock}>
              Buy Your First Stock
            </button>
          </div>
        ) : (
          <div className="holdings-table">
            <div className="table-header">
              <div className="table-cell symbol">Symbol</div>
              <div className="table-cell shares">Shares</div>
              <div className="table-cell avg-cost">Purchase Price</div>
              <div className="table-cell current-price">Current Price</div>
              <div className="table-cell market-value">Market Value</div>
              <div className="table-cell pnl">P&L</div>
              <div className="table-cell actions">Actions</div>
            </div>
            
            {holdings.map((holding, index) => {
              const shares = holding.shares || holding.quantity || 0;
              const avgCost = holding.average_cost || holding.purchase_price || 0;
              const currentPrice = holding.current_price || avgCost;
              const marketValue = shares * currentPrice;
              const costBasis = shares * avgCost;
              const pnl = marketValue - costBasis;
              const pnlPercent = costBasis > 0 ? (pnl / costBasis) * 100 : 0;

              return (
                <div key={index} className="table-row">
                  <div className="table-cell symbol">
                    <div className="symbol-info">
                      <span className="symbol-text">{holding.symbol}</span>
                    </div>
                  </div>
                  <div className="table-cell shares">
                    {shares.toLocaleString()}
                  </div>
                  <div className="table-cell avg-cost">
                    {formatCurrency(avgCost)}
                  </div>
                  <div className="table-cell current-price">
                    {formatCurrency(currentPrice)}
                  </div>
                  <div className="table-cell market-value">
                    {formatCurrency(marketValue)}
                  </div>
                  <div className="table-cell pnl">
                    <div className={`pnl-value ${getPerformanceClass(pnl)}`}>
                      {formatCurrency(pnl)}
                      <span className="pnl-percent">
                        {formatPercent(pnlPercent)}
                      </span>
                    </div>
                  </div>
                  <div className="table-cell actions">
                    <button 
                      className="adjust-btn"
                      onClick={() => onAdjustHolding(holding)}
                    >
                      Adjust
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default PortfolioPage; 