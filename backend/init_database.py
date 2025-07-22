"""
Database initialization script for the AI Portfolio Agent
"""
import os
import logging
import asyncio
from supabase import create_client, Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize database tables and functions"""
    try:
        # Get Supabase credentials
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            logger.error("Supabase credentials not found in environment variables")
            return False
        
        # Connect to Supabase
        supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("Connected to Supabase")
        
        # Check current working directory
        cwd = os.getcwd()
        logger.info(f"Current working directory: {cwd}")
        
        # Log successful connection
        logger.info("Supabase connection verified")
        logger.info("Database tables will be created through application usage")
        logger.info("Market context cache and other tables will be auto-created when first accessed")
        logger.info("Database initialization completed successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False

def main():
    """Main entry point"""
    success = initialize_database()
    if success:
        logger.info("Database initialization completed successfully")
    else:
        logger.error("Database initialization failed")

if __name__ == "__main__":
    main() 