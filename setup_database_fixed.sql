-- Portfolio Agent Database Setup Script - FIXED VERSION
-- Run this in your Supabase SQL Editor

-- First, drop existing tables if they exist (to start clean)
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS holdings CASCADE;
DROP TABLE IF EXISTS portfolios CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS historical_prices CASCADE;
DROP TABLE IF EXISTS current_prices CASCADE;

-- Enable Row Level Security (RLS) extensions if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Create Users Table FIRST (no dependencies)
CREATE TABLE users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    google_id TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    picture_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Create Portfolios Table (depends on users)
CREATE TABLE portfolios (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL DEFAULT 'My Portfolio',
    cash_balance DECIMAL(15,2) DEFAULT 10000.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Create Holdings Table (depends on portfolios)
CREATE TABLE holdings (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    shares DECIMAL(15,6) NOT NULL,
    average_cost DECIMAL(15,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(portfolio_id, symbol)
);

-- 4. Create Transactions Table (depends on portfolios and users)
CREATE TABLE transactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('BUY', 'SELL')),
    symbol TEXT NOT NULL,
    shares DECIMAL(15,6) NOT NULL,
    price_per_share DECIMAL(15,2) NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL,
    cash_balance_after DECIMAL(15,2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Create Market Data Tables (no dependencies)
CREATE TABLE current_prices (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    symbol TEXT NOT NULL,
    price DECIMAL(15,2) NOT NULL,
    change_amount DECIMAL(15,2),
    change_percent DECIMAL(8,4),
    volume BIGINT,
    market_cap BIGINT,
    source TEXT DEFAULT 'twelvedata',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(symbol)
);

CREATE TABLE historical_prices (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    symbol TEXT NOT NULL,
    price DECIMAL(15,2) NOT NULL,
    volume BIGINT,
    source TEXT DEFAULT 'twelvedata',
    price_date DATE NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(symbol, price_date)
);

-- 6. Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE holdings ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE current_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE historical_prices ENABLE ROW LEVEL SECURITY;

-- 7. Create RLS Policies (Allow all operations since we're using service key)
CREATE POLICY "Allow all operations on users" ON users
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on portfolios" ON portfolios
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on holdings" ON holdings
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on transactions" ON transactions
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on current_prices" ON current_prices
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on historical_prices" ON historical_prices
    FOR ALL USING (true) WITH CHECK (true);

-- 8. Create Indexes for Performance
CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_portfolios_user_id ON portfolios(user_id);
CREATE INDEX idx_holdings_portfolio_id ON holdings(portfolio_id);
CREATE INDEX idx_holdings_symbol ON holdings(symbol);
CREATE INDEX idx_transactions_portfolio_id ON transactions(portfolio_id);
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_symbol ON transactions(symbol);
CREATE INDEX idx_current_prices_symbol ON current_prices(symbol);
CREATE INDEX idx_historical_prices_symbol_date ON historical_prices(symbol, price_date);

-- 9. Create Updated At Triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_portfolios_updated_at BEFORE UPDATE ON portfolios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_holdings_updated_at BEFORE UPDATE ON holdings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Success message
SELECT 'Database setup completed successfully! All tables created.' as message,
       'Tables: users, portfolios, holdings, transactions, current_prices, historical_prices' as tables_created; 