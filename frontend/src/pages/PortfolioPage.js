import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { isMarketOpen } from '../utils/formatters';
import BuyStock from '../BuyStock';
import HoverChart from '../components/HoverChart';
import GlobalLoadingIndicator from '../components/GlobalLoadingIndicator';
import './PortfolioPage.css';

const PortfolioPage = ({ onTransactionSuccess }) => {
  const navigate = useNavigate();
  
  // Load cached portfolio data immediately if available
  const getCachedPortfolio = () => {
    try {
      const cached = localStorage.getItem('portfolio_data');
      return cached ? JSON.parse(cached) : null;
    } catch (error) {
      console.warn('Failed to load cached portfolio data:', error);
      return null;
    }
  };
  
  const [portfolio, setPortfolio] = useState(getCachedPortfolio());
  const [hasLoadedBefore, setHasLoadedBefore] = useState(!!getCachedPortfolio());
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState(null);
  const [showBuyModal, setShowBuyModal] = useState(false);
  const [selectedHolding, setSelectedHolding] = useState(null);
  const [marketStatus, setMarketStatus] = useState({
    isOpen: false,
    nextUpdateMinutes: 5,
    nextUpdateSeconds: 0
  });

  // Hover chart state
  const [hoverChart, setHoverChart] = useState({
    visible: false,
    symbol: null,
    position: { x: 0, y: 0 }
  });
  const hoverTimeoutRef = useRef(null);

  const refreshIntervalRef = useRef(null);
  const countdownIntervalRef = useRef(null);
  const nextUpdateTimeRef = useRef(null);

  // Get market update interval based on market status
  const getUpdateInterval = useCallback((isMarketOpen) => {
    // 3 minutes when market is open, 20 minutes when closed
    return isMarketOpen ? 3 * 60 * 1000 : 20 * 60 * 1000;
  }, []);

  // Update countdown timer
  const updateCountdown = useCallback(() => {
    if (!nextUpdateTimeRef.current) return;
    
    const now = Date.now();
    const timeUntilUpdate = nextUpdateTimeRef.current - now;
    
    if (timeUntilUpdate <= 0) {
      setMarketStatus(prev => ({ ...prev, nextUpdateMinutes: 0, nextUpdateSeconds: 0 }));
      return;
    }
    
    const totalSeconds = Math.ceil(timeUntilUpdate / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    
    setMarketStatus(prev => ({ 
      ...prev, 
      nextUpdateMinutes: minutes,
      nextUpdateSeconds: seconds
    }));
  }, []);

  // Fetch health status
  const fetchHealthStatus = useCallback(async () => {
    try {
      const response = await axios.get('/health');
      return response.data;
    } catch (error) {
      console.error('Error fetching health status:', error);
      return null;
    }
  }, []);

  const fetchPortfolio = useCallback(async () => {
    // Always use corner loading indicator for all scenarios
    setIsUpdating(true);
    setError(null);
    
    try {
      console.log('Fetching portfolio data...');
      
      // Fetch both portfolio and health status
      const [portfolioResponse, healthData] = await Promise.all([
        axios.get('/portfolio'),
        fetchHealthStatus()
      ]);
      
      console.log('Portfolio data received:', portfolioResponse.data);
      
      // Extract portfolio data from response structure
      const portfolioData = portfolioResponse.data.portfolio || {};
      const holdingsData = portfolioResponse.data.holdings || [];
      
      // Calculate total value and holdings value
      const cashBalance = portfolioData.cash_balance || 0;
      const holdingsValue = holdingsData.reduce((total, holding) => total + (holding.market_value || 0), 0);
      const totalValue = cashBalance + holdingsValue;
      
      const newPortfolioData = {
        cash_balance: cashBalance,
        holdings: holdingsData,
        total_value: totalValue,
        holdings_value: holdingsValue
      };
      
      setPortfolio(newPortfolioData);
      
      // Cache the portfolio data for persistence
      try {
        localStorage.setItem('portfolio_data', JSON.stringify(newPortfolioData));
      } catch (error) {
        console.warn('Failed to cache portfolio data:', error);
      }
      
      // Mark that we've successfully loaded data at least once
      setHasLoadedBefore(true);
      
      // Determine market status - prefer health status data, fallback to local check
      let currentMarketOpen;
      if (healthData && healthData.services && healthData.services.market_data && healthData.services.market_data.auto_refresh) {
        currentMarketOpen = healthData.services.market_data.auto_refresh.market_status === 'open';
      } else {
        currentMarketOpen = isMarketOpen();
      }
      
      setMarketStatus(prev => ({
        ...prev,
        isOpen: currentMarketOpen
      }));
      
      return currentMarketOpen;
      
    } catch (error) {
      console.error('Error fetching portfolio:', error);
      setError('Failed to load portfolio data. Please try again.');
      
      // Fallback market status
      const fallbackMarketOpen = isMarketOpen();
      setMarketStatus(prev => ({ ...prev, isOpen: fallbackMarketOpen }));
      return fallbackMarketOpen;
    } finally {
      setIsUpdating(false);
    }
  }, [fetchHealthStatus]);

  // Schedule next update
  const scheduleNextUpdate = useCallback((currentMarketOpen) => {
    const interval = getUpdateInterval(currentMarketOpen);
    nextUpdateTimeRef.current = Date.now() + interval;
    
    // Clear existing intervals
    if (refreshIntervalRef.current) {
      clearTimeout(refreshIntervalRef.current);
    }
    if (countdownIntervalRef.current) {
      clearInterval(countdownIntervalRef.current);
    }
    
    // Set up new refresh interval
    refreshIntervalRef.current = setTimeout(async () => {
      const marketOpen = await fetchPortfolio();
      scheduleNextUpdate(marketOpen);
    }, interval);
    
    // Set up countdown timer (updates every second)
    countdownIntervalRef.current = setInterval(updateCountdown, 1000);
    
    // Initial countdown update
    updateCountdown();
  }, [getUpdateInterval, updateCountdown, fetchPortfolio]);

  useEffect(() => {
    const initializePortfolio = async () => {
      const marketOpen = await fetchPortfolio(); // Initial load
      scheduleNextUpdate(marketOpen);
    };
    
    initializePortfolio();
    
    // Cleanup intervals on unmount
    return () => {
      if (refreshIntervalRef.current) {
        clearTimeout(refreshIntervalRef.current);
      }
      if (countdownIntervalRef.current) {
        clearInterval(countdownIntervalRef.current);
      }
    };
  }, [fetchPortfolio, scheduleNextUpdate]);

  const handleBuyStock = () => {
    setSelectedHolding(null);
    setShowBuyModal(true);
  };
  
  const handleAdjustHolding = (holding) => {
    setSelectedHolding(holding);
    setShowBuyModal(true);
  };

  // Hover chart handlers
  const handleRowMouseEnter = (symbol, event) => {
    // Clear any existing timeout
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
    }

    // Set a delay before showing the chart (1 second)
    hoverTimeoutRef.current = setTimeout(() => {
      setHoverChart({
        visible: true,
        symbol: symbol,
        position: {
          x: event.clientX,
          y: event.clientY
        }
      });
    }, 1000);
  };

  const handleRowMouseLeave = () => {
    // Clear the timeout if user leaves before 1 second
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
      hoverTimeoutRef.current = null;
    }

    // Hide the chart
    setHoverChart(prev => ({ ...prev, visible: false }));
  };

  const handleRowClick = (symbol) => {
    // Hide hover chart when clicking
    setHoverChart(prev => ({ ...prev, visible: false }));
    // Navigate to stock detail page
    navigate(`/stock/${symbol}`);
  };

  const handleChartMouseLeave = () => {
    setHoverChart(prev => ({ ...prev, visible: false }));
  };
  
  const handleTransactionSuccess = (data) => {
    fetchPortfolio();
    setSelectedHolding(null);
    if (onTransactionSuccess) {
      onTransactionSuccess(data);
    }
  };

  // Only show error page if there's an error and absolutely no data exists
  if (error && !portfolio && !hasLoadedBefore) {
    return (
      <div className="portfolio-page">
        <h1 className="page-title">Portfolio</h1>
        <div className="error">
          <p>{error}</p>
          <button onClick={fetchPortfolio}>Try Again</button>
        </div>
      </div>
    );
  }

  const { cash_balance, holdings, total_value, holdings_value } = portfolio || {};
  const holdingsCount = holdings ? holdings.length : 0;

  return (
    <div className="portfolio-page">
      <h1 className="page-title">Portfolio</h1>
      
      <div className="market-status-bar">
        <div className="status-indicator-container">
          <span className="status-text">
            {portfolio ? (
              <>
                <span className={`market-status-text ${marketStatus.isOpen ? 'open' : 'closed'}`}>
                  Market {marketStatus.isOpen ? 'Open' : 'Closed'}
                </span>
                <span className="separator">|</span>
                <span className="update-text">Next update in {marketStatus.nextUpdateMinutes}m {marketStatus.nextUpdateSeconds}s</span>
              </>
            ) : (
              'Connecting to market data...'
            )}
          </span>
        </div>
        <div className="status-actions">
          <button className="icon-button buy-icon" onClick={handleBuyStock} title="Buy Stock" disabled={!hasLoadedBefore}>
            <span className="icon">+</span>
            <span className="button-text">Buy Stock</span>
          </button>
          <button className="icon-button refresh-icon" onClick={fetchPortfolio} title="Refresh">
            <span className="icon">↻</span>
            <span className="button-text">Refresh</span>
          </button>
        </div>
      </div>
      
      <div className="portfolio-summary">
        <div className="summary-cards">
          <div className="summary-card">
            <div className="card-label">Total Value</div>
            <div className="card-value">${total_value !== undefined ? total_value.toFixed(2) : '—'}</div>
            <div className="card-subtitle">
              {portfolio && portfolio.total_change !== undefined ? (
                <span className={`change-indicator ${portfolio.total_change >= 0 ? 'positive' : 'negative'}`}>
                  {portfolio.total_change >= 0 ? '+' : ''}{portfolio.total_change.toFixed(2)}%
                </span>
              ) : (
                <span className="change-placeholder">Today's change</span>
              )}
            </div>
          </div>
          
          <div className="summary-card">
            <div className="card-label">Holdings Value</div>
            <div className="card-value">${holdings_value !== undefined ? holdings_value.toFixed(2) : '—'}</div>
            <div className="card-subtitle">
              <span className="portfolio-percentage">
                {holdings_value && total_value ? ((holdings_value / total_value) * 100).toFixed(1) : '0.0'}% of portfolio
              </span>
            </div>
          </div>
          
          <div className="summary-card">
            <div className="card-label">Cash Balance</div>
            <div className="card-value">${cash_balance !== undefined ? cash_balance.toFixed(2) : '—'}</div>
            <div className="card-subtitle">
              <span className="portfolio-percentage">
                {cash_balance && total_value ? ((cash_balance / total_value) * 100).toFixed(1) : '0.0'}% of portfolio
              </span>
            </div>
          </div>
        </div>
      </div>
      
      {holdingsCount > 0 ? (
        <>
          <div className="positions-count">{holdingsCount} positions</div>
          <div className="holdings-table-container">
            <table className="holdings-table">
              <thead>
                <tr>
                  <th>SYMBOL</th>
                  <th>SHARES</th>
                  <th>AVG. COST</th>
                  <th>CURRENT PRICE</th>
                  <th>MARKET VALUE</th>
                  <th>PROFIT/LOSS</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {holdings.map((holding) => (
                  <tr 
                    key={holding.symbol}
                    className="holdings-row interactive-row"
                    onMouseEnter={(e) => handleRowMouseEnter(holding.symbol, e)}
                    onMouseLeave={handleRowMouseLeave}
                    onClick={() => handleRowClick(holding.symbol)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td className="symbol-cell clickable">{holding.symbol}</td>
                    <td>{parseFloat(holding.shares).toFixed(2)}</td>
                    <td>${holding.average_cost ? holding.average_cost.toFixed(2) : holding.avg_cost.toFixed(2)}</td>
                    <td>${holding.current_price.toFixed(2)}</td>
                    <td>${holding.market_value.toFixed(2)}</td>
                    <td className={`profit-cell ${holding.profit_loss >= 0 ? 'positive' : 'negative'}`}>
                      ${holding.profit_loss.toFixed(2)}
                      <br />
                      {holding.profit_loss_percent >= 0 ? '+' : ''}{holding.profit_loss_percent.toFixed(2)}%
                    </td>
                    <td className="action-cell">
                      <button 
                        className="table-icon-button adjust-icon" 
                        onClick={(e) => {
                          e.stopPropagation(); // Prevent row click
                          handleAdjustHolding(holding);
                        }}
                        title="Adjust Position"
                      >
                        <span className="icon">⚙</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : (
        <div className="no-holdings">
          <h3>No holdings yet</h3>
          <p>Start building your portfolio by buying your first stock.</p>
          <button onClick={handleBuyStock}>Buy Stock</button>
        </div>
      )}
      
      <BuyStock 
        isOpen={showBuyModal} 
        onClose={() => setShowBuyModal(false)}
        onSuccess={handleTransactionSuccess}
        existingHolding={selectedHolding}
      />

      {/* Global Loading Indicator */}
      <GlobalLoadingIndicator 
        isVisible={isUpdating || !portfolio} 
        message="•" 
      />

      {/* Hover Chart */}
      <HoverChart
        symbol={hoverChart.symbol}
        isVisible={hoverChart.visible}
        position={hoverChart.position}
        onMouseLeave={handleChartMouseLeave}
      />
    </div>
  );
};

export default PortfolioPage; 