import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import StockChart from '../components/StockChart';
import { Line } from 'react-chartjs-2';
import './StockDetailPage.css';

const StockDetailPage = () => {
  const { symbol } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [stockDetails, setStockDetails] = useState(null);
  const [stockInfo, setStockInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedChart, setSelectedChart] = useState('price');

  // Handle back navigation based on where user came from
  const handleBackNavigation = () => {
    const from = location.state?.from;
    if (from) {
      navigate(from);
    } else {
      // Default fallback to portfolio
      navigate('/portfolio');
    }
  };

  const fetchStockDetails = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch both stock details and basic stock info (for exchange data)
      const [detailsResponse, searchResponse] = await Promise.all([
        axios.get(`/stock-details/${symbol}`),
        axios.get(`/search-stocks?query=${symbol}`)
      ]);
      
      const data = detailsResponse.data;
      setStockDetails(data);
      
      // Find the exact match in search results for exchange info
      const searchResults = searchResponse.data.results || [];
      const exactMatch = searchResults.find(stock => 
        stock.symbol.toLowerCase() === symbol.toLowerCase()
      );
      if (exactMatch) {
        setStockInfo(exactMatch);
      }

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  useEffect(() => {
    if (symbol) {
      fetchStockDetails();
    }
  }, [symbol, fetchStockDetails]);

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
            <button onClick={handleBackNavigation} className="back-btn">
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
            onClick={handleBackNavigation}
            title="Back"
          >
            ← Back
          </button>
          <div className="stock-title">
            <h1>{symbol}</h1>
            <div className="stock-subtitle-container">
              <span className="stock-subtitle">Stock Details & Charts</span>
              {stockInfo && (
                <div className="stock-exchange-info">
                  {stockInfo.exchange && <span className="exchange-badge">{stockInfo.exchange}</span>}
                  {stockInfo.region && stockInfo.region !== 'United States' && (
                    <span className="region-badge">{stockInfo.region}</span>
                  )}
                  {stockInfo.currency && stockInfo.currency !== 'USD' && (
                    <span className="currency-badge">{stockInfo.currency}</span>
                  )}
                </div>
              )}
            </div>
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
      
      console.log(`🔍 IntradayChart: Fetching intraday data for ${symbol} with interval ${interval}`);
      
      const response = await axios.get(`/intraday/${symbol}?interval=${interval}&outputsize=50`);
      const data = response.data;
      
      console.log(`📊 IntradayChart: Received data for ${symbol}:`, data);
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

  // Format data for display with even intervals
  const allData = intradayData.data; // Already in chronological order
  
  // Filter to get evenly spaced intervals
  const filteredData = [];
  const intervalMinutes = interval === '1h' ? 60 : interval === '30min' ? 30 : interval === '2h' ? 120 : 240;
  
  for (let i = 0; i < allData.length; i++) {
    const point = allData[i];
    const datetime = new Date(point.datetime);
    const minutes = datetime.getMinutes();
    const hours = datetime.getHours();
    
    // Only include points that fall on even intervals
    if (intervalMinutes === 60) {
      // For hourly: only show on the hour
      if (minutes === 0) filteredData.push(point);
    } else if (intervalMinutes === 30) {
      // For 30min: show on :00 and :30
      if (minutes === 0 || minutes === 30) filteredData.push(point);
    } else if (intervalMinutes === 120) {
      // For 2h: show every 2 hours on the hour
      if (minutes === 0 && hours % 2 === 0) filteredData.push(point);
    } else if (intervalMinutes === 240) {
      // For 4h: show every 4 hours on the hour
      if (minutes === 0 && hours % 4 === 0) filteredData.push(point);
    } else {
      filteredData.push(point);
    }
  }
  
  const prices = filteredData.map(point => point.close);

  return (
    <div className="intraday-chart-container">
      <div className="intraday-controls">
        <div className="interval-selector">
          {['30min', '1h', '2h', '4h'].map(int => {
            console.log(`🔧 Rendering interval button: ${int}, active: ${interval === int}`);
            return (
              <button
                key={int}
                className={`interval-btn ${interval === int ? 'active' : ''}`}
                onClick={() => {
                  console.log(`🔧 Interval button clicked: ${int}`);
                  setInterval(int);
                }}
                style={{ 
                  display: 'inline-block',
                  visibility: 'visible',
                  opacity: 1
                }}
              >
                {int}
              </button>
            );
          })}
        </div>
      </div>
      
      <div className="intraday-chart-wrapper">
        <div style={{ height: '400px' }}>
          <Line
            data={{
              labels: filteredData.map(point => {
                const datetime = new Date(point.datetime);
                return datetime.toLocaleTimeString('en-US', {
                  hour: '2-digit',
                  minute: '2-digit',
                  timeZone: 'America/New_York',
                  hour12: false
                }) + ' ET';
              }),
              datasets: [
                {
                  label: `${symbol} Price`,
                  data: prices,
                  borderColor: prices[prices.length - 1] >= prices[0] ? '#8BC34A' : '#E57373',
                  backgroundColor: prices[prices.length - 1] >= prices[0] ? 'rgba(139, 195, 74, 0.1)' : 'rgba(229, 115, 115, 0.1)',
                  borderWidth: 2,
                  fill: true,
                  tension: 0.1,
                  pointBackgroundColor: prices[prices.length - 1] >= prices[0] ? '#8BC34A' : '#E57373',
                  pointBorderColor: '#ffffff',
                  pointBorderWidth: 2,
                  pointRadius: 3,
                  pointHoverRadius: 5,
                }
              ]
            }}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              layout: {
                padding: {
                  left: 10,
                  right: 10,
                  top: 10,
                  bottom: 10
                }
              },
              plugins: {
                legend: {
                  display: true,
                  position: 'top',
                  labels: {
                    font: { size: 14 },
                    color: '#2C3E50'
                  }
                },
                title: {
                  display: true,
                  text: `${symbol} - ${interval} intervals (${filteredData.length} data points)`,
                  font: { size: 16, weight: 'bold' },
                  color: '#2C3E50'
                },
                tooltip: {
                  enabled: true,
                  mode: 'nearest',
                  intersect: false,
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  titleColor: '#2C3E50',
                  bodyColor: '#2C3E50',
                  borderColor: '#8BC34A',
                  borderWidth: 1,
                  titleFont: { size: 12 },
                  bodyFont: { size: 11 },
                  callbacks: {
                    label: function(context) {
                      return `Price: $${context.parsed.y.toFixed(2)}`;
                    },
                    afterLabel: function(context) {
                      const index = context.dataIndex;
                      if (index > 0) {
                        const currentPrice = context.parsed.y;
                        const prevPrice = prices[index - 1];
                        const change = currentPrice - prevPrice;
                        const changePercent = (change / prevPrice * 100);
                        const sign = change >= 0 ? '+' : '';
                        return `Change: ${sign}$${change.toFixed(2)} (${sign}${changePercent.toFixed(2)}%)`;
                      }
                      return '';
                    }
                  }
                }
              },
              scales: {
                x: {
                  display: true,
                  grid: {
                    display: false
                  },
                  ticks: {
                    display: true,
                    maxTicksLimit: 8,
                    color: '#7A8A9A',
                    font: { size: 11 }
                  }
                },
                y: {
                  display: true,
                  grid: {
                    display: true,
                    color: 'rgba(139, 195, 74, 0.1)'
                  },
                  ticks: {
                    display: true,
                    maxTicksLimit: 6,
                    color: '#7A8A9A',
                    font: { size: 11 },
                    callback: function(value) {
                      return '$' + value.toFixed(2);
                    }
                  }
                }
              },
              interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
              }
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default StockDetailPage;