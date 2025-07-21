# AI Portfolio Agent MVP

ProCogia's AI-powered portfolio management assistant that provides intelligent insights and real-time market analysis.

## 🚀 Quick Start

The application works in **demo mode** without API keys, but you'll get the full experience with real data by configuring the APIs below.

### 1. Clone and Setup

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies  
cd ../frontend
npm install
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```bash
# Copy the example configuration
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# AlphaVantage API Key (for real-time market data)
ALPHAVANTAGE_API_KEY=your_alphavantage_key_here

# Google Gemini API Key (for AI assistant functionality)  
GEMINI_API_KEY=your_gemini_key_here
```

### 3. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

Visit **http://localhost:3000** to use the application!

---

## 🔑 API Keys Setup

### AlphaVantage API (Real-time Market Data)

1. **Visit**: https://www.alphavantage.co/support/#api-key
2. **Sign up** for a free account (no credit card required)
3. **Get your API key** - Free tier includes:
   - 5 API requests per minute
   - 500 requests per day
   - Real-time stock quotes
4. **Add to .env**: `ALPHAVANTAGE_API_KEY=your_key_here`

**Without this key**: The app uses mock market data (AAPL: $175.23, GOOGL: $2634.50, MSFT: $347.89)

### Google Gemini API (AI Assistant)

1. **Visit**: https://makersuite.google.com/app/apikey
2. **Sign in** with your Google account
3. **Create new API key** (free tier available)
4. **Free tier includes**:
   - 60 requests per minute
   - No billing required for basic usage
   - Gemini Pro model access
5. **Add to .env**: `GEMINI_API_KEY=your_key_here`

**Estimated cost**: **FREE** for MVP testing and development with generous limits.

**Without this key**: AI assistant will show configuration message but portfolio data still works.

---

## 📊 Features

### Portfolio Analytics
- **Real-time market data** integration with AlphaVantage
- **Performance tracking** with P&L calculations
- **Hardcoded portfolio**: AAPL (10 shares), GOOGL (5 shares), MSFT (8 shares)
- **Auto-refresh** every 60 seconds
- **Professional ProCogia styling**

### AI Investment Assistant  
- **Natural language** portfolio queries powered by Google Gemini
- **Context-aware analysis** with real-time portfolio data
- **Smart insights** based on current market data
- **Conversation history** for context

### Try These AI Queries:
- "What's my portfolio performance?"
- "How is Apple doing?"
- "Should I be concerned about any holdings?"
- "Give me a portfolio summary"
- "What's my best performing stock?"

---

## 🛠 Technical Stack

**Backend:**
- FastAPI (Python web framework)
- AlphaVantage API integration
- Google Gemini Pro AI model
- In-memory caching for rate limits

**Frontend:**
- React 18 with hooks
- Axios for HTTP requests
- ProCogia design system
- Responsive CSS Grid layout

---

## 🎯 MVP Scope

This is a **minimal viable product** demonstrating:
- ✅ AI + Market Data + Portfolio Analysis integration
- ✅ Real-time stock quotes and portfolio calculations
- ✅ Professional ProCogia-branded interface
- ✅ Conversational AI with portfolio context
- ✅ Error handling and fallback data

**MVP Limitations:**
- Single hardcoded portfolio (no user accounts)
- No data persistence (resets on restart)
- Basic error handling
- Limited to 3 stocks (AAPL, GOOGL, MSFT)

---

## 🚨 Troubleshooting

### Backend won't start:
```bash
# Check Python version (needs 3.9+)
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Run directly
cd backend && python main.py
```

### Frontend won't start:
```bash
# Check Node version (needs 16+)
node --version

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm start
```

### API Issues:
- **AlphaVantage errors**: Check your API key and rate limits (5 requests/minute)
- **Gemini errors**: Verify API key is valid from Google AI Studio
- **CORS errors**: Make sure backend is running on port 8000

### Health Check:
Visit http://localhost:8000/health to see service status and configuration.

---

## 📈 Next Steps After MVP

The MVP provides a foundation for expanding to:
- User authentication and multiple portfolios
- Portfolio editing and trade simulation  
- Advanced charting and technical analysis
- News sentiment integration
- Risk assessment and optimization
- Real-time notifications
- Mobile responsiveness
- Database persistence

---

## 🎨 ProCogia Design System

The interface follows ProCogia's professional design standards:
- **Primary colors**: ProCogia blue (#1e40af)
- **Typography**: Clean, readable font hierarchy
- **Layout**: Two-column responsive grid
- **Components**: Professional cards and data tables
- **Status indicators**: Real-time data freshness
- **Loading states**: Smooth user experience

---

## 📞 Support

This MVP demonstrates the core concept of AI-powered portfolio management. The application works in demo mode without API keys and provides full functionality when properly configured.

For questions about extending this MVP or enterprise deployment, contact the ProCogia team. 

## Railway Deployment

For deploying this application to Railway with a custom domain, please refer to the following guides:

- [Railway Deployment Guide](docs/railway-deployment-guide.md) - Step-by-step instructions for deploying to Railway
- [Railway Environment Variables](docs/railway-env-variables.md) - List of required environment variables
- [Railway README](docs/README.railway.md) - Additional Railway-specific information

The application is designed to be deployed as two separate services on Railway:
1. Backend service (FastAPI)
2. Frontend service (React)

Both services can be deployed from the same GitHub repository by specifying different root directories.

### Custom Domain Setup

This application can be configured to run on a custom domain. For detailed instructions on setting up the custom domain `portfolioagent.procogia.ai`, see the [Railway Deployment Guide](docs/railway-deployment-guide.md). 

## Documentation

All project documentation is available in the [docs](docs/) folder:

- [Project Documentation](docs/README.md) - Index of all documentation
- [MVP Specification](docs/mvp.md) - Details about the Minimum Viable Product
- [Deployment Guides](docs/railway-deployment-guide.md) - Instructions for deploying to Railway 