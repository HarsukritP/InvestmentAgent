# AI Portfolio Agent - MVP Design Layout (ProCogia Style)

## Overall Page Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  [ProCogia Logo]                     AI Portfolio Agent                     │
│  Data-Driven Investment Intelligence               MVP Demo                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────┐  ┌─────────────────────────────────┐ │
│  │                                     │  │                                 │ │
│  │          PORTFOLIO ANALYTICS        │  │         AI ASSISTANT            │ │
│  │                                     │  │                                 │ │
│  │  ┌─────────────────────────────────┐ │  │  ┌─────────────────────────────┐ │ │
│  │  │ Holdings Dashboard              │ │  │  │                             │ │ │
│  │  │                                 │ │  │  │      Conversation           │ │ │
│  │  │ Symbol │ Qty │ Entry │ Current  │ │  │  │                             │ │ │
│  │  │ AAPL   │ 10  │ $150  │ $175  ↗ │ │  │  │  💼 User: Portfolio summary? │ │ │
│  │  │ GOOGL  │ 5   │ $2500 │ $2600 ↗ │ │  │  │  🤖 AI: Your portfolio...   │ │ │
│  │  │ MSFT   │ 8   │ $300  │ $350  ↗ │ │  │  │  💼 User: Apple performance? │ │ │
│  │  │                                 │ │  │  │  🤖 AI: AAPL gained 16.7%  │ │ │
│  │  └─────────────────────────────────┘ │  │  │                             │ │ │
│  │                                     │  │  └─────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────┐ │  │                                 │ │
│  │  │ 📊 Performance Metrics          │ │  │  ┌─────────────────────────────┐ │ │
│  │  │                                 │ │  │  │                             │ │ │
│  │  │ 💰 Total Value: $XX,XXX.XX      │ │  │  │  Ask about your portfolio   │ │ │
│  │  │ 📈 P&L: +$X,XXX.XX (+X.X%)     │ │  │  │                             │ │ │
│  │  │ 💵 Cash: $5,000.00              │ │  │  └─────────────────────────────┘ │ │
│  │  │ 🕐 Updated: Real-time           │ │  │                    [Send] ──────┘ │ │
│  │  └─────────────────────────────────┘ │  │                                 │ │
│  │                                     │  │                                 │ │
│  └─────────────────────────────────────┘  └─────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Mobile/Responsive Layout (Stacked)

```
┌─────────────────────────────────┐
│    [ProCogia Logo]              │
│    AI Portfolio Agent           │
├─────────────────────────────────┤
│                                 │
│  ┌─────────────────────────────┐ │
│  │   📊 PORTFOLIO ANALYTICS    │ │
│  │                             │ │
│  │  Holdings Dashboard:        │ │
│  │  ┌─────────────────────────┐ │ │
│  │  │ AAPL  │ 10 │ $150→$175 ↗│ │ │
│  │  │ GOOGL │ 5  │ $2500→$2600↗│ │ │
│  │  │ MSFT  │ 8  │ $300→$350 ↗│ │ │
│  │  └─────────────────────────┘ │ │
│  │                             │ │
│  │  📈 Performance:            │ │
│  │  Total: $XX,XXX (+X.X%)     │ │
│  │  Cash:  $5,000              │ │
│  │                             │ │
│  └─────────────────────────────┘ │
│                                 │
│  ┌─────────────────────────────┐ │
│  │      🤖 AI ASSISTANT        │ │
│  │                             │ │
│  │  ┌─────────────────────────┐ │ │
│  │  │                         │ │ │
│  │  │   Intelligent Insights  │ │ │
│  │  │                         │ │ │
│  │  └─────────────────────────┘ │ │
│  │                             │ │
│  │  ┌─────────────────────────┐ │ │
│  │  │ Ask me anything  [Send] │ │ │
│  │  └─────────────────────────┘ │ │
│  │                             │ │
│  └─────────────────────────────┘ │
│                                 │
└─────────────────────────────────┘
```

## Component Breakdown

### Portfolio Dashboard Component
```
┌─────────────────────────────────────────────────────────────────┐
│                    📊 Holdings Dashboard                       │
├──────────┬─────────┬─────────────┬─────────────┬───────────────┤
│  Symbol  │   Qty   │   Entry $   │  Current $  │   Performance │
├──────────┼─────────┼─────────────┼─────────────┼───────────────┤
│   AAPL   │    10   │   $150.00   │   $175.23   │ +$252.30 ↗16%│
│  GOOGL   │     5   │  $2500.00   │  $2634.50   │ +$672.50 ↗5% │
│   MSFT   │     8   │   $300.00   │   $347.89   │ +$383.12 ↗16%│
├──────────┼─────────┼─────────────┼─────────────┼───────────────┤
│          │         │             │   📈 TOTAL  │ +$1,307.92   │
└──────────┴─────────┴─────────────┴─────────────┴───────────────┘
```

### Performance Metrics Component
```
┌─────────────────────────────────────────────────────────────────┐
│                   📊 Performance Analytics                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  💰 Portfolio Value:          $28,307.92                       │
│  📈 Total Return:             +$1,307.92 (+4.84%) ↗           │
│  💵 Available Cash:           $5,000.00                        │
│  🏦 Account Total:            $33,307.92                       │
│                                                                 │
│  🔄 Real-time Data │ 🕐 Last Update: 14:30:25 EST             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### AI Assistant Component
```
┌─────────────────────────────────────────────────────────────────┐
│                     🤖 AI Investment Assistant                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  💬 Intelligent Conversation:                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                                                             │ │
│  │ 💼 You: What's my portfolio performance today?              │ │
│  │                                                             │ │
│  │ 🤖 Assistant: Your portfolio shows strong performance      │ │
│  │     with $28,307.92 total value, representing a 4.84%      │ │
│  │     gain (+$1,307.92). All holdings are trending           │ │
│  │     positively with AAPL leading at +16.82%.               │ │
│  │                                                             │ │
│  │ 💼 You: Should I consider rebalancing?                      │ │
│  │                                                             │ │
│  │ 🤖 Assistant: Based on current market data, your           │ │
│  │     diversified tech portfolio is well-positioned.         │ │
│  │     Consider monitoring GOOGL's momentum for potential     │ │
│  │     optimization opportunities.                             │ │
│  │                                                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────┐  ┌──────────────┐  │
│  │ Ask me about your investments...        │  │   Analyze 🔍 │  │
│  └─────────────────────────────────────────┘  └──────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## ProCogia-Inspired Color Scheme & Styling

### CSS Variables (ProCogia Theme)
```css
:root {
  /* ProCogia Primary Colors */
  --procogia-primary: #1e40af;        /* Professional blue */
  --procogia-secondary: #3b82f6;      /* Accent blue */
  --procogia-dark: #0f172a;           /* Dark navy */
  --procogia-light: #f8fafc;          /* Light background */
  
  /* Application Colors */
  --primary-bg: #f8fafc;              /* Clean white-gray */
  --card-bg: #ffffff;                 /* Pure white cards */
  --card-border: #e2e8f0;             /* Subtle borders */
  --header-bg: #1e40af;               /* ProCogia blue header */
  
  /* Text Colors */
  --text-primary: #0f172a;            /* Dark navy text */
  --text-secondary: #475569;          /* Medium gray */
  --text-light: #94a3b8;              /* Light gray */
  
  /* Status Colors */
  --success-green: #059669;           /* Positive returns */
  --warning-amber: #d97706;           /* Neutral/warning */
  --error-red: #dc2626;               /* Negative returns */
  
  /* Interactive Elements */
  --button-primary: #1e40af;          /* ProCogia blue buttons */
  --button-hover: #1d4ed8;            /* Darker blue hover */
  --link-color: #3b82f6;              /* Link blue */
  
  /* Effects */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.07);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
  --gradient: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
}
```

### Typography (ProCogia Style)
```
/* Professional Typography Hierarchy */
Logo/Brand:     32px, bold, ProCogia blue
Page Title:     28px, bold, --text-primary
Section Headers: 20px, semibold, --text-primary
Subsections:    18px, medium, --text-primary
Body Text:      16px, normal, --text-secondary
Data/Numbers:   16px, monospace, --text-primary
Small Text:     14px, normal, --text-light
Chat Text:      15px, normal, --text-secondary

/* Font Stack */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
             'Roboto', 'Helvetica Neue', Arial, sans-serif;
```

## Enhanced Interactive Elements

### Loading States (ProCogia Style)
```
Data Loading:
┌─────────────────────────────────┐
│  🔄 Analyzing portfolio data... │
│  ████████████░░░░░░░░░░░ 75%    │
│  Powered by ProCogia Analytics  │
└─────────────────────────────────┘

AI Processing:
┌─────────────────────────────────┐
│  🧠 AI Assistant analyzing...   │
│  ⚪ ⚪ ⚪ (pulsing animation)    │
│  Generating insights...         │
└─────────────────────────────────┘
```

### Error States (Professional)
```
API Connection Error:
┌─────────────────────────────────┐
│  ⚠️  Market data temporarily    │
│  unavailable. Our systems are   │
│  working to restore connection. │
│  [Retry Connection] ──────────── │
└─────────────────────────────────┘
```

## Header Design with ProCogia Branding

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  [ProCogia Logo]           AI Portfolio Agent                    [⚙️ Settings] │
│  Data-Driven Investment Intelligence                               [📊 Export] │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
```

## Professional Data Visualization Elements

### Performance Indicators
```
Trending Up:    ↗ +16.82% 🟢
Trending Down:  ↘ -2.45%  🔴
Stable:         → +0.12%  🟡
Strong Growth:  ⬆ +25.3%  🟢🟢
```

### Status Indicators
```
🟢 Market Open    🔴 Market Closed    🟡 Pre-Market
🔄 Live Data      ⏸️ Delayed Data     ⚠️ Data Issue
💹 Trending       📈 Bullish          📉 Bearish
```

## Responsive Breakpoints (ProCogia Standard)

```
Large Desktop (≥1440px): Full layout with expanded panels
Desktop (≥1024px):       Standard two-column layout
Tablet (768-1023px):     Condensed two-column
Mobile (≥640px):         Single column, stacked
Small Mobile (<640px):   Compact single column
```

## Professional User Flow

```
Application Launch
  │
  ▼
┌─────────────────┐
│ Authentication  │ ──► ProCogia secure login
│ & Data Load     │     Portfolio data fetch
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ Dashboard View  │ ──► Real-time analytics
│                 │     Performance metrics
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ AI Interaction  │ ──► Intelligent analysis
│                 │     Investment insights
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ Actionable      │ ──► Data-driven decisions
│ Intelligence    │     Portfolio optimization
└─────────────────┘
```

## ProCogia Design Principles Applied

- **Professional Aesthetics**: Clean, modern interface reflecting ProCogia's enterprise focus
- **Data-First Design**: Emphasis on analytics and intelligent insights
- **Intuitive Navigation**: Streamlined user experience for financial professionals
- **Responsive Excellence**: Optimized for all devices and screen sizes
- **Brand Consistency**: ProCogia colors, typography, and visual language throughout

This design maintains the functional MVP requirements while elevating the visual presentation to match ProCogia's professional standards and brand identity from [ProCogia.com](https://procogia.com/). The logo from [ProCogia's assets](https://procogia.com/wp-content/uploads/2024/03/procogia-horizontal-light-bg-1.png) will be integrated as the primary branding element. 