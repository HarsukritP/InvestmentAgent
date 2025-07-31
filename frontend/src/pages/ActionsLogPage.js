import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ActionsLogPage.css';
import { API_URL } from '../config';
import { formatCurrency, formatDate } from '../utils/formatters';
import { FaArrowUp, FaArrowDown, FaCheck, FaTimes, FaSync } from 'react-icons/fa';
import GlobalLoadingIndicator from '../components/GlobalLoadingIndicator';

function ActionsLogPage() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    totalTransactions: 0,
    buys: 0,
    sells: 0,
    totalBuyAmount: 0,
    totalSellAmount: 0,
    mostTradedSymbol: 'N/A'
  });
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [alert, setAlert] = useState(null);

  // Fetch data when component mounts or refreshTrigger changes
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch transactions and stats in parallel
        const [transactionsResponse, statsResponse] = await Promise.all([
          axios.get(`${API_URL}/transactions`, { withCredentials: true }),
          axios.get(`${API_URL}/transaction-stats`, { withCredentials: true })
        ]);
        
        console.log('Transactions response:', transactionsResponse.data);
        console.log('Stats response:', statsResponse.data);
        
        // Handle transactions
        if (transactionsResponse.data.status === 'success') {
          setTransactions(transactionsResponse.data.data || []);
        } else {
          console.error('Error fetching transactions:', transactionsResponse.data.message);
          setTransactions([]);
        }
        
        // Handle stats
        if (statsResponse.data.status === 'success') {
          setStats({
            totalTransactions: statsResponse.data.transaction_count || 0,
            buys: statsResponse.data.buy_count || 0,
            sells: statsResponse.data.sell_count || 0,
            totalBuyAmount: statsResponse.data.total_buy_amount || 0,
            totalSellAmount: statsResponse.data.total_sell_amount || 0,
            mostTradedSymbol: statsResponse.data.most_traded_symbol || 'N/A'
          });
        } else {
          console.error('Error fetching transaction stats:', statsResponse.data.message);
          // Use default stats
          setStats({
            totalTransactions: 0,
            buys: 0,
            sells: 0,
            totalBuyAmount: 0,
            totalSellAmount: 0,
            mostTradedSymbol: 'N/A'
          });
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        setError('Failed to load data. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [refreshTrigger]);

  const handleRefresh = () => {
    setRefreshTrigger(prev => prev + 1);
    setAlert({ type: 'success', message: 'Data refreshed' });
  };

  const getTransactionIcon = (type) => {
    if (type === 'BUY' || type === 'BUY_NEW' || type === 'BUY_ADD') {
      return <FaArrowUp className="buy-icon" />;
    } else if (type === 'SELL') {
      return <FaArrowDown className="sell-icon" />;
    }
    return null;
  };

  return (
    <div className="actions-log-page">
      <h1>Actions Log</h1>
      
      {alert && (
        <div className={`alert alert-${alert.type}`}>
          {alert.type === 'success' && <FaCheck />}
          {alert.type === 'error' && <FaTimes />}
          {alert.type === 'info' && <FaSync className="spinning" />}
          {alert.message}
        </div>
      )}
      
      <div className="action-buttons">
        <button className="refresh-button" onClick={handleRefresh}>
          Refresh
        </button>
      </div>
      
      <div className="stats-section">
        <h2>Transaction Statistics</h2>
        <div className="stats-grid">
          <div className="stat-card">
            <h3>TOTAL TRANSACTIONS</h3>
            <p className="stat-value">{stats.totalTransactions}</p>
          </div>
          <div className="stat-card">
            <h3>BUY TRANSACTIONS</h3>
            <p className="stat-value">{stats.buys}</p>
          </div>
          <div className="stat-card">
            <h3>SELL TRANSACTIONS</h3>
            <p className="stat-value">{stats.sells}</p>
          </div>
          <div className="stat-card">
            <h3>TOTAL BUY AMOUNT</h3>
            <p className="stat-value">{formatCurrency(stats.totalBuyAmount)}</p>
          </div>
          <div className="stat-card">
            <h3>TOTAL SELL AMOUNT</h3>
            <p className="stat-value">{formatCurrency(stats.totalSellAmount)}</p>
          </div>
          <div className="stat-card">
            <h3>MOST TRADED SYMBOL</h3>
            <p className="stat-value">{stats.mostTradedSymbol}</p>
          </div>
        </div>
      </div>
      
      <div className="transactions-section">
        <h2>Transaction History</h2>
        {loading ? (
          <div className="loading">Loading transactions...</div>
        ) : error ? (
          <div className="error-state">
            <p>⚠️ {error}</p>
            <button onClick={handleRefresh} className="retry-button">
              Try Again
            </button>
          </div>
        ) : transactions.length > 0 ? (
          <div className="transactions-table-container">
            <table className="transactions-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Type</th>
                  <th>Symbol</th>
                  <th>Shares</th>
                  <th>Price</th>
                  <th>Total</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((transaction) => (
                  <tr key={transaction.id} className={transaction.transaction_type.toLowerCase()}>
                    <td>{formatDate(transaction.created_at)}</td>
                    <td className="transaction-type">
                      {getTransactionIcon(transaction.transaction_type)}
                      {transaction.transaction_type}
                    </td>
                    <td>{transaction.symbol}</td>
                    <td>{transaction.shares}</td>
                    <td>{formatCurrency(transaction.price_per_share)}</td>
                    <td>{formatCurrency(transaction.total_amount)}</td>
                    <td>{transaction.notes || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="no-transactions">
            <div className="chart-icon">📊</div>
            <h3>No Transactions Yet</h3>
            <p>Your transaction history will appear here after you buy or sell stocks.</p>
          </div>
        )}
      </div>
      
      {/* Global Loading Indicator */}
      <GlobalLoadingIndicator 
        isVisible={loading} 
        message="•" 
      />
    </div>
  );
}

export default ActionsLogPage; 