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
CREATE POLICY market_context_cache_policy ON market_context_cache 
    USING (auth.role() = 'authenticated')
    WITH CHECK (auth.role() = 'authenticated'); 