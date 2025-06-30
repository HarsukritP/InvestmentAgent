#!/usr/bin/env python3
"""
ProCogia AI Hub - User Migration Script

This script migrates users from the portfolio database to the hub database.
Run this after setting up the hub database to move user management centrally.

Requirements:
    pip install supabase python-dotenv

Usage:
    python scripts/migrate-users-to-hub.py
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def get_portfolio_client() -> Client:
    """Create Supabase client for portfolio database"""
    url = os.getenv('PORTFOLIO_SUPABASE_URL') or os.getenv('SUPABASE_URL')
    key = os.getenv('PORTFOLIO_SUPABASE_ANON_KEY') or os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        raise ValueError(
            "Portfolio database credentials not found. Please set:\n"
            "PORTFOLIO_SUPABASE_URL (or SUPABASE_URL)\n"
            "PORTFOLIO_SUPABASE_ANON_KEY (or SUPABASE_ANON_KEY)"
        )
    
    return create_client(url, key)

def get_hub_client() -> Client:
    """Create Supabase client for hub database"""
    url = os.getenv('HUB_SUPABASE_URL')
    key = os.getenv('HUB_SUPABASE_ANON_KEY')
    
    if not url or not key:
        raise ValueError(
            "Hub database credentials not found. Please set:\n"
            "HUB_SUPABASE_URL\n"
            "HUB_SUPABASE_ANON_KEY"
        )
    
    return create_client(url, key)

def fetch_portfolio_users(portfolio_client: Client) -> List[Dict[str, Any]]:
    """Fetch all users from portfolio database"""
    try:
        response = portfolio_client.table('users').select('*').execute()
        users = response.data
        print(f"✅ Found {len(users)} users in portfolio database")
        return users
    except Exception as e:
        print(f"❌ Error fetching users from portfolio database: {e}")
        raise

def check_hub_users(hub_client: Client) -> List[Dict[str, Any]]:
    """Check existing users in hub database"""
    try:
        response = hub_client.table('users').select('*').execute()
        users = response.data
        print(f"ℹ️  Found {len(users)} existing users in hub database")
        return users
    except Exception as e:
        print(f"ℹ️  No existing users in hub database (expected for first run)")
        return []

def migrate_users(portfolio_users: List[Dict[str, Any]], hub_client: Client, existing_users: List[Dict[str, Any]]) -> None:
    """Migrate users from portfolio to hub database"""
    existing_emails = {user['email'] for user in existing_users}
    existing_ids = {user['id'] for user in existing_users}
    
    users_to_insert = []
    users_to_update = []
    skipped_count = 0
    
    for user in portfolio_users:
        # Prepare user data for hub database
        hub_user = {
            'id': user['id'],
            'email': user['email'],
            'name': user.get('name'),
            'avatar_url': user.get('avatar_url'),
            'google_id': user.get('google_id'),
            'is_active': user.get('is_active', True),
            'last_login_at': user.get('last_login_at'),
            'created_at': user.get('created_at'),
            'updated_at': user.get('updated_at')
        }
        
        if user['id'] in existing_ids:
            # User exists, update if needed
            users_to_update.append(hub_user)
        elif user['email'] in existing_emails:
            print(f"⚠️  Email conflict: {user['email']} exists with different ID")
            skipped_count += 1
        else:
            users_to_insert.append(hub_user)
    
    # Insert new users
    if users_to_insert:
        print(f"📥 Inserting {len(users_to_insert)} new users...")
        try:
            response = hub_client.table('users').insert(users_to_insert).execute()
            print(f"✅ Successfully inserted {len(response.data)} users")
        except Exception as e:
            print(f"❌ Error inserting users: {e}")
            raise
    
    # Update existing users
    if users_to_update:
        print(f"🔄 Updating {len(users_to_update)} existing users...")
        update_count = 0
        for user in users_to_update:
            try:
                hub_client.table('users').update(user).eq('id', user['id']).execute()
                update_count += 1
            except Exception as e:
                print(f"⚠️  Warning: Failed to update user {user['email']}: {e}")
        print(f"✅ Successfully updated {update_count} users")
    
    if skipped_count > 0:
        print(f"⚠️  Skipped {skipped_count} users due to email conflicts")

def verify_migration(portfolio_client: Client, hub_client: Client) -> None:
    """Verify the migration was successful"""
    print("\n🔍 Verifying migration...")
    
    # Count users in both databases
    portfolio_count = len(portfolio_client.table('users').select('id').execute().data)
    hub_count = len(hub_client.table('users').select('id').execute().data)
    
    print(f"Portfolio DB users: {portfolio_count}")
    print(f"Hub DB users: {hub_count}")
    
    if hub_count >= portfolio_count:
        print("✅ Migration verification successful!")
    else:
        print("⚠️  Migration verification warning: Hub has fewer users than portfolio")
    
    # Sample a few users to verify data integrity
    portfolio_sample = portfolio_client.table('users').select('*').limit(3).execute().data
    for portfolio_user in portfolio_sample:
        hub_user_response = hub_client.table('users').select('*').eq('id', portfolio_user['id']).execute()
        if hub_user_response.data:
            hub_user = hub_user_response.data[0]
            if hub_user['email'] == portfolio_user['email']:
                print(f"✅ User {portfolio_user['email']} migrated correctly")
            else:
                print(f"❌ User {portfolio_user['id']} data mismatch")
        else:
            print(f"❌ User {portfolio_user['email']} not found in hub database")

def create_portfolio_agent_stats(hub_client: Client, portfolio_users: List[Dict[str, Any]]) -> None:
    """Create initial user agent stats for portfolio agent"""
    print("\n📊 Creating initial portfolio agent usage stats...")
    
    # Get portfolio agent ID
    agent_response = hub_client.table('agents').select('id').eq('slug', 'portfolio-agent').execute()
    if not agent_response.data:
        print("❌ Portfolio agent not found in agents table")
        return
    
    agent_id = agent_response.data[0]['id']
    
    # Create stats for each user
    stats_to_insert = []
    for user in portfolio_users:
        stats = {
            'user_id': user['id'],
            'agent_id': agent_id,
            'total_sessions': 1,  # Assume at least one session
            'total_time_seconds': 0,
            'total_actions': 0,
            'first_used_at': user.get('created_at'),
            'last_used_at': user.get('last_login_at') or user.get('created_at'),
            'preferences': {}
        }
        stats_to_insert.append(stats)
    
    try:
        response = hub_client.table('user_agent_stats').insert(stats_to_insert).execute()
        print(f"✅ Created agent stats for {len(response.data)} users")
    except Exception as e:
        print(f"⚠️  Warning: Error creating agent stats: {e}")

def main():
    """Main migration function"""
    print("🚀 ProCogia AI Hub - User Migration Script")
    print("=" * 50)
    
    try:
        # Create database clients
        print("🔌 Connecting to databases...")
        portfolio_client = get_portfolio_client()
        hub_client = get_hub_client()
        print("✅ Database connections established")
        
        # Fetch users from portfolio database
        print("\n📥 Fetching users from portfolio database...")
        portfolio_users = fetch_portfolio_users(portfolio_client)
        
        if not portfolio_users:
            print("ℹ️  No users found in portfolio database. Nothing to migrate.")
            return
        
        # Check existing users in hub database
        print("\n🔍 Checking existing users in hub database...")
        existing_users = check_hub_users(hub_client)
        
        # Confirm migration
        print(f"\n📋 Migration Summary:")
        print(f"   Users in portfolio DB: {len(portfolio_users)}")
        print(f"   Users in hub DB: {len(existing_users)}")
        
        if len(existing_users) > 0:
            print("⚠️  Hub database already contains users. This will update/merge data.")
        
        response = input("\nProceed with migration? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Migration cancelled by user")
            return
        
        # Perform migration
        print("\n🔄 Starting user migration...")
        migrate_users(portfolio_users, hub_client, existing_users)
        
        # Create initial agent stats
        create_portfolio_agent_stats(hub_client, portfolio_users)
        
        # Verify migration
        verify_migration(portfolio_client, hub_client)
        
        print("\n🎉 User migration completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Update your environment variables to use hub database for auth")
        print("   2. Remove users table from portfolio database (optional)")
        print("   3. Test the hub service with migrated users")
        
    except KeyboardInterrupt:
        print("\n❌ Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 