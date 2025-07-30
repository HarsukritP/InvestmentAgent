import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import StockChart from '../components/StockChart';
import './StockDetailPage.css';

const StockDetailPage = () => {
  const { symbol } = useParams();
  const navigate = useNavigate();
  const [stockDetails, setStockDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedChart, setSelectedChart] = useState('price');

  useEffect(() => {
    if (symbol) {
      fetchStockDetails();
    }
  }, [symbol, fetchStockDetails]);

  const fetchStockDetails = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/stock-details/${symbol}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch stock details: ${response.status}`);
      }

      const data = await response.json();
      setStockDetails(data);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  const formatCurrency = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatPercentage = (value) => {
    if (value === null || value === undefined) return 'N/A';
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  const formatNumber = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US').format(value);
  };

  if (loading) {
    return (
      <div className="stock-detail-page">
        <div className="stock-detail-loading">
          <div className="detail-spinner"></div>
          <h2>Loading {symbol} details...</h2>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stock-detail-page">
        <div className="stock-detail-error">
          <h2>❌ Error loading stock details</h2>
          <p>{error}</p>
          <div className="error-actions">
            <button onClick={fetchStockDetails} className="retry-btn">
              Try Again
            </button>
            <button onClick={() => navigate('/portfolio')} className="back-btn">
              Back to Portfolio
            </button>
          </div>
        </div>
      </div>
    );
  }

  const { quote, analytics } = stockDetails || {};

  return (
    <div className="stock-detail-page">
      {/* Header Section */}
      <div className="stock-detail-header">
        <div className="header-main">
          <button 
            className="back-button" 
            onClick={() => navigate('/portfolio')}
            title="Back to Portfolio"
          >
            ← Back
          </button>
          <div className="stock-title">
            <h1>{symbol}</h1>
            <span className="stock-subtitle">Stock Details & Charts</span>
          </div>
        </div>
        
        <div className="price-section">
          <div className="current-price">
            {formatCurrency(quote?.price)}
          </div>
          <div className={`price-change ${analytics?.daily_change >= 0 ? 'positive' : 'negative'}`}>
            {analytics?.daily_change >= 0 ? '↗' : '↘'} 
            {formatCurrency(Math.abs(analytics?.daily_change || 0))} 
            ({formatPercentage(analytics?.daily_change_percent)})
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-section">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">24h Change</div>
            <div className={`stat-value ${analytics?.daily_change >= 0 ? 'positive' : 'negative'}`}>
              {formatPercentage(analytics?.daily_change_percent)}
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-label">7d Change</div>
            <div className={`stat-value ${analytics?.weekly_change >= 0 ? 'positive' : 'negative'}`}>
              {formatPercentage(analytics?.weekly_change_percent)}
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-label">30d Change</div>
            <div className={`stat-value ${analytics?.monthly_change >= 0 ? 'positive' : 'negative'}`}>
              {formatPercentage(analytics?.monthly_change_percent)}
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-label">52W High</div>
            <div className="stat-value">
              {formatCurrency(analytics?.high_52w)}
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-label">52W Low</div>
            <div className="stat-value">
              {formatCurrency(analytics?.low_52w)}
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-label">Avg Volume</div>
            <div className="stat-value">
              {formatNumber(analytics?.avg_volume)}
            </div>
          </div>
        </div>
      </div>

      {/* Chart Section */}
      <div className="chart-section">
        <div className="chart-controls">
          <h2>📈 Interactive Charts</h2>
          <div className="chart-type-selector">
            <button 
              className={`chart-type-btn ${selectedChart === 'price' ? 'active' : ''}`}
              onClick={() => setSelectedChart('price')}
            >
              Price Chart
            </button>
            <button 
              className={`chart-type-btn ${selectedChart === 'intraday' ? 'active' : ''}`}
              onClick={() => setSelectedChart('intraday')}
            >
              Intraday (Hourly)
            </button>
          </div>
        </div>
        
        <div className="chart-container">
          {selectedChart === 'price' ? (
            <StockChart 
              symbol={symbol}
              period="6months"
              height={500}
              showControls={true}
            />
          ) : (
            <IntradayChart symbol={symbol} />
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="actions-section">
        <div className="action-cards">
          <div className="action-card">
            <h3>📊 Market Data</h3>
            <p>Real-time price: {formatCurrency(quote?.price)}</p>
            <p>Last updated: {new Date(stockDetails?.last_updated).toLocaleTimeString()}</p>
          </div>
          
          <div className="action-card">
            <h3>📈 Performance</h3>
            <p>Today: {formatPercentage(analytics?.daily_change_percent)}</p>
            <p>This week: {formatPercentage(analytics?.weekly_change_percent)}</p>
            <p>This month: {formatPercentage(analytics?.monthly_change_percent)}</p>
          </div>
          
          <div className="action-card">
            <h3>🎯 Quick Actions</h3>
            <button 
              className="action-btn buy-btn"
              onClick={() => navigate(`/buy?symbol=${symbol}`)}
            >
              Buy More Shares
            </button>
            <button 
              className="action-btn portfolio-btn"
              onClick={() => navigate('/portfolio')}
            >
              View Portfolio
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Intraday Chart Component
const IntradayChart = ({ symbol }) => {
  const [intradayData, setIntradayData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [interval, setInterval] = useState('1h');

  const fetchIntradayData = useCallback(async () => {
    try {
      setLoading(true);
      
      const response = await fetch(`/api/intraday/${symbol}?interval=${interval}&outputsize=50`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch intraday data');
      }

      const data = await response.json();
      setIntradayData(data);

    } catch (err) {
      console.error('Error fetching intraday data:', err);
    } finally {
      setLoading(false);
    }
  }, [symbol, interval]);

  useEffect(() => {
    fetchIntradayData();
  }, [fetchIntradayData]);

  if (loading) {
    return (
      <div className="intraday-loading">
        <div className="detail-spinner"></div>
        <p>Loading intraday data...</p>
      </div>
    );
  }

  if (!intradayData?.data) {
    return (
      <div className="intraday-error">
        <p>❌ Intraday data unavailable</p>
      </div>
    );
  }

  // Format data for display
  const chartData = intradayData.data.reverse(); // Chronological order
  const prices = chartData.map(point => point.close);

  return (
    <div className="intraday-chart-container">
      <div className="intraday-controls">
        <div className="interval-selector">
          {['30min', '1h', '2h', '4h'].map(int => (
            <button
              key={int}
              className={`interval-btn ${interval === int ? 'active' : ''}`}
              onClick={() => setInterval(int)}
            >
              {int}
            </button>
          ))}
        </div>
      </div>
      
      <div className="intraday-chart-wrapper">
        <div style={{ height: '400px' }}>
          {/* We'll use the StockChart component but with custom data */}
          <div className="chart-placeholder">
            <p>📊 Intraday chart with {chartData.length} data points</p>
            <p>Price range: ${Math.min(...prices).toFixed(2)} - ${Math.max(...prices).toFixed(2)}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StockDetailPage;