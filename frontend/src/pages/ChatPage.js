import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './ChatPage.css';
import { API_URL } from '../config';
import defaultAvatar from '../assets/default-avatar.js';
import assistantAvatar from '../assets/assistant-avatar.js';

const ChatPage = ({ portfolio, user }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedFunctions, setExpandedFunctions] = useState({});
  const [activeFunctions, setActiveFunctions] = useState([]);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  
  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  // Scroll when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  // Focus input when loading state changes
  useEffect(() => {
    if (!isLoading) {
      inputRef.current?.focus();
    }
  }, [isLoading]);
  
  // Initialize with welcome message
  useEffect(() => {
    const welcomeMessage = {
      role: 'assistant',
      content: `👋 Hello! I'm your AI investment assistant. How can I help you today?`,
      timestamp: new Date().toISOString()
    };
    setMessages([welcomeMessage]);
  }, []); // Only run once on mount

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString()
    };

    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);
    // Clear active functions when sending a new message
    setActiveFunctions([]);

    try {
      // Prepare portfolio context
      const portfolioContext = portfolio ? {
        portfolio_value: portfolio.portfolio?.total_market_value || 0,
        cash_balance: portfolio.portfolio?.cash_balance || 0,
        holdings: portfolio.holdings || []
      } : null;

      const response = await axios.post(`${API_URL}/chat`, {
        message: userMessage.content,
        portfolio_context: portfolioContext
      });

      // Handle function call data if present
      let functionContent = '';
      if (response.data.function_called && response.data.function_response) {
        functionContent = formatFunctionResponse(
          response.data.function_called, 
          response.data.function_response
        );
      }

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString(),
        function_called: response.data.function_called,
        function_response: response.data.function_response,
        function_content: functionContent
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      
      let errorMessage = 'Sorry, I encountered an error. Please try again.';
      
      if (error.response?.status === 503) {
        errorMessage = '🤖 AI Assistant is currently unavailable. This might be due to missing API configuration.';
      } else if (error.response?.data?.detail) {
        errorMessage = `Error: ${error.response.data.detail}`;
      }

      const errorResponse = {
        role: 'assistant',
        content: errorMessage,
        timestamp: new Date().toISOString(),
        isError: true
      };

      setMessages(prev => [...prev, errorResponse]);
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Add a function to track active functions
  const addActiveFunction = (functionName, args = {}) => {
    const functionCall = {
      name: functionName,
      args: args,
      timestamp: new Date().toISOString(),
      id: Date.now() + Math.random().toString(36).substring(2, 9)
    };
    
    setActiveFunctions(prev => [...prev, functionCall]);
    return functionCall.id;
  };

  // Remove function from active functions
  const removeActiveFunction = (functionId) => {
    setActiveFunctions(prev => prev.filter(func => func.id !== functionId));
  };

  // Format function response data for display
  const formatFunctionResponse = (functionName, responseData) => {
    if (!responseData) return '';

    // Add function to active functions when it's called
    const functionId = addActiveFunction(functionName, responseData);
    
    // Remove function from active functions after a delay
    setTimeout(() => {
      removeActiveFunction(functionId);
    }, 3000);

    switch (functionName) {
      case 'get_portfolio_summary':
        return formatPortfolioSummary(responseData);
      case 'get_stock_details':
        return formatStockDetails(responseData);
      case 'search_stock':
        return formatStockSearch(responseData);
      case 'buy_stock':
        return formatBuyStock(responseData);
      case 'sell_stock':
        return formatSellStock(responseData);
      case 'calculate_portfolio_metrics':
        return formatPortfolioMetrics(responseData);
      case 'get_transaction_history':
        return formatTransactionHistory(responseData);
      case 'get_market_context':
        return formatMarketContext(responseData);
      default:
        return JSON.stringify(responseData, null, 2);
    }
  };

  const formatPortfolioSummary = (data) => {
    if (data.error) return `Error: ${data.error}`;
    
    const summary = data.portfolio_summary;
    if (!summary) return 'No portfolio summary available';

    return `
📊 Portfolio Summary:
• Total Value: $${summary.total_portfolio_value?.toLocaleString() || 0}
• Total P&L: $${summary.total_pnl?.toLocaleString() || 0} (${summary.total_pnl_percent?.toFixed(2) || 0}%)
• Cash Balance: $${summary.cash_balance?.toLocaleString() || 0}
• Total Account Value: $${summary.total_account_value?.toLocaleString() || 0}
`;
  };

  const formatStockDetails = (data) => {
    if (data.error) return `Error: ${data.error}`;
    
    return `
📈 ${data.symbol || 'Stock'} Details:
• Shares Owned: ${data.shares_owned || 0}
• Purchase Price: $${data.purchase_price?.toFixed(2) || 0}
• Current Price: $${data.current_price?.toFixed(2) || 0}
• Current Value: $${data.current_value?.toLocaleString() || 0}
• P&L: $${data.pnl?.toLocaleString() || 0} (${data.pnl_percent?.toFixed(2) || 0}%)
`;
  };

  const formatStockSearch = (data) => {
    if (data.error) return `Error: ${data.error}`;
    if (!data.results || data.results.length === 0) return 'No stocks found matching your search.';

    let result = '🔍 Search Results:\n';
    data.results.forEach((stock, index) => {
      result += `${index + 1}. ${stock.symbol} - ${stock.name || 'N/A'}`;
      if (stock.current_price) result += ` ($${stock.current_price})`;
      result += '\n';
    });

    return result;
  };

  const formatPortfolioMetrics = (data) => {
    if (data.error) return `Error: ${data.error}`;
    
    let sectorInfo = '';
    if (data.sector_distribution) {
      sectorInfo = '\nSector Distribution:\n';
      Object.entries(data.sector_distribution).forEach(([sector, info]) => {
        sectorInfo += `• ${sector}: ${info.percentage?.toFixed(2) || 0}%\n`;
      });
    }

    return `
📊 Portfolio Metrics:
• Diversification Score: ${data.diversification_score || 0}/100
• Risk Level: ${data.risk_level || 'N/A'}
• Concentration Risk: ${data.concentration_risk || 'N/A'}
${sectorInfo}
`;
  };

  const formatTransactionHistory = (data) => {
    if (data.error) return `Error: ${data.error}`;
    if (!data.transactions || data.transactions.length === 0) return 'No transaction history available.';

    let result = '📜 Recent Transactions:\n';
    data.transactions.forEach((tx, index) => {
      const date = new Date(tx.timestamp).toLocaleDateString();
      result += `${index + 1}. ${date} - ${tx.type} ${tx.symbol}: ${tx.quantity} shares @ $${tx.price?.toFixed(2) || 0}\n`;
    });

    return result;
  };

  const formatBuyStock = (data) => {
    if (data.error) {
      let errorMsg = `Error: ${data.error}`;
      if (data.suggestions && data.suggestions.length > 0) {
        errorMsg += `\nDid you mean one of these symbols? ${data.suggestions.join(', ')}`;
      }
      return errorMsg;
    }
    
    if (!data.success) {
      let message = `Could not complete purchase: ${data.error || "Unknown error"}`;
      if (data.affordability) {
        message += `\nCash balance: $${data.affordability.cash_balance?.toFixed(2) || 0}`;
        message += `\nTotal cost: $${data.affordability.total_cost?.toFixed(2) || 0}`;
        message += `\nMax affordable shares: ${data.affordability.max_affordable_shares || 0}`;
      }
      return message;
    }
    
    let stockName = '';
    if (data.stock_info && data.stock_info.name) {
      stockName = ` (${data.stock_info.name})`;
    }
    
    return `
💰 Purchase Executed:
• Symbol: ${data.symbol}${stockName}
• Shares: ${data.quantity}
• Price: $${data.price?.toFixed(2) || 0}/share
• Total Cost: $${data.total_cost?.toFixed(2) || 0}
• New Cash Balance: $${data.new_cash_balance?.toFixed(2) || 0}
• Transaction ID: ${data.transaction_id || "N/A"}
`;
  };

  const formatSellStock = (data) => {
    if (data.error) return `Error: ${data.error}`;
    if (!data.success) {
      let message = `Could not complete sale: ${data.error || "Unknown error"}`;
      if (data.available_shares !== undefined) {
        message += `\nAvailable shares: ${data.available_shares}`;
      }
      return message;
    }
    
    return `
💸 Sale Executed:
• Symbol: ${data.symbol}
• Shares: ${data.quantity}
• Price: $${data.price?.toFixed(2) || 0}/share
• Total Proceeds: $${data.total_proceeds?.toFixed(2) || 0}
• New Cash Balance: $${data.new_cash_balance?.toFixed(2) || 0}
• Transaction ID: ${data.transaction_id || "N/A"}
`;
  };

  const formatMarketContext = (data) => {
    if (data.error) return `Error: ${data.error}`;
    
    let result = '🌍 Market Context:\n';
    
    // Add market sentiment if available
    if (data.market_sentiment) {
      const sentiment = data.market_sentiment;
      result += `• Market Sentiment: ${sentiment.sentiment_category.replace('_', ' ')}\n`;
      result += `• Sentiment Score: ${sentiment.sentiment_score}\n`;
      
      if (sentiment.sentiment_factors && sentiment.sentiment_factors.length > 0) {
        result += '\nKey Factors:\n';
        sentiment.sentiment_factors.forEach(factor => {
          result += `• ${factor}\n`;
        });
      }
      
      if (sentiment.economic_indicators_summary) {
        result += `\nEconomic Indicators: ${sentiment.economic_indicators_summary}\n`;
      }
    }
    
    // Add news if available
    if (data.market_news && data.market_news.general_news) {
      const news = data.market_news.general_news.slice(0, 3);
      if (news.length > 0) {
        result += '\nRecent News:\n';
        news.forEach((item, index) => {
          result += `• ${item.title} (${item.source})\n`;
        });
      }
    }
    
    return result;
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
    // Re-add welcome message
    const welcomeMessage = {
      role: 'assistant',
      content: `👋 Hello! I'm your AI investment assistant. How can I help you today?`,
      timestamp: new Date().toISOString()
    };
    setMessages([welcomeMessage]);
  };

  const getPortfolioSummary = () => {
    if (!portfolio || !portfolio.portfolio) {
      return 'No portfolio data available';
    }

    const portfolioValue = portfolio.portfolio.total_market_value || 0;
    const cashBalance = portfolio.portfolio.cash_balance || 0;
    const holdingsCount = portfolio.holdings?.length || 0;

    return `Portfolio: ${portfolioValue.toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD'
    })} • Cash: ${cashBalance.toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD'
    })} • ${holdingsCount} position${holdingsCount !== 1 ? 's' : ''}`;
  };

  const toggleFunctionResponse = (index) => {
    setExpandedFunctions(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const renderMessage = (message, index) => {
    const isUser = message.role === 'user';
    
    // Function call display - show before the message content
    const functionCallDisplay = !isUser && message.function_called ? (
      <div className="function-call-display">
        <div className="function-call-header" onClick={() => toggleFunctionResponse(index)}>
          <span className="function-icon">🔍</span>
          <span className="function-name">
            Function called: <strong>{message.function_called}</strong>
          </span>
          <span className="function-toggle">
            {expandedFunctions[index] ? '▲' : '▼'}
          </span>
        </div>
        <div className={`function-response ${expandedFunctions[index] ? 'expanded' : ''}`}>
          <pre>{JSON.stringify(message.function_response, null, 2)}</pre>
        </div>
      </div>
    ) : null;
    
    return (
      <div 
        key={index} 
        className={`chat-message ${isUser ? 'user-message' : 'assistant-message'}`}
      >
        <div className="message-avatar">
          <img 
            src={isUser ? (user?.picture || defaultAvatar) : assistantAvatar} 
            alt={isUser ? "User" : "AI Assistant"}
          />
        </div>
        <div className="message-content">
          {/* Show function call before message content */}
          {functionCallDisplay}
          
          <div className="message-text">
            {message.content}
          </div>
          
          <div className="message-timestamp">
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="chat-page">
      {/* Page Header */}
      <h1 className="page-title">AI Assistant</h1>
      
      <div className="header-actions">
        <div className="portfolio-summary-badge">
          {getPortfolioSummary()}
        </div>
        <button 
          className="clear-chat-btn"
          onClick={clearChat}
          title="Clear conversation"
        >
          <span className="btn-icon">🗑️</span>
          Clear Chat
        </button>
      </div>

      {/* Active Functions Display */}
      {activeFunctions.length > 0 && (
        <div className="active-functions-container">
          {activeFunctions.map(func => (
            <div key={func.id} className="active-function-item">
              <span className="function-icon">🔍</span>
              <span className="function-name">{func.name}</span>
            </div>
          ))}
        </div>
      )}

      {/* Chat Container */}
      <div className="chat-container">
        {/* Messages Area */}
        <div className="messages-area">
          <div className="messages-list">
            {messages.map((message, index) => 
              renderMessage(message, index)
            )}
            
            {/* Loading indicator */}
            {isLoading && (
              <div className="chat-message assistant-message">
                <div className="message-avatar">
                  <img src={assistantAvatar} alt="AI Assistant" />
                </div>
                <div className="message-content">
                  <div className="message-text">
                    <div className="typing-indicator">
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                    </div>
                  </div>
                  <div className="message-timestamp">Thinking...</div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="input-area">
          <div className="input-container">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about your portfolio, market trends, or investment strategies..."
              className="message-input"
              rows="1"
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="send-button"
              title="Send message (Enter)"
            >
              <span className="send-icon">
                {isLoading ? '⏳' : '📤'}
              </span>
            </button>
          </div>
          
          {/* Quick Actions */}
          <div className="quick-actions">
            <button 
              className="quick-action-btn"
              onClick={() => setInputMessage("How is my portfolio performing?")}
              disabled={isLoading}
            >
              Portfolio Performance
            </button>
            <button 
              className="quick-action-btn"
              onClick={() => setInputMessage("What are my biggest holdings?")}
              disabled={isLoading}
            >
              Top Holdings
            </button>
            <button 
              className="quick-action-btn"
              onClick={() => setInputMessage("Should I diversify more?")}
              disabled={isLoading}
            >
              Diversification Advice
            </button>
            <button 
              className="quick-action-btn"
              onClick={() => setInputMessage("What's the market outlook?")}
              disabled={isLoading}
            >
              Market Outlook
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage; 