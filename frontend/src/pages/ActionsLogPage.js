import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { formatCurrency, formatDate } from '../utils/formatters';
import GlobalLoadingIndicator from '../components/GlobalLoadingIndicator';
import './ActionsLogPage.css';

const ActionsLogPage = () => {
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
  const [transactions, setTransactions] = useState(getCachedData('actions_transactions'));
  const [stats, setStats] = useState(getCachedData('actions_stats'));
  const [isUpdating, setIsUpdating] = useState(false);
  const [hasLoadedBefore, setHasLoadedBefore] = useState(!!getCachedData('actions_transactions'));
  const [error, setError] = useState(null);
  
  // Filter and sort state
  const [filterType, setFilterType] = useState('ALL');
  const [sortBy, setSortBy] = useState('DATE_DESC');
  const [searchQuery, setSearchQuery] = useState('');
  const [timeFilter, setTimeFilter] = useState('ALL_TIME');

  // Fetch transaction data
  const fetchTransactions = async () => {
    try {
      const response = await axios.get('/transactions', { withCredentials: true });
      
      if (response.data.status === 'success') {
        const transactionData = response.data.data || [];
        setTransactions(transactionData);
        localStorage.setItem('actions_transactions', JSON.stringify(transactionData));
        return transactionData;
      } else {
        console.error('Error fetching transactions:', response.data.message);
        setTransactions([]);
        return [];
      }
    } catch (error) {
      console.error('Error fetching transactions:', error);
      throw error;
    }
  };

  // Fetch stats data
  const fetchStats = async () => {
    try {
      const response = await axios.get('/transaction-stats', { withCredentials: true });
      
      if (response.data.status === 'success') {
        const statsData = {
          totalTransactions: response.data.transaction_count || 0,
          buys: response.data.buy_count || 0,
          sells: response.data.sell_count || 0,
          totalBuyAmount: response.data.total_buy_amount || 0,
          totalSellAmount: response.data.total_sell_amount || 0,
          mostTradedSymbol: response.data.most_traded_symbol || 'N/A'
        };
        setStats(statsData);
        localStorage.setItem('actions_stats', JSON.stringify(statsData));
        return statsData;
      } else {
        console.error('Error fetching transaction stats:', response.data.message);
        // Use default stats
        const defaultStats = {
          totalTransactions: 0,
          buys: 0,
          sells: 0,
          totalBuyAmount: 0,
          totalSellAmount: 0,
          mostTradedSymbol: 'N/A'
        };
        setStats(defaultStats);
        return defaultStats;
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
      throw error;
    }
  };

  // Refresh all data
  const refreshData = async () => {
    setIsUpdating(true);
    setError(null);
    
    try {
      // Fetch both transactions and stats concurrently
      await Promise.all([
        fetchTransactions(),
        fetchStats()
      ]);
      
      setHasLoadedBefore(true);
    } catch (error) {
      console.error('Error refreshing data:', error);
      setError('Failed to load transaction data. Please try again.');
    } finally {
      setIsUpdating(false);
    }
  };

  // Initial data load
  useEffect(() => {
    refreshData();
  }, []);

  // Get transaction type icon
  const getTransactionIcon = (type) => {
    if (type === 'BUY' || type === 'BUY_NEW' || type === 'BUY_ADD') {
      return '↗';
    } else if (type === 'SELL') {
      return '↘';
    }
    return '◦';
  };

  // Get transaction type color class
  const getTransactionColorClass = (type) => {
    if (type === 'BUY' || type === 'BUY_NEW' || type === 'BUY_ADD') {
      return 'buy-transaction';
    } else if (type === 'SELL') {
      return 'sell-transaction';
    }
    return 'other-transaction';
  };

  // Handle stock symbol click
  const handleSymbolClick = (symbol) => {
    navigate(`/stock/${symbol}`, { state: { from: '/actions-log' } });
  };

  // Filter and sort transactions
  const getFilteredAndSortedTransactions = () => {
    if (!transactions) return [];
    
    let filtered = transactions;
    
    // Apply type filter
    if (filterType !== 'ALL') {
      if (filterType === 'BUY') {
        filtered = filtered.filter(t => ['BUY', 'BUY_NEW', 'BUY_ADD'].includes(t.transaction_type));
      } else if (filterType === 'SELL') {
        filtered = filtered.filter(t => t.transaction_type === 'SELL');
      }
    }
    
    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(t => 
        t.symbol.toLowerCase().includes(query) ||
        (t.notes && t.notes.toLowerCase().includes(query))
      );
    }
    
    // Apply time filter
    if (timeFilter !== 'ALL_TIME') {
      const now = new Date();
      let startDate;
      
      if (timeFilter === 'THIS_WEEK') {
        startDate = new Date(now);
        startDate.setDate(now.getDate() - 7);
      } else if (timeFilter === 'THIS_MONTH') {
        startDate = new Date(now);
        startDate.setMonth(now.getMonth() - 1);
      }
      
      if (startDate) {
        filtered = filtered.filter(t => new Date(t.created_at) >= startDate);
      }
    }
    
    // Apply sorting
    const sorted = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'DATE_DESC':
          return new Date(b.created_at) - new Date(a.created_at);
        case 'DATE_ASC':
          return new Date(a.created_at) - new Date(b.created_at);
        case 'AMOUNT_DESC':
          return b.total_amount - a.total_amount;
        case 'AMOUNT_ASC':
          return a.total_amount - b.total_amount;
        case 'SYMBOL_ASC':
          return a.symbol.localeCompare(b.symbol);
        case 'SYMBOL_DESC':
          return b.symbol.localeCompare(a.symbol);
        default:
          return 0;
      }
    });
    
    return sorted;
  };

  // Only show error page if there's an error and absolutely no data exists
  if (error && !transactions && !hasLoadedBefore) {
    return (
      <div className="actions-log-page">
        <h1 className="page-title">Actions Log</h1>
        <div className="error">
          <p>{error}</p>
          <button onClick={refreshData}>Try Again</button>
        </div>
      </div>
    );
  }

  const netTradingAmount = (stats?.totalSellAmount || 0) - (stats?.totalBuyAmount || 0);

  return (
    <div className="actions-log-page">
      <h1 className="page-title">Actions Log</h1>
      
      {/* Market Status Bar */}
      <div className="market-status-bar">
        <div className="status-indicator-container">
          <span className="status-text">
            <span className="activity-text">Trading Activity</span>
            <span className="separator">|</span>
            <div className="filter-controls">
              <input
                type="text"
                placeholder="Search symbol or notes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
              />
              <select 
                value={timeFilter} 
                onChange={(e) => setTimeFilter(e.target.value)}
                className="time-filter-select"
              >
                <option value="ALL_TIME">All Time</option>
                <option value="THIS_MONTH">This Month</option>
                <option value="THIS_WEEK">This Week</option>
              </select>
              <select 
                value={filterType} 
                onChange={(e) => setFilterType(e.target.value)}
                className="filter-select"
              >
                <option value="ALL">All Types</option>
                <option value="BUY">Buy Orders</option>
                <option value="SELL">Sell Orders</option>
              </select>
              <select 
                value={sortBy} 
                onChange={(e) => setSortBy(e.target.value)}
                className="sort-select"
              >
                <option value="DATE_DESC">Latest First</option>
                <option value="DATE_ASC">Oldest First</option>
                <option value="AMOUNT_DESC">Highest Amount</option>
                <option value="AMOUNT_ASC">Lowest Amount</option>
                <option value="SYMBOL_ASC">Symbol A-Z</option>
                <option value="SYMBOL_DESC">Symbol Z-A</option>
              </select>
            </div>
          </span>
        </div>
        <div className="status-actions">
          <button 
            className="icon-button refresh-icon" 
            onClick={refreshData} 
            title="Refresh Data"
            disabled={isUpdating}
          >
            <span className="icon">↻</span>
            <span className="button-text">Refresh</span>
          </button>
        </div>
      </div>

      {/* Transaction Summary */}
      <div className="transaction-summary">
        <div className="summary-cards">
          <div className="summary-card">
            <div className="card-label">Total Transactions</div>
            <div className="card-value">{stats?.totalTransactions || 0}</div>
            <div className="card-subtitle">
              <span className="transaction-info">All time activity</span>
            </div>
          </div>
          
          <div className="summary-card">
            <div className="card-label">Buy Orders</div>
            <div className="card-value">{stats?.buys || 0}</div>
            <div className="card-subtitle">
              <span className="buy-info">{formatCurrency(stats?.totalBuyAmount || 0)} invested</span>
            </div>
          </div>
          
          <div className="summary-card">
            <div className="card-label">Sell Orders</div>
            <div className="card-value">{stats?.sells || 0}</div>
            <div className="card-subtitle">
              <span className="sell-info">{formatCurrency(stats?.totalSellAmount || 0)} realized</span>
            </div>
          </div>

          <div className="summary-card">
            <div className="card-label">Net Trading</div>
            <div className="card-value">{formatCurrency(netTradingAmount)}</div>
            <div className="card-subtitle">
              <span className={`net-info ${netTradingAmount >= 0 ? 'positive' : 'negative'}`}>
                {netTradingAmount >= 0 ? 'Net inflow' : 'Net outflow'}
              </span>
            </div>
          </div>

          <div className="summary-card">
            <div className="card-label">Most Traded</div>
            <div className="card-value symbol-value">{stats?.mostTradedSymbol || 'N/A'}</div>
            <div className="card-subtitle">
              <span className="traded-info">Favorite stock</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Transaction History */}
      {transactions && transactions.length > 0 ? (
        <>
          <div className="transactions-count">
            {getFilteredAndSortedTransactions().length} transactions
            {(filterType !== 'ALL' || sortBy !== 'DATE_DESC' || searchQuery.trim() || timeFilter !== 'ALL_TIME') ? ` (filtered/sorted)` : ''}
          </div>
          <div className="transactions-table-container">
            <table className="transactions-table">
              <thead>
                <tr>
                  <th>DATE</th>
                  <th>TYPE</th>
                  <th>SYMBOL</th>
                  <th>SHARES</th>
                  <th>PRICE</th>
                  <th>TOTAL</th>
                  <th>NOTES</th>
                </tr>
              </thead>
              <tbody>
                {getFilteredAndSortedTransactions().map((transaction) => (
                  <tr 
                    key={transaction.id}
                    className={`transaction-row ${getTransactionColorClass(transaction.transaction_type)}`}
                  >
                    <td className="date-cell">{formatDate(transaction.created_at)}</td>
                    <td className="type-cell">
                      <span className="transaction-type">
                        <span className="transaction-icon">
                          {getTransactionIcon(transaction.transaction_type)}
                        </span>
                        {transaction.transaction_type}
                      </span>
                    </td>
                    <td className="symbol-cell">
                      <button 
                        className="symbol-link"
                        onClick={() => handleSymbolClick(transaction.symbol)}
                        title={`View ${transaction.symbol} details`}
                      >
                        {transaction.symbol}
                      </button>
                    </td>
                    <td className="shares-cell">{transaction.shares}</td>
                    <td className="price-cell">{formatCurrency(transaction.price_per_share)}</td>
                    <td className="total-cell">{formatCurrency(transaction.total_amount)}</td>
                    <td className="notes-cell">{transaction.notes || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : (
        <div className="no-transactions">
          <div className="no-transactions-icon">◯</div>
          <h3>No Transactions Yet</h3>
          <p>Your transaction history will appear here after you buy or sell stocks.</p>
          <button className="start-trading-btn" onClick={() => navigate('/portfolio')}>
            Start Trading
          </button>
        </div>
      )}
      
      {/* Global Loading Indicator */}
      <GlobalLoadingIndicator 
        isVisible={isUpdating || (!transactions && !hasLoadedBefore)} 
        message="•" 
      />
    </div>
  );
};

export default ActionsLogPage;