import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './TransactionHistory.css';

const TransactionHistory = ({ isOpen, onClose }) => {
  const [transactions, setTransactions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [cashBalance, setCashBalance] = useState(0);

  useEffect(() => {
    if (isOpen) {
      fetchTransactions();
    }
  }, [isOpen]);

  const fetchTransactions = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await axios.get('/transactions');
      setTransactions(response.data.transactions || []);
      setCashBalance(response.data.cash_balance || 0);
    } catch (error) {
      console.error('Error fetching transactions:', error);
      setError('Failed to load transaction history');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getTransactionIcon = (type) => {
    switch (type) {
      case 'BUY_NEW':
        return '🆕';
      case 'BUY_ADD':
        return '➕';
      case 'SELL':
        return '💰';
      default:
        return '📊';
    }
  };

  const getTransactionDescription = (transaction) => {
    switch (transaction.type) {
      case 'BUY_NEW':
        return `Bought ${transaction.quantity} shares of ${transaction.symbol} (New Position)`;
      case 'BUY_ADD':
        return `Added ${transaction.quantity} shares of ${transaction.symbol} (Existing Position)`;
      case 'SELL':
        return `Sold ${transaction.quantity} shares of ${transaction.symbol}`;
      default:
        return `${transaction.type} ${transaction.quantity} shares of ${transaction.symbol}`;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="transaction-history-overlay">
      <div className="transaction-history-modal">
        <div className="transaction-history-header">
          <h2>Transaction History</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="transaction-history-content">
          <div className="cash-balance-info">
            <div className="cash-balance">
              <span className="label">Current Cash Balance:</span>
              <span className="amount">${cashBalance.toFixed(2)}</span>
            </div>
          </div>

          {isLoading ? (
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Loading transactions...</p>
            </div>
          ) : error ? (
            <div className="error-state">
              <p>⚠️ {error}</p>
              <button onClick={fetchTransactions} className="retry-button">
                Try Again
              </button>
            </div>
          ) : transactions.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📊</div>
              <h3>No Transactions Yet</h3>
              <p>Your transaction history will appear here after you buy or sell stocks.</p>
            </div>
          ) : (
            <div className="transactions-list">
              <div className="transactions-header">
                <span>Total Transactions: {transactions.length}</span>
              </div>
              
              {transactions.map((transaction) => (
                <div key={transaction.id} className="transaction-item">
                  <div className="transaction-icon">
                    {getTransactionIcon(transaction.type)}
                  </div>
                  
                  <div className="transaction-details">
                    <div className="transaction-main">
                      <span className="transaction-description">
                        {getTransactionDescription(transaction)}
                      </span>
                      <span className="transaction-amount">
                        ${transaction.total_amount.toFixed(2)}
                      </span>
                    </div>
                    
                    <div className="transaction-meta">
                      <span className="transaction-price">
                        @ ${transaction.price.toFixed(2)} per share
                      </span>
                      <span className="transaction-date">
                        {formatDate(transaction.timestamp)}
                      </span>
                    </div>
                    
                    <div className="transaction-balance">
                      Cash after: ${transaction.cash_balance_after.toFixed(2)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TransactionHistory; 