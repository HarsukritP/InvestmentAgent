import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const Chat = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI Portfolio Assistant. I can help you analyze your portfolio performance, understand individual stock performance, and provide investment insights based on real-time market data.\n\nTry asking me:\n• "What\'s my portfolio performance?"\n• "How is Apple doing?"\n• "Should I be concerned about any holdings?"\n• "Give me a portfolio summary"',
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setError(null);

    // Add user message to conversation
    const newUserMessage = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toLocaleTimeString()
    };
    
    setMessages(prev => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      // Prepare conversation history for API (last 10 messages for context)
      const conversationHistory = messages.slice(-10).map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const response = await axios.post('/chat', {
        message: userMessage,
        conversation_history: conversationHistory
      });

      if (response.data.success) {
        const assistantMessage = {
          role: 'assistant',
          content: response.data.response,
          timestamp: new Date().toLocaleTimeString(),
          function_called: response.data.function_called
        };
        
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error(response.data.error || 'Failed to get AI response');
      }
    } catch (err) {
      console.error('Chat error:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Sorry, I encountered an error processing your message.';
      
      setError(errorMessage);
      
      const errorResponse = {
        role: 'assistant',
        content: `I'm sorry, I encountered an error: ${errorMessage}\n\nPlease try again or rephrase your question.`,
        timestamp: new Date().toLocaleTimeString(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearConversation = () => {
    setMessages([
      {
        role: 'assistant',
        content: 'Conversation cleared. How can I help you with your portfolio analysis?',
        timestamp: new Date().toLocaleTimeString()
      }
    ]);
    setError(null);
  };

  const formatMessage = (content) => {
    // Simple formatting for better readability
    return content.split('\n').map((line, index) => (
      <React.Fragment key={index}>
        {line}
        {index < content.split('\n').length - 1 && <br />}
      </React.Fragment>
    ));
  };

  return (
    <div className="card">
      <div className="card-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 className="card-title">🤖 AI Investment Assistant</h2>
            <p className="card-subtitle">
              Intelligent portfolio analysis and insights
            </p>
          </div>
          <button
            onClick={clearConversation}
            style={{
              padding: '0.5rem 1rem',
              background: 'transparent',
              border: '1px solid var(--card-border)',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '12px',
              color: 'var(--text-secondary)'
            }}
          >
            Clear Chat
          </button>
        </div>
      </div>
      
      <div className="card-content" style={{ padding: 0 }}>
        <div className="chat-container">
          <div className="chat-messages">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`message ${message.role}`}
                style={{
                  opacity: message.isError ? 0.8 : 1,
                  borderLeft: message.isError ? '3px solid var(--error-red)' : 'none'
                }}
              >
                <div className="message-content">
                  {formatMessage(message.content)}
                </div>
                <div className="message-timestamp">
                  {message.timestamp}
                  {message.function_called && (
                    <span style={{ marginLeft: '0.5rem', fontSize: '11px', opacity: 0.7 }}>
                      • Used {message.function_called}
                    </span>
                  )}
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="message assistant">
                <div className="message-content">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div className="spinner" style={{ width: '16px', height: '16px' }}></div>
                    <span>AI is analyzing your request...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          <div className="chat-input-container">
            {error && (
              <div style={{
                background: '#fef2f2',
                border: '1px solid #fecaca',
                color: '#dc2626',
                padding: '0.5rem',
                borderRadius: '6px',
                marginBottom: '0.5rem',
                fontSize: '14px'
              }}>
                ⚠️ {error}
              </div>
            )}
            
            <form onSubmit={sendMessage} className="chat-input-form">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask me about your portfolio performance, individual stocks, or investment insights..."
                className="chat-input"
                disabled={isLoading}
                maxLength={500}
              />
              <button
                type="submit"
                className="chat-button"
                disabled={isLoading || !inputMessage.trim()}
              >
                {isLoading ? 'Sending...' : 'Analyze 🔍'}
              </button>
            </form>
            
            <div style={{
              fontSize: '12px',
              color: 'var(--text-light)',
              marginTop: '0.5rem',
              textAlign: 'center'
            }}>
              💡 Try: "Portfolio summary", "How is AAPL doing?", "What's my best performer?"
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat; 