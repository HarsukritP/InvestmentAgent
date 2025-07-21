"""
Database initialization script for Railway deployment
This script will run the SQL setup files to create the necessary tables
"""
import os
import logging
import asyncio
from supabase import create_client, Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_sql_file(file_path):
    """Read SQL file contents"""
    try:
        # Try current directory first
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return file.read()
        # Try with absolute path
        elif os.path.exists(os.path.join(os.getcwd(), file_path)):
            with open(os.path.join(os.getcwd(), file_path), 'r') as file:
                return file.read()
        # Try looking in the parent directory
        elif os.path.exists(os.path.join(os.getcwd(), '..', os.path.basename(file_path))):
            with open(os.path.join(os.getcwd(), '..', os.path.basename(file_path)), 'r') as file:
                return file.read()
        else:
            # Look for the file in the current directory structure
            for root, dirs, files in os.walk(os.getcwd()):
                if os.path.basename(file_path) in files:
                    full_path = os.path.join(root, os.path.basename(file_path))
                    with open(full_path, 'r') as file:
                        logger.info(f"Found SQL file at: {full_path}")
                        return file.read()
            
            logger.error(f"SQL file not found: {file_path}")
            return None
    except Exception as e:
        logger.error(f"Error reading SQL file {file_path}: {str(e)}")
        return None

async def initialize_database():
    """Initialize database tables"""
    try:
        # Get Supabase credentials
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')  # Use service key for admin operations
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables")
        
        # Initialize Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("Connected to Supabase")
        
        # Print current working directory for debugging
        logger.info(f"Current working directory: {os.getcwd()}")
        
        # Create market context table directly
        market_context_sql = """
        -- Create market_context_cache table for storing market data
        CREATE TABLE IF NOT EXISTS market_context_cache (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            key TEXT NOT NULL UNIQUE,
            data JSONB NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            CONSTRAINT market_context_cache_key_unique UNIQUE (key)
        );

        -- Add indexes
        CREATE INDEX IF NOT EXISTS market_context_cache_key_idx ON market_context_cache (key);
        CREATE INDEX IF NOT EXISTS market_context_cache_timestamp_idx ON market_context_cache (timestamp);

        -- Add comment
        COMMENT ON TABLE market_context_cache IS 'Cache for market context data including economic indicators and news';

        -- Grant permissions
        ALTER TABLE market_context_cache ENABLE ROW LEVEL SECURITY;

        -- Create policy for authenticated users
        CREATE POLICY IF NOT EXISTS market_context_cache_policy ON market_context_cache 
            USING (true)
            WITH CHECK (true);
        """
        
        # Execute market context table creation
        logger.info("Creating market context table...")
        result = await supabase.rpc('execute_sql', {'sql_query': market_context_sql}).execute()
        logger.info("Market context table created")
        
        # Create transaction stats function
        transaction_stats_sql = """
        CREATE OR REPLACE FUNCTION public.get_transaction_stats(
          p_portfolio_id UUID
        ) RETURNS JSON AS $$
        BEGIN
          RETURN (
            WITH stats AS (
              SELECT
                COUNT(*) AS transaction_count,
                COUNT(*) FILTER (WHERE transaction_type LIKE 'BUY%') AS buy_count,
                COUNT(*) FILTER (WHERE transaction_type = 'SELL') AS sell_count,
                SUM(total_amount) FILTER (WHERE transaction_type LIKE 'BUY%') AS total_buy_amount,
                SUM(total_amount) FILTER (WHERE transaction_type = 'SELL') AS total_sell_amount,
                (SELECT symbol FROM public.transactions 
                 WHERE portfolio_id = p_portfolio_id 
                 GROUP BY symbol 
                 ORDER BY COUNT(*) DESC LIMIT 1) AS most_traded_symbol,
                (SELECT ROW_TO_JSON(t) FROM (
                    SELECT id, transaction_type, symbol, shares, price_per_share, total_amount, created_at as timestamp
                    FROM public.transactions
                    WHERE portfolio_id = p_portfolio_id
                    ORDER BY total_amount DESC
                    LIMIT 1
                ) t) AS largest_transaction
              FROM public.transactions
              WHERE portfolio_id = p_portfolio_id
            )
            SELECT ROW_TO_JSON(stats) FROM stats
          );
        END;
        $$ LANGUAGE plpgsql STABLE;
        
        COMMENT ON FUNCTION public.get_transaction_stats IS 'Gets transaction statistics for a portfolio';
        """
        
        # Execute transaction stats function creation
        logger.info("Creating transaction stats function...")
        result = await supabase.rpc('execute_sql', {'sql_query': transaction_stats_sql}).execute()
        logger.info("Transaction stats function created")
        
        # Create basic tables if they don't exist
        basic_tables_sql = """
        -- Enable Row Level Security (RLS) extensions if not already enabled
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

        -- 1. Create Users Table FIRST (no dependencies)
        CREATE TABLE IF NOT EXISTS users (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            google_id TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            picture_url TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- 2. Create Portfolios Table (depends on users)
        CREATE TABLE IF NOT EXISTS portfolios (
            id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name TEXT NOT NULL DEFAULT 'My Portfolio',
            cash_balance DECIMAL(15,2) DEFAULT 10000.00,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- 3. Create Holdings Table (depends on portfolios)
        CREATE TABLE IF NOT EXISTS holdings (
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
        CREATE TABLE IF NOT EXISTS transactions (
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
        CREATE TABLE IF NOT EXISTS current_prices (
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

        CREATE TABLE IF NOT EXISTS historical_prices (
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
        CREATE POLICY IF NOT EXISTS "Allow all operations on users" ON users
            FOR ALL USING (true) WITH CHECK (true);

        CREATE POLICY IF NOT EXISTS "Allow all operations on portfolios" ON portfolios
            FOR ALL USING (true) WITH CHECK (true);

        CREATE POLICY IF NOT EXISTS "Allow all operations on holdings" ON holdings
            FOR ALL USING (true) WITH CHECK (true);

        CREATE POLICY IF NOT EXISTS "Allow all operations on transactions" ON transactions
            FOR ALL USING (true) WITH CHECK (true);

        CREATE POLICY IF NOT EXISTS "Allow all operations on current_prices" ON current_prices
            FOR ALL USING (true) WITH CHECK (true);

        CREATE POLICY IF NOT EXISTS "Allow all operations on historical_prices" ON historical_prices
            FOR ALL USING (true) WITH CHECK (true);

        -- 8. Create Indexes for Performance
        CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios(user_id);
        CREATE INDEX IF NOT EXISTS idx_holdings_portfolio_id ON holdings(portfolio_id);
        CREATE INDEX IF NOT EXISTS idx_holdings_symbol ON holdings(symbol);
        CREATE INDEX IF NOT EXISTS idx_transactions_portfolio_id ON transactions(portfolio_id);
        CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
        CREATE INDEX IF NOT EXISTS idx_transactions_symbol ON transactions(symbol);
        CREATE INDEX IF NOT EXISTS idx_current_prices_symbol ON current_prices(symbol);
        CREATE INDEX IF NOT EXISTS idx_historical_prices_symbol_date ON historical_prices(symbol, price_date);

        -- 9. Create Updated At Triggers
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';

        DROP TRIGGER IF EXISTS update_users_updated_at ON users;
        CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

        DROP TRIGGER IF EXISTS update_portfolios_updated_at ON portfolios;
        CREATE TRIGGER update_portfolios_updated_at BEFORE UPDATE ON portfolios
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

        DROP TRIGGER IF EXISTS update_holdings_updated_at ON holdings;
        CREATE TRIGGER update_holdings_updated_at BEFORE UPDATE ON holdings
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """
        
        # Execute basic tables creation
        logger.info("Creating basic tables...")
        result = await supabase.rpc('execute_sql', {'sql_query': basic_tables_sql}).execute()
        logger.info("Basic tables created")
        
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False

def main():
    """Run the async initialization function"""
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(initialize_database())
    return success

if __name__ == "__main__":
    main() 