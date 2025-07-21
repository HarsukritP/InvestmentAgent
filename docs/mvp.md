# AI Portfolio Agent - MVP Requirements

## MVP Overview
A minimal viable product demonstrating the core concept: an AI assistant that can analyze a simple portfolio and answer questions using real-time market data. Focus on proving the integration between LLM, market data API, and portfolio analysis.

## Core MVP Goals
- **Prove the concept**: Demonstrate AI + market data + portfolio analysis working together
- **Minimal complexity**: Single user, hardcoded portfolio, essential features only
- **Quick development**: Achievable in 1-2 weeks
- **Foundation for expansion**: Clean architecture that can be extended

## MVP Feature Set

### 1. Hardcoded Portfolio
- **No user management**: Single hardcoded portfolio in the backend
- **Simple holdings**: 3-5 stocks (e.g., AAPL, GOOGL, MSFT, TSLA, NVDA)
- **Basic data**: Symbol, quantity, purchase price
- **Example portfolio**:
  ```json
  {
    "holdings": [
      {"symbol": "AAPL", "quantity": 10, "purchase_price": 150.00},
      {"symbol": "GOOGL", "quantity": 5, "purchase_price": 2500.00},
      {"symbol": "MSFT", "quantity": 8, "purchase_price": 300.00}
    ],
    "cash_balance": 5000.00
  }
  ```

### 2. Market Data Integration
- **AlphaVantage API**: Real-time stock quotes only
- **Single endpoint**: `GLOBAL_QUOTE` for current prices
- **Basic caching**: 5-minute cache to handle rate limits
- **Essential data**: Current price, change, change percentage

### 3. AI Chat Interface
- **OpenAI GPT integration**: Simple chat completion API
- **Pre-defined functions**:
  - `get_portfolio_value()` - Calculate total portfolio worth
  - `get_stock_performance(symbol)` - Individual stock P&L
  - `get_portfolio_summary()` - Overview of all holdings
- **Basic prompting**: System prompt with portfolio context
- **Simple responses**: Text-based answers, no complex formatting

### 4. Minimal Web Interface
- **Single page application**: Everything on one page
- **Two main sections**:
  - **Portfolio Display**: Simple table showing holdings and current values
  - **Chat Interface**: Basic chat UI with message history
- **No authentication**: Direct access to the application
- **Basic styling**: Clean but minimal CSS

## Technical Stack (Simplified)

### Backend
- **FastAPI**: Single `main.py` file
- **No database**: In-memory data storage
- **Libraries**:
  - `fastapi`
  - `requests` (for API calls)
  - `openai` (for LLM)
  - `uvicorn` (server)

### Frontend
- **Plain React**: No TypeScript, minimal complexity
- **Single component structure**: App.js with inline components
- **Styling**: Basic CSS or simple CSS framework
- **Libraries**:
  - `react`
  - `axios` (HTTP requests)

### Environment
- **Local development only**: No deployment considerations
- **Environment variables**: `.env` file for API keys

## MVP API Structure

### Backend Endpoints
```
GET  /portfolio        - Get current portfolio with live prices
POST /chat            - Send message to AI, get response
GET  /health          - Basic health check
```

### Function Definitions for LLM
```python
functions = [
    {
        "name": "get_portfolio_value",
        "description": "Get the total current value of the portfolio",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "get_stock_performance", 
        "description": "Get performance data for a specific stock",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Stock symbol"}
            },
            "required": ["symbol"]
        }
    }
]
```

## MVP User Stories

### As a user, I want to:
1. **See my portfolio**: View my holdings with current prices and values
2. **Ask about total value**: "What's my portfolio worth?"
3. **Ask about individual stocks**: "How is Apple performing?"
4. **Get simple insights**: "Which stock is my best performer?"
5. **Ask basic questions**: "Should I be worried about any of my holdings?"

## MVP Success Criteria
- [ ] Portfolio displays with real-time prices from AlphaVantage
- [ ] AI chat responds to portfolio questions using function calls
- [ ] Portfolio calculations are accurate (total value, P&L)
- [ ] Chat interface works smoothly with message history
- [ ] Application runs locally without errors
- [ ] Basic error handling for API failures

## Development Timeline

### Week 1: Backend Foundation
- **Day 1-2**: FastAPI setup, AlphaVantage integration
- **Day 3-4**: OpenAI integration with function calling
- **Day 5**: Portfolio logic and API endpoints

### Week 2: Frontend & Integration
- **Day 1-2**: React app setup, portfolio display
- **Day 3-4**: Chat interface implementation
- **Day 5**: Integration testing and bug fixes

## File Structure
```
portfolio-agent-mvp/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── portfolio.py         # Portfolio logic
│   ├── market_data.py       # AlphaVantage integration
│   ├── ai_agent.py          # OpenAI integration
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── Portfolio.js    # Portfolio display
│   │   ├── Chat.js         # Chat interface
│   │   └── App.css         # Basic styling
│   ├── package.json        # Node dependencies
│   └── public/
└── .env                    # API keys
```

## Required API Keys
- **AlphaVantage**: Free tier (5 API requests/minute, 500/day)
- **OpenAI**: Pay-per-use (estimated $5-10 for MVP development)

## MVP Limitations & Future Enhancements
### Current Limitations:
- Single hardcoded portfolio
- No user accounts or persistence
- Basic error handling
- Minimal UI styling
- Limited AI functions

### Immediate Next Steps After MVP:
- Add portfolio editing capabilities
- Implement data persistence
- Add more sophisticated AI functions
- Improve UI/UX design
- Add user authentication

## Risk Mitigation for MVP
- **API Rate Limits**: Basic caching and error messages
- **API Costs**: Monitor OpenAI usage, use shorter prompts
- **Development Time**: Focus only on core features, no extras
- **Technical Issues**: Keep dependencies minimal, well-documented setup

This MVP focuses on proving the core concept with minimal complexity while providing a solid foundation for future development. 