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
  const [pendingConfirmation, setPendingConfirmation] = useState(null);
  const [expandedFunctions, setExpandedFunctions] = useState({});
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load conversation history from localStorage on component mount
  useEffect(() => {
    const savedMessages = localStorage.getItem('chatMessages');
    if (savedMessages) {
      try {
        setMessages(JSON.parse(savedMessages));
      } catch (e) {
        console.error('Failed to parse saved messages:', e);
      }
    }
  }, []);

  // Save conversation history to localStorage when messages change
  useEffect(() => {
    if (messages.length > 1) { // Only save if there's more than the initial message
      localStorage.setItem('chatMessages', JSON.stringify(messages));
    }
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim() && !pendingConfirmation) return;
    if (isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setError(null);

    // Add user message to conversation if there's input
    if (userMessage) {
      const newUserMessage = {
        role: 'user',
        content: userMessage,
        timestamp: new Date().toLocaleTimeString()
      };
      
      setMessages(prev => [...prev, newUserMessage]);
    }
    
    setIsLoading(true);

    try {
      // Prepare conversation history for API (last 15 messages for context)
      const conversationHistory = messages.slice(-15).map(msg => ({
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
          function_called: response.data.function_called,
          all_function_calls: response.data.all_function_calls || []
        };
        
        // Check if any function call is requesting confirmation
        const confirmationRequest = assistantMessage.all_function_calls?.find(
          call => call.name === 'request_confirmation' && call.response?.confirmation_requested
        );
        
        if (confirmationRequest) {
          setPendingConfirmation({
            action_plan: confirmationRequest.response.action_plan,
            details: confirmationRequest.response.details
          });
        } else {
          setPendingConfirmation(null);
        }
        
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
      setPendingConfirmation(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirmation = async (confirmed) => {
    if (!pendingConfirmation) return;
    
    const confirmationMessage = {
      role: 'user',
      content: confirmed ? 'I confirm this action. Please proceed.' : 'I decline this action. Let\'s discuss alternatives.',
      timestamp: new Date().toLocaleTimeString()
    };
    
    setMessages(prev => [...prev, confirmationMessage]);
    setPendingConfirmation(null);
    
    // If confirmed, send the confirmation message to continue the conversation
    if (confirmed) {
      setInputMessage('');
      await sendMessage({ preventDefault: () => {} });
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
    setPendingConfirmation(null);
    localStorage.removeItem('chatMessages');
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

  const toggleFn = (key) => {
    setExpandedFunctions(prev => ({ ...prev, [key]: !prev[key] }));
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
                  {message.all_function_calls && message.all_function_calls.length > 0 && (
                    <div style={{ marginTop: '8px', border: '1px solid #e5e7eb', borderRadius: 8 }}>
                      <button
                        onClick={() => toggleFn(`fn-${index}`)}
                        style={{
                          width: '100%',
                          textAlign: 'left',
                          background: '#f8fafc',
                          border: 'none',
                          padding: '8px 10px',
                          cursor: 'pointer',
                          borderBottom: expandedFunctions[`fn-${index}`] ? '1px solid #e5e7eb' : 'none',
                          borderRadius: expandedFunctions[`fn-${index}`] ? '8px 8px 0 0' : 8,
                          fontSize: 12,
                          color: '#374151'
                        }}
                      >
                        Functions called ({message.all_function_calls.length}) {expandedFunctions[`fn-${index}`] ? '▲' : '▼'}
                      </button>
                      {expandedFunctions[`fn-${index}`] && (
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
            
            {pendingConfirmation && (
              <div className="message assistant confirmation-request">
                <div className="message-content">
                  <div style={{ 
                    padding: '10px',
                    marginTop: '10px',
                    backgroundColor: '#f0f9ff',
                    borderRadius: '8px',
                    border: '1px solid #bae6fd'
                  }}>
                    <h4 style={{ margin: '0 0 10px 0', color: '#0369a1' }}>Action Confirmation Required</h4>
                    <p style={{ margin: '0 0 15px 0' }}>{pendingConfirmation.action_plan}</p>
                    
                    <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                      <button
                        onClick={() => handleConfirmation(false)}
                        style={{
                          padding: '8px 16px',
                          background: '#f1f5f9',
                          border: '1px solid #cbd5e1',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          color: '#64748b'
                        }}
                      >
                        Decline
                      </button>
                      <button
                        onClick={() => handleConfirmation(true)}
                        style={{
                          padding: '8px 16px',
                          background: '#0ea5e9',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          color: 'white',
                          fontWeight: 'bold'
                        }}
                      >
                        Execute Action
                      </button>
                    </div>
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
                disabled={isLoading || (!inputMessage.trim() && !pendingConfirmation)}
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