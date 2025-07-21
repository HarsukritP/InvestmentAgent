"""
Database initialization script for Railway deployment
This script will run the SQL setup files to create the necessary tables
"""
import os
import logging
from supabase import create_client, Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_sql_file(file_path):
    """Read SQL file contents"""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error reading SQL file {file_path}: {str(e)}")
        return None

def main():
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
        
        # Execute main database setup script
        setup_sql = read_sql_file('../setup_database_fixed.sql')
        if setup_sql:
            logger.info("Running main database setup script...")
            result = supabase.sql(setup_sql).execute()
            logger.info("Main database setup completed")
        
        # Execute market context table creation script
        market_context_sql = read_sql_file('create_market_context_table.sql')
        if market_context_sql:
            logger.info("Creating market context table...")
            result = supabase.sql(market_context_sql).execute()
            logger.info("Market context table created")
        
        # Create transaction stats function
        from run_sql import main as run_transaction_stats
        logger.info("Creating transaction stats function...")
        run_transaction_stats()
        logger.info("Transaction stats function created")
        
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    main() 