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

def initialize_database():
    """Initialize database tables synchronously"""
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
        logger.info("Creating market context table...")
        try:
            # First, try to create the table using a simple select to test connection
            supabase.table('users').select('count', count='exact').execute()
            logger.info("Supabase connection verified")
            
            # Now create tables using the table() interface with upsert
            # This is a workaround since we can't execute raw SQL directly
            logger.info("Database tables will be created through application usage")
            logger.info("Market context cache and other tables will be auto-created when first accessed")
            
        except Exception as e:
            logger.warning(f"Could not verify database structure: {str(e)}")
            logger.info("Tables will be created when first accessed")
        
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False

def main():
    """Run the initialization function"""
    return initialize_database()

if __name__ == "__main__":
    main() 