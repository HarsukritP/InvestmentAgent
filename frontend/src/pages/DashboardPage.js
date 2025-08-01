import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { isMarketOpen } from '../utils/formatters';
import GlobalLoadingIndicator from '../components/GlobalLoadingIndicator';
import './DashboardPage.css';

const DashboardPage = () => {
  const navigate = useNavigate();
  
  // Load cached data immediately if available
  const getCachedData = (key) => {
    try {
      const cached = localStorage.getItem(key);
      return cached ? JSON.parse(cached) : null;
    } catch (error) {
      console.warn(`Failed to load cached ${key}:`, error);
      return null;
    }
  };

  // State management
  const [portfolio, setPortfolio] = useState(getCachedData('dashboard_portfolio'));
  const [news, setNews] = useState(getCachedData('dashboard_news'));
  const [marketStatus, setMarketStatus] = useState({
    isOpen: false,
    nextUpdateMinutes: 5,
    nextUpdateSeconds: 0
  });
  const [isUpdating, setIsUpdating] = useState(false);
  const [hasLoadedBefore, setHasLoadedBefore] = useState(!!getCachedData('dashboard_portfolio'));
  
  // Stock lookup state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [searchError, setSearchError] = useState('');

  // Fetch portfolio summary
  const fetchPortfolioSummary = useCallback(async () => {
    try {
      const response = await axios.get('/portfolio');
      const portfolioData = response.data.portfolio || {};
      const holdingsData = response.data.holdings || [];
      
      const cashBalance = portfolioData.cash_balance || 0;
      const holdingsValue = holdingsData.reduce((total, holding) => total + (holding.market_value || 0), 0);
      const totalValue = cashBalance + holdingsValue;
      
      const portfolioSummary = {
        cash_balance: cashBalance,
        holdings: holdingsData.slice(0, 5), // Top 5 holdings for dashboard
        holdings_count: holdingsData.length,
        total_value: totalValue,
        holdings_value: holdingsValue
      };
      
      setPortfolio(portfolioSummary);
      localStorage.setItem('dashboard_portfolio', JSON.stringify(portfolioSummary));
      
      return portfolioSummary;
    } catch (error) {
      console.error('Error fetching portfolio:', error);
      throw error;
    }
  }, []);

  // Fetch market news
  const fetchNews = useCallback(async () => {
    try {
      const response = await axios.get('/market-news');
      const newsData = {
        articles: response.data.general_news || [],
        timestamp: new Date().toISOString()
      };
      
      setNews(newsData);
      localStorage.setItem('dashboard_news', JSON.stringify(newsData));
      
      return newsData;
    } catch (error) {
      console.error('Error fetching news:', error);
      // Don't throw error for news, it's not critical
      return null;
    }
  }, []);

  // Search stocks
  const searchStocks = async () => {
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    setHasSearched(true);
    setSearchError('');
    
    try {
      const response = await axios.get(`/search-stocks?query=${encodeURIComponent(searchQuery.trim())}`);
      setSearchResults(response.data.results || []);
    } catch (error) {
      console.error('Search error:', error);
      setSearchError('Failed to search stocks. Please try again.');
    } finally {
      setIsSearching(false);
    }
  };

  // Handle stock selection
  const handleStockSelect = (stock) => {
    navigate(`/stock/${stock.symbol}`);
  };

  // Handle key press for search
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      searchStocks();
    }
  };

  // Refresh all dashboard data
  const refreshDashboard = useCallback(async () => {
    setIsUpdating(true);
    
    try {
      // Fetch both portfolio and news concurrently
      await Promise.all([
        fetchPortfolioSummary(),
        fetchNews()
      ]);
      
      setHasLoadedBefore(true);
      
      // Update market status
      const currentMarketOpen = isMarketOpen();
      setMarketStatus(prev => ({
        ...prev,
        isOpen: currentMarketOpen
      }));
      
    } catch (error) {
      console.error('Error refreshing dashboard:', error);
    } finally {
      setIsUpdating(false);
    }
  }, [fetchPortfolioSummary, fetchNews]);

  // Initial data load
  useEffect(() => {
    refreshDashboard();
  }, [refreshDashboard]);

  // Format time ago
  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMinutes = Math.floor((now - time) / (1000 * 60));
    
    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)}h ago`;
    return `${Math.floor(diffMinutes / 1440)}d ago`;
  };

  const { cash_balance, holdings, holdings_count, total_value, holdings_value } = portfolio || {};

  return (
    <div className="dashboard-page">
      <h1 className="page-title">Dashboard</h1>
      
      {/* Market Status Bar */}
      <div className="market-status-bar">
        <div className="status-indicator-container">
          <span className="status-text">
            {portfolio ? (
              <>
                <span className={`market-status-text ${marketStatus.isOpen ? 'open' : 'closed'}`}>
                  Market {marketStatus.isOpen ? 'Open' : 'Closed'}
                </span>
                <span className="separator">|</span>
                <span className="update-text">Welcome to your portfolio dashboard</span>
              </>
            ) : (
              'Loading dashboard...'
            )}
          </span>
        </div>
        <div className="status-actions">
          <button 
            className="icon-button refresh-icon" 
            onClick={refreshDashboard} 
            title="Refresh Dashboard"
            disabled={isUpdating}
          >
            <span className="icon">↻</span>
            <span className="button-text">Refresh</span>
          </button>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Portfolio Summary Section */}
        <div className="dashboard-section portfolio-section">
          <div className="section-header">
            <h2 className="section-title">Portfolio Summary</h2>
            <button 
              className="view-all-button"
              onClick={() => navigate('/portfolio')}
            >
              View All →
            </button>
          </div>
          
          <div className="summary-cards">
            <div className="summary-card">
              <div className="card-label">Total Value</div>
              <div className="card-value">${total_value !== undefined ? total_value.toFixed(2) : '—'}</div>
              <div className="card-subtitle">
                <span className="portfolio-info">
                  {holdings_count || 0} positions
                </span>
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
          
          {/* Top Holdings */}
          {holdings && holdings.length > 0 && (
            <div className="top-holdings">
              <h3 className="holdings-title">Top Holdings</h3>
              <div className="holdings-list">
                {holdings.map((holding) => (
                  <div key={holding.symbol} className="holding-item" onClick={() => navigate(`/stock/${holding.symbol}`)}>
                    <div className="holding-info">
                      <span className="holding-symbol">{holding.symbol}</span>
                      <span className="holding-shares">{holding.shares} shares</span>
                    </div>
                    <div className="holding-values">
                      <span className="holding-value">${holding.market_value?.toFixed(2) || '0.00'}</span>
                      <span className={`holding-change ${holding.profit_loss_percent >= 0 ? 'positive' : 'negative'}`}>
                        {holding.profit_loss_percent >= 0 ? '+' : ''}{holding.profit_loss_percent?.toFixed(2) || '0.00'}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Stock Lookup Section */}
        <div className="dashboard-section lookup-section">
          <div className="section-header">
            <h2 className="section-title">Quick Stock Lookup</h2>
          </div>
          
          <div className="stock-search">
            <div className="search-box">
              <input
                type="text"
                placeholder="Search stocks by symbol or name..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setHasSearched(false);
                }}
                onKeyPress={handleKeyPress}
              />
              <button 
                className="search-button"
                onClick={searchStocks}
                disabled={isSearching || !searchQuery.trim()}
              >
                {isSearching ? 'Searching...' : 'Search'}
              </button>
            </div>
            
            {searchError && <div className="error-message">{searchError}</div>}
            
            {isSearching ? (
              <div className="loading-indicator">
                <div className="spinner"></div>
                <p>Searching for stocks...</p>
              </div>
            ) : (
              <div className="search-results">
                {searchResults.length > 0 ? (
                  <ul className="stock-list">
                    {searchResults.slice(0, 5).map((stock, index) => (
                      <li key={index} className="stock-item" onClick={() => handleStockSelect(stock)}>
                        <div className="stock-info">
                          <div className="stock-symbol">{stock.symbol}</div>
                          <div className="stock-name">{stock.name}</div>
                          {(stock.exchange || stock.region || stock.currency) && (
                            <div className="stock-details">
                              {stock.exchange && <span className="stock-exchange">{stock.exchange}</span>}
                              {stock.region && stock.region !== 'United States' && <span className="stock-region">{stock.region}</span>}
                              {stock.currency && stock.currency !== 'USD' && <span className="stock-currency">{stock.currency}</span>}
                            </div>
                          )}
                        </div>
                        {stock.current_price && (
                          <div className="stock-price">${stock.current_price.toFixed(2)}</div>
                        )}
                      </li>
                    ))}
                  </ul>
                ) : hasSearched && searchQuery.trim() ? (
                  <div className="no-results">No stocks found matching "{searchQuery}"</div>
                ) : null}
              </div>
            )}
          </div>
        </div>

        {/* News Feed Section */}
        <div className="dashboard-section news-section">
          <div className="section-header">
            <h2 className="section-title">Market News</h2>
          </div>
          
          <div className="news-feed">
            {news && news.articles && news.articles.length > 0 ? (
              <div className="news-list">
                {news.articles.slice(0, 6).map((article, index) => (
                  <div key={index} className="news-item" onClick={() => window.open(article.url, '_blank')}>
                    <div className="news-content">
                      <h4 className="news-title">{article.title}</h4>
                      <p className="news-description">{article.description}</p>
                      <div className="news-meta">
                        <span className="news-source">{article.source}</span>
                        <span className="news-time">{formatTimeAgo(article.published_at)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-news">
                <p>Loading market news...</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Global Loading Indicator */}
      <GlobalLoadingIndicator 
        isVisible={isUpdating || (!portfolio && !hasLoadedBefore)} 
        message="•" 
      />
    </div>
  );
};

export default DashboardPage;