-- ProCogia AI Hub Database Setup Script
-- Run this in your NEW hub Supabase project after creation

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table (migrated from portfolio database)
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    avatar_url TEXT,
    google_id TEXT UNIQUE,
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes for performance
    CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Create agents registry table
CREATE TABLE IF NOT EXISTS agents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    
    -- Agent identification
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    detailed_description TEXT,
    icon_url TEXT,
    
    -- Technical configuration
    api_prefix TEXT, -- e.g., "/api/portfolio-agent"
    frontend_route TEXT, -- e.g., "/portfolio-agent"
    database_url TEXT, -- URL to agent's dedicated database
    
    -- Status and metadata
    is_active BOOLEAN DEFAULT true,
    version TEXT DEFAULT '1.0.0',
    category TEXT DEFAULT 'general', -- 'finance', 'trading', 'analytics', etc.
    tags TEXT[], -- Array of tags for categorization
    
    -- Usage statistics
    total_users INTEGER DEFAULT 0,
    total_sessions INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT agents_slug_format CHECK (slug ~* '^[a-z0-9-]+$'),
    CONSTRAINT agents_name_length CHECK (length(name) BETWEEN 1 AND 100),
    CONSTRAINT agents_description_length CHECK (length(description) BETWEEN 1 AND 500)
);

-- Create user sessions tracking table
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    
    -- Session information
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    session_start TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    session_end TIMESTAMP WITH TIME ZONE,
    
    -- Session metadata
    ip_address INET,
    user_agent TEXT,
    duration_seconds INTEGER, -- Calculated on session end
    
    -- Activity tracking
    actions_count INTEGER DEFAULT 0,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    
    -- Indexes for performance
    CONSTRAINT user_sessions_duration_check CHECK (duration_seconds >= 0),
    CONSTRAINT user_sessions_actions_check CHECK (actions_count >= 0)
);

-- Create user agent usage statistics
CREATE TABLE IF NOT EXISTS user_agent_stats (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    
    -- Composite key
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    
    -- Usage statistics
    total_sessions INTEGER DEFAULT 0,
    total_time_seconds INTEGER DEFAULT 0,
    total_actions INTEGER DEFAULT 0,
    first_used_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    
    -- Preferences (JSON for flexibility)
    preferences JSONB DEFAULT '{}',
    
    -- Unique constraint on user + agent combination
    UNIQUE(user_id, agent_id),
    
    -- Constraints
    CONSTRAINT user_agent_stats_sessions_check CHECK (total_sessions >= 0),
    CONSTRAINT user_agent_stats_time_check CHECK (total_time_seconds >= 0),
    CONSTRAINT user_agent_stats_actions_check CHECK (total_actions >= 0)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login_at);

CREATE INDEX IF NOT EXISTS idx_agents_slug ON agents(slug);
CREATE INDEX IF NOT EXISTS idx_agents_is_active ON agents(is_active);
CREATE INDEX IF NOT EXISTS idx_agents_category ON agents(category);
CREATE INDEX IF NOT EXISTS idx_agents_tags ON agents USING GIN(tags);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_agent_id ON user_sessions(agent_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_start ON user_sessions(session_start);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions(user_id, agent_id) WHERE session_end IS NULL;

CREATE INDEX IF NOT EXISTS idx_user_agent_stats_user_id ON user_agent_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_user_agent_stats_agent_id ON user_agent_stats(agent_id);
CREATE INDEX IF NOT EXISTS idx_user_agent_stats_last_used ON user_agent_stats(last_used_at);

-- Insert initial portfolio agent registration
INSERT INTO agents (
    name,
    slug,
    description,
    detailed_description,
    api_prefix,
    frontend_route,
    category,
    tags,
    version
) VALUES (
    'Portfolio Management Agent',
    'portfolio-agent',
    'AI-powered portfolio management and trading assistant',
    'Advanced AI agent that helps users manage their investment portfolios, execute trades, analyze market data, and get intelligent investment recommendations. Features real-time market data, automated trading strategies, and comprehensive portfolio analytics.',
    '/api/portfolio-agent',
    '/portfolio-agent',
    'finance',
    ARRAY['trading', 'investment', 'portfolio', 'finance', 'ai-assistant'],
    '1.0.0'
) ON CONFLICT (slug) DO UPDATE SET
    updated_at = timezone('utc'::text, now()),
    description = EXCLUDED.description,
    detailed_description = EXCLUDED.detailed_description,
    api_prefix = EXCLUDED.api_prefix,
    frontend_route = EXCLUDED.frontend_route,
    category = EXCLUDED.category,
    tags = EXCLUDED.tags;

-- Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_agents_updated_at ON agents;
CREATE TRIGGER update_agents_updated_at 
    BEFORE UPDATE ON agents 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_sessions_updated_at ON user_sessions;
CREATE TRIGGER update_user_sessions_updated_at 
    BEFORE UPDATE ON user_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_agent_stats_updated_at ON user_agent_stats;
CREATE TRIGGER update_user_agent_stats_updated_at 
    BEFORE UPDATE ON user_agent_stats 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to automatically update session duration
CREATE OR REPLACE FUNCTION calculate_session_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.session_end IS NOT NULL AND OLD.session_end IS NULL THEN
        NEW.duration_seconds = EXTRACT(EPOCH FROM (NEW.session_end - NEW.session_start))::INTEGER;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for session duration calculation
DROP TRIGGER IF EXISTS calculate_session_duration_trigger ON user_sessions;
CREATE TRIGGER calculate_session_duration_trigger
    BEFORE UPDATE ON user_sessions
    FOR EACH ROW EXECUTE FUNCTION calculate_session_duration();

-- Create Row Level Security (RLS) policies

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_agent_stats ENABLE ROW LEVEL SECURITY;

-- Users can read their own data
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

-- Anyone can read active agents (for public agent directory)
CREATE POLICY "Anyone can view active agents" ON agents
    FOR SELECT USING (is_active = true);

-- Users can read their own sessions
CREATE POLICY "Users can view own sessions" ON user_sessions
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert own sessions" ON user_sessions
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own sessions" ON user_sessions
    FOR UPDATE USING (auth.uid()::text = user_id::text);

-- Users can read their own stats
CREATE POLICY "Users can view own agent stats" ON user_agent_stats
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert own agent stats" ON user_agent_stats
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own agent stats" ON user_agent_stats
    FOR UPDATE USING (auth.uid()::text = user_id::text);

-- Grant permissions to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Grant permissions to service role (for server-side operations)
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;

-- Create a view for agent statistics
CREATE OR REPLACE VIEW agent_usage_summary AS
SELECT 
    a.id,
    a.name,
    a.slug,
    a.description,
    a.category,
    a.is_active,
    a.total_users,
    a.total_sessions,
    a.last_used_at,
    COUNT(DISTINCT uas.user_id) as active_users,
    AVG(uas.total_sessions) as avg_sessions_per_user,
    SUM(uas.total_time_seconds) as total_usage_time,
    MAX(uas.last_used_at) as most_recent_usage
FROM agents a
LEFT JOIN user_agent_stats uas ON a.id = uas.agent_id
GROUP BY a.id, a.name, a.slug, a.description, a.category, a.is_active, 
         a.total_users, a.total_sessions, a.last_used_at;

-- Grant access to the view
GRANT SELECT ON agent_usage_summary TO authenticated, service_role;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Hub database setup complete! Tables created:';
    RAISE NOTICE '✅ users - User management';
    RAISE NOTICE '✅ agents - Agent registry';
    RAISE NOTICE '✅ user_sessions - Session tracking';
    RAISE NOTICE '✅ user_agent_stats - Usage statistics';
    RAISE NOTICE '✅ agent_usage_summary - Analytics view';
    RAISE NOTICE '';
    RAISE NOTICE 'Portfolio agent registered with slug: portfolio-agent';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Get Supabase URL and keys from project settings';
    RAISE NOTICE '2. Configure environment variables';
    RAISE NOTICE '3. Migrate users from portfolio database';
END $$; 