#!/usr/bin/env python3
"""
Test Supabase Connection Script

Tests the connection to Supabase and displays basic information.
Run this to verify your credentials are working.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config_loader import get_config

def test_connection():
    """Test Supabase connection and display info."""
    print("=" * 60)
    print("SUPABASE CONNECTION TEST")
    print("=" * 60)
    print()
    
    # Load config
    try:
        config = get_config()
        print(f"✓ Config loaded successfully")
        print(f"  URL: {config.supabase_url}")
        print(f"  Service Key: {'*' * 20}...{config.supabase_service_key[-10:]}")
        print()
    except Exception as e:
        print(f"✗ Failed to load config: {e}")
        return False
    
    # Check if configured
    if not config.is_configured:
        print("✗ Supabase credentials not configured")
        print("  Please set SUPABASE_URL and SUPABASE_SERVICE_KEY")
        print("  Or add them to config/config_local.ini")
        return False
    
    # Test connection
    try:
        from supabase import create_client
        
        print("Attempting to connect to Supabase...")
        client = create_client(config.supabase_url, config.supabase_service_key)
        
        # Try a simple query
        print("Testing connection with a simple query...")
        result = client.table('dim_schedule').select('game_id').limit(1).execute()
        
        print()
        print("=" * 60)
        print("✓ CONNECTION SUCCESSFUL!")
        print("=" * 60)
        print()
        print("Connection details:")
        print(f"  URL: {config.supabase_url}")
        print(f"  Status: Connected")
        print()
        
        # Try to get table count
        try:
            count_result = client.table('dim_schedule').select('game_id', count='exact').execute()
            print(f"  Sample table (dim_schedule) has {count_result.count} rows")
        except:
            pass
        
        return True
        
    except ImportError:
        print("✗ Supabase package not installed")
        print("  Install with: pip install supabase --break-system-packages")
        return False
    except Exception as e:
        print()
        print("=" * 60)
        print("✗ CONNECTION FAILED")
        print("=" * 60)
        print()
        print(f"Error: {e}")
        print()
        print("Common issues:")
        print("  1. Check your URL and service_key in config/config_local.ini")
        print("  2. Verify your Supabase project is active")
        print("  3. Check if RLS (Row Level Security) is blocking access")
        print("  4. Ensure the service_key has proper permissions")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
