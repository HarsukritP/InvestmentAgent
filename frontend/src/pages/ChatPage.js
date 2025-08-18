import React, { useState, useEffect, useRef, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import axios from 'axios';
import './ChatPage.css';
import { API_URL } from '../config';
import { formatCurrency, formatPercentage } from '../utils/formatters';
import defaultAvatar from '../assets/default-avatar.js';
import assistantAvatar from '../assets/assistant-avatar.js';
import { useLocation } from 'react-router-dom';

const STORAGE_KEY = 'procogia_chat_history';

const ChatPage = ({ portfolio, user }) => {
  const location = useLocation();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [expandedFunctions, setExpandedFunctions] = useState({});
  const [activeFunctions, setActiveFunctions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(true);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const chatContainerRef = useRef(null);
  
  // Generate context-aware suggestions
  const generateSuggestions = useCallback(() => {
    const suggestions = [];
    
    // Portfolio-based suggestions
    if (portfolio && portfolio.holdings && portfolio.holdings.length > 0) {
      const topHolding = portfolio.holdings[0];
      const poorPerformers = portfolio.holdings.filter(h => 
        h.daily_change_percent && h.daily_change_percent < -2
      );
      const strongPerformers = portfolio.holdings.filter(h => 
        h.daily_change_percent && h.daily_change_percent > 3
      );
      
      suggestions.push(`How is my ${topHolding.symbol} performing?`);
      
      if (poorPerformers.length > 0) {
        suggestions.push(`Should I be concerned about ${poorPerformers[0].symbol}?`);
      }
      
      if (strongPerformers.length > 0) {
        suggestions.push(`Why is ${strongPerformers[0].symbol} doing so well?`);
      }
      
      suggestions.push("What's my portfolio's overall performance?");
      suggestions.push("Are there any rebalancing opportunities?");
    }
    
    // Financial analysis suggestions
    suggestions.push("Analyze Apple's financial health");
    suggestions.push("Compare Microsoft vs Google financials");
    suggestions.push("Show me Tesla's income statement");
    
    // General market suggestions
    suggestions.push("What are the latest market trends?");
    suggestions.push("Should I diversify my portfolio?");
    suggestions.push("What stocks are trending today?");
    
    // Chat history based suggestions
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage && lastMessage.role === 'assistant') {
        suggestions.push("Can you explain that in more detail?");
        suggestions.push("What should I do next?");
      }
    }
    
    // Return a mix of 4-6 relevant suggestions
    return suggestions.slice(0, Math.min(6, suggestions.length));
  }, [portfolio, messages]);

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

  // Handle suggestion click
  const handleSuggestionClick = (suggestion) => {
    setInputMessage(suggestion);
    setShowSuggestions(false);
    setTimeout(() => {
      handleSendMessage(suggestion);
    }, 100);
  };

  // Handle input change
  const handleInputChange = (e) => {
    setInputMessage(e.target.value);
    // Hide suggestions when user starts typing
    if (e.target.value.trim() && showSuggestions) {
      setShowSuggestions(false);
    }
  };

  // Handle key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Auto-resize textarea
  const handleTextareaResize = (e) => {
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
  };

  // Combined input change handler
  const handleInputChangeWithResize = (e) => {
    handleInputChange(e);
    handleTextareaResize(e);
  };
  
  // Load chat history from localStorage on mount
  useEffect(() => {
    const savedMessages = localStorage.getItem(STORAGE_KEY);
    
    if (savedMessages) {
      try {
        const parsedMessages = JSON.parse(savedMessages);
        
        // Only use saved messages if they exist and are in the correct format
        if (Array.isArray(parsedMessages) && parsedMessages.length > 0) {
          setMessages(parsedMessages);
          return; // Skip adding welcome message if we loaded history
        }
      } catch (error) {
        console.error('Error parsing saved chat history:', error);
        // If there's an error, we'll fall through to the default welcome message
      }
    }
    
    // Initialize with welcome message if no history was loaded
    const welcomeMessage = {
      role: 'assistant',
      content: `Hello! I'm your AI investment assistant. I can help you analyze your portfolio, understand market trends, and provide personalized investment insights based on real-time data.`,
      timestamp: new Date().toISOString()
    };
    setMessages([welcomeMessage]);
  }, []); // Only run once on mount
  
  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    }
  }, [messages]);

  // Handle prefilled message from navigation
  useEffect(() => {
    const prefilledMessage = location.state?.prefilledMessage;
    if (prefilledMessage) {
      setInputMessage(prefilledMessage);
      setShowSuggestions(false);
      // Focus the input field
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
      // Clear the navigation state to prevent re-filling on refresh
      window.history.replaceState({}, document.title);
    }
  }, [location.state]);

  // Handle transaction confirmation
  const handleTransactionConfirm = (confirmed, transactionDetails) => {
    if (confirmed) {
      // User confirmed the transaction, send confirmation message
      const confirmMessage = `Yes, please proceed with the transaction as described.`;
      setInputMessage(confirmMessage);
      handleSendMessage(confirmMessage);
    } else {
      // User declined the transaction
      const declineMessage = `No, please don't proceed with the transaction.`;
      setInputMessage(declineMessage);
      handleSendMessage(declineMessage);
    }
  };
  
  // Custom function to send a message programmatically
  const handleSendMessage = async (overrideMessage = null) => {
    const messageToSend = overrideMessage || inputMessage;
    
    if (!messageToSend.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: messageToSend.trim(),
      timestamp: new Date().toISOString()
    };

    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    // Clear active functions when sending a new message
    setActiveFunctions([]);

    try {
      // Prepare portfolio context
      const portfolioContext = portfolio ? {
        portfolio_value: portfolio.portfolio?.total_market_value || 0,
        cash_balance: portfolio.portfolio?.cash_balance || 0,
        holdings: portfolio.holdings || []
      } : null;

      // Prepare conversation history - only include role and content
      const conversationHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const response = await axios.post(`${API_URL}/chat`, {
        message: messageToSend.trim(),
        portfolio_context: portfolioContext,
        conversation_history: conversationHistory
      });

      // Process all function calls if available
      let functionContent = '';
      let allFunctionCalls = [];
      
      // Handle multiple function calls if available
      if (response.data.all_function_calls && response.data.all_function_calls.length > 0) {
        allFunctionCalls = response.data.all_function_calls;
        
        // Process each function call
        for (const funcCall of allFunctionCalls) {
          const formattedResponse = formatFunctionResponse(
            funcCall.name,
            funcCall.response
          );
          
          if (formattedResponse) {
            functionContent += formattedResponse + "\n\n";
          }
        }
      } 
      // Fallback to legacy single function call
      else if (response.data.function_called && response.data.function_response) {
        functionContent = formatFunctionResponse(
          response.data.function_called, 
          response.data.function_response
        );
        
        allFunctionCalls = [{
          name: response.data.function_called,
          response: response.data.function_response
        }];
      }

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString(),
        function_called: response.data.function_called,
        function_response: response.data.function_response,
        function_content: functionContent,
        all_function_calls: allFunctionCalls
      };

      setMessages(prev => [...prev, assistantMessage]);

      // If a trade occurred, trigger a portfolio refresh so UI reflects changes
      try {
        const tradeCall = allFunctionCalls.find(fc => fc.name === 'buy_stock' || fc.name === 'sell_stock');
        if (tradeCall && (tradeCall.response?.success || tradeCall.response?.transaction)) {
          // Fire-and-forget refresh for pages that rely on /portfolio
          axios.get('/portfolio').catch(() => {});
        }
      } catch (_) {}
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
      // setError(errorMessage); // This line was removed as per the edit hint
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
    }, 5000); // Increased to 5 seconds for better visibility

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
      case 'get_historical_prices':
        return formatHistoricalPrices(responseData);
      case 'get_cache_stats':
        return formatCacheStats(responseData);
      case 'get_market_context':
        return formatMarketContext(responseData);
      default:
        // For any unhandled function types, return a generic format
        return `Function ${functionName} result:\n${JSON.stringify(responseData, null, 2)}`;
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

  // Format historical prices data
  const formatHistoricalPrices = (data) => {
    if (data.error) return `Error: ${data.error}`;
    
    if (!data.prices || data.prices.length === 0) {
      return `No historical price data available for ${data.symbol || 'this stock'}.`;
    }
    
    // Get first and last price for comparison
    const firstPrice = data.prices[0];
    const lastPrice = data.prices[data.prices.length - 1];
    const priceChange = lastPrice.price - firstPrice.price;
    const percentChange = (priceChange / firstPrice.price) * 100;
    
    return `
📈 Historical Prices for ${data.symbol}:
• Period: ${data.days || 30} days
• First Price: $${firstPrice.price?.toFixed(2) || 0} (${new Date(firstPrice.date).toLocaleDateString()})
• Last Price: $${lastPrice.price?.toFixed(2) || 0} (${new Date(lastPrice.date).toLocaleDateString()})
• Change: ${priceChange >= 0 ? '+' : ''}$${priceChange.toFixed(2)} (${percentChange >= 0 ? '+' : ''}${percentChange.toFixed(2)}%)
• Data Points: ${data.prices.length}
`;
  };
  
  // Format cache stats
  const formatCacheStats = (data) => {
    if (data.error) return `Error: ${data.error}`;
    
    return `
🔄 Market Data Cache Stats:
• Total Cached Items: ${data.total_items || 0}
• Cache Hit Rate: ${data.hit_rate ? (data.hit_rate * 100).toFixed(1) + '%' : 'N/A'}
• Cache Size: ${data.cache_size_kb ? data.cache_size_kb.toFixed(2) + ' KB' : 'N/A'}
• Oldest Item Age: ${data.oldest_item_age || 'N/A'}
`;
  };

  const clearChat = () => {
    // Clear messages state
    setMessages([]);
    // setError(null); // This line was removed as per the edit hint
    
    // Clear localStorage
    localStorage.removeItem(STORAGE_KEY);
    
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

  // Render the active functions display
  const renderActiveFunctions = () => {
    if (activeFunctions.length === 0) return null;
    
    return (
      <div className="active-functions-container">
        {activeFunctions.map(func => (
          <div key={func.id} className="active-function-item">
            <span className="function-icon">
              {getFunctionIcon(func.name)}
            </span>
            <span className="function-name">
              Function called: <strong>{formatFunctionName(func.name)}</strong>
            </span>
          </div>
        ))}
      </div>
    );
  };
  
  // Get an appropriate icon for each function type
  const getFunctionIcon = (functionName) => {
    switch (functionName) {
      case 'get_portfolio_summary':
        return '📊';
      case 'get_stock_details':
      case 'search_stock':
        return '🔍';
      case 'buy_stock':
        return '💰';
      case 'sell_stock':
        return '💸';
      case 'calculate_portfolio_metrics':
        return '📈';
      case 'get_transaction_history':
        return '📝';
      case 'get_historical_prices':
        return '📅';
      case 'get_market_context':
        return '🌐';
      default:
        return '⚙️';
    }
  };
  
  // Format function name for display
  const formatFunctionName = (functionName) => {
    return functionName
      .replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase());
  };

  const renderMessage = (message, index) => {
    const isUser = message.role === 'user';
    
    // Function call display - show before the message content
    let functionCallDisplay = null;
    
    if (!isUser) {
      // Handle multiple function calls if available
      if (message.all_function_calls && message.all_function_calls.length > 0) {
        const validFunctions = message.all_function_calls.filter(funcCall => funcCall.name !== 'request_confirmation');
        
        functionCallDisplay = (
          <div className="function-calls-container">
            <div 
              className="function-calls-summary"
              onClick={() => toggleFunctionResponse(`${index}-summary`)}
            >
              <div className="function-summary-content">
                <span className="function-summary-triangle">
                  {expandedFunctions[`${index}-summary`] ? '▼' : '▶'}
                </span>
                <span className="function-summary-text">
                  Functions called ({validFunctions.length})
                </span>
              </div>
              
              <div className="function-calls-preview">
                {validFunctions.map((funcCall, funcIndex) => (
                  <span key={funcIndex} className="function-chip-mini">
                    <span className="function-chip-icon">{getFunctionIcon(funcCall.name)}</span>
                    {formatFunctionName(funcCall.name)}
                  </span>
                ))}
              </div>
            </div>
            
            {expandedFunctions[`${index}-summary`] && (
              <div className="function-calls-details">
                {validFunctions.map((funcCall, funcIndex) => (
                  <div className="function-call-display" key={funcIndex}>
                    <div 
                      className="function-call-header" 
                      onClick={() => toggleFunctionResponse(`${index}-${funcIndex}`)}
                    >
                      <span className="function-icon">{getFunctionIcon(funcCall.name)}</span>
                      <span className="function-name">
                        <strong>{formatFunctionName(funcCall.name)}</strong>
                      </span>
                      <span className="function-toggle">
                        {expandedFunctions[`${index}-${funcIndex}`] ? '▲' : '▼'}
                      </span>
                    </div>
                    {expandedFunctions[`${index}-${funcIndex}`] && (
                      <div className="function-response expanded">
                        <pre>{JSON.stringify(funcCall.response, null, 2)}</pre>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      }
      // Fallback for legacy single function call
      else if (message.function_called) {
        functionCallDisplay = (
          <div className="function-call-display">
            <div 
              className="function-call-header" 
              onClick={() => toggleFunctionResponse(index)}
            >
              <span className="function-icon">{getFunctionIcon(message.function_called)}</span>
              <span className="function-name">
                Function called: <strong>{formatFunctionName(message.function_called)}</strong>
              </span>
              <span className="function-toggle">
                {expandedFunctions[index] ? '▲' : '▼'}
              </span>
            </div>
            <div className={`function-response ${expandedFunctions[index] ? 'expanded' : ''}`}>
              <pre>{JSON.stringify(message.function_response, null, 2)}</pre>
            </div>
          </div>
        );
      }
    }
    
    // Check if this message needs transaction confirmation
    const hasConfirmationRequest = () => {
      if (!message.all_function_calls) return false;
      
      return message.all_function_calls.some(
        call => call.name === 'request_confirmation' && call.response?.confirmation_requested
      );
    };
    
    // Also check for text-based confirmation patterns as fallback
    const containsConfirmationRequest = (text) => {
      if (!text) return false;
      
      const patterns = [
        /would you like (me )?to proceed with this rebalancing/i,
        /would you like (me )?to proceed with this transaction/i,
        /would you like (me )?to execute this (trade|transaction)/i,
        /shall i proceed with (this|the) (trade|transaction)/i,
        /do you (want|wish) (me )?to (proceed|continue) with (this|the) (trade|transaction)/i,
        /confirm (this|the) (trade|transaction)/i,
        /please confirm if you('d| would) like to proceed/i,
        /confirm (if|that) you approve this plan/i,
        /please confirm (if|that) you approve/i,
        /confirm (this|the) (plan|action|strategy)/i,
        /let('s| us) confirm the execution of this plan/i
      ];
      
      return patterns.some(pattern => pattern.test(text));
    };
    
    const showConfirmation = !isUser && 
      index === messages.length - 1 && // Only show for the last message
      (hasConfirmationRequest() || containsConfirmationRequest(message.content)) && 
      !isLoading; // Don't show while loading
    
    return (
      <div 
        key={index} 
        className={`chat-message ${isUser ? 'user-message' : 'assistant-message'} ${message.isError ? 'error-message' : ''}`}
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
          
          <div className="message-text message-content-modern">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content || ''}</ReactMarkdown>
            {showConfirmation && <TransactionConfirmation message={message} />}
          </div>
          
          <div className="message-timestamp">
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    );
  };

  // Transaction confirmation component
  const TransactionConfirmation = ({ message }) => {
    // First try to get confirmation details from function call
    const getConfirmationDetails = () => {
      if (!message.all_function_calls) return null;
      
      const confirmationCall = message.all_function_calls?.find(
        call => call.name === 'request_confirmation' && call.response?.confirmation_requested
      );
      
      return confirmationCall ? confirmationCall.response : null;
    };
    
    // Extract action plan from text if no function call
    const extractActionPlanFromText = (text) => {
      if (!text) return null;
      
      // Look for common patterns that indicate a transaction plan
      const planPatterns = [
        /let('s| us) confirm the execution of this plan:\s*([\s\S]+?)(?=please confirm|$)/i,
        /strategic rebalancing plan outlined:\s*([\s\S]+?)(?=please confirm|$)/i,
        /here('s| is) the recommended strategy:\s*([\s\S]+?)(?=please confirm|$)/i,
        /recommended actions?:\s*([\s\S]+?)(?=please confirm|$)/i
      ];
      
      for (const pattern of planPatterns) {
        const match = text.match(pattern);
        if (match && match[1]) {
          return match[1].trim();
        }
      }
      
      // If no specific pattern matched, return a default message
      return "Execute the transaction as described above?";
    };
    
    const confirmationDetails = getConfirmationDetails();
    const actionPlan = confirmationDetails?.action_plan || extractActionPlanFromText(message.content);
    
    return (
      <div className="transaction-confirmation">
        <div className="confirmation-message">
          ⚠️ Transaction Confirmation Required
        </div>
        <div className="confirmation-plan">
          {actionPlan}
        </div>
        <div className="confirmation-buttons">
          <button 
            className="decline-button"
            onClick={() => handleTransactionConfirm(false)}
          >
            Decline
          </button>
          <button 
            className="confirm-button"
            onClick={() => handleTransactionConfirm(true)}
          >
            Execute Action
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="modern-chat-page">
      {/* Page Title */}
      <h1 className="page-title">AI Assistant</h1>

      {/* Active Functions Display */}
      {renderActiveFunctions()}

      {/* Main Chat Area */}
      <div className="chat-main-container" ref={chatContainerRef}>
        
        {/* Empty State / Welcome */}
        {messages.length <= 1 && (
          <div className="welcome-container">
            <div className="welcome-content">
              <div className="welcome-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                  <path d="m2 17 10 5 10-5"/>
                  <path d="m2 12 10 5 10-5"/>
                </svg>
              </div>
              <h2 className="welcome-title">Investment Intelligence</h2>
              <p className="welcome-description">
                Advanced portfolio analysis, market insights, and personalized investment strategies powered by AI.
              </p>
              
              {/* Context-aware suggestions */}
              {showSuggestions && (
                <div className="suggestions-grid">
                  <h3 className="suggestions-title">Try asking me:</h3>
                  <div className="suggestions-list">
                    {generateSuggestions().map((suggestion, index) => (
                      <button
                        key={index}
                        className="suggestion-card"
                        onClick={() => handleSuggestionClick(suggestion)}
                        disabled={isLoading}
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Messages Container */}
        {messages.length > 1 && (
          <div className="messages-container-modern">
            <div className="messages-scroll-area">
              {messages.map((message, index) => (
                <div key={index} className={`message-wrapper ${message.role}`}>
                  <div className="message-bubble">
                    <div className="message-content-modern">
                      {message.content}
                      {message.all_function_calls && message.all_function_calls.length > 0 && (
                        <div style={{ marginTop: '8px', border: '1px solid #e5e7eb', borderRadius: 8 }}>
                          <button
                            onClick={() => toggleFunctionResponse(`modern-${index}`)}
                            style={{
                              width: '100%',
                              textAlign: 'left',
                              background: '#f8fafc',
                              border: 'none',
                              padding: '8px 10px',
                              cursor: 'pointer',
                              borderBottom: expandedFunctions[`modern-${index}`] ? '1px solid #e5e7eb' : 'none',
                              borderRadius: expandedFunctions[`modern-${index}`] ? '8px 8px 0 0' : 8,
                              fontSize: 12,
                              color: '#374151'
                            }}
                          >
                            Functions called ({message.all_function_calls.length}) {expandedFunctions[`modern-${index}`] ? '▲' : '▼'}
                          </button>
                          {expandedFunctions[`modern-${index}`] && (
                            <div style={{ padding: '8px 10px', background: 'white', borderRadius: '0 0 8px 8px' }}>
                              {message.all_function_calls.map((fn, i) => (
                                <div key={i} style={{ marginBottom: 10 }}>
                                  <div style={{ fontWeight: 600, fontSize: 12, color: '#111827', marginBottom: 4 }}>
                                    {fn.name}
                                  </div>
                                  <pre style={{
                                    margin: 0,
                                    background: '#f9fafb',
                                    border: '1px solid #e5e7eb',
                                    borderRadius: 6,
                                    padding: 8,
                                    fontSize: 11,
                                    overflowX: 'auto'
                                  }}>{JSON.stringify(fn.response || fn.result, null, 2)}</pre>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                    <div className="message-meta">
                      <span className="message-time">
                        {new Date(message.timestamp).toLocaleTimeString([], { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
              
              {/* Loading Message */}
              {isLoading && (
                <div className="message-wrapper assistant">
                  <div className="message-bubble loading">
                    <div className="typing-indicator-modern">
                      <div className="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                      <span className="typing-text">AI is thinking...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </div>
        )}
      </div>

      {/* Input Area - Fixed at bottom */}
      <div className="input-area-modern">
        {/* Show suggestions when there are conversations and input is empty */}
        {messages.length > 1 && showSuggestions && !inputMessage.trim() && (
          <div className="quick-suggestions">
            {generateSuggestions().slice(0, 3).map((suggestion, index) => (
              <button
                key={index}
                className="quick-suggestion-chip"
                onClick={() => handleSuggestionClick(suggestion)}
                disabled={isLoading}
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}
        
        <div className="input-container-modern">
          <div className="input-wrapper">
            <textarea
              ref={inputRef}
              className="input-field-modern"
              placeholder="Ask about your portfolio, market trends, or investment strategies..."
              value={inputMessage}
              onChange={handleInputChangeWithResize}
              onKeyDown={handleKeyPress}
              disabled={isLoading}
              rows={1}
              style={{ height: 'auto', overflow: 'hidden' }}
            />
            <button
              className="send-button-modern"
              onClick={() => handleSendMessage()}
              disabled={!inputMessage.trim() || isLoading}
            >
              <div className="send-icon-modern">
                {isLoading ? (
                  <div className="spinner-small"></div>
                ) : (
                  <span>Send</span>
                )}
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage; 