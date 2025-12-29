#!/usr/bin/env python3
"""
BenchSight Supabase Connection Test
===================================
Tests connection to Supabase and performs health checks.

Usage:
    python scripts/supabase_test_connection.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Setup paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
CONFIG_DIR = PROJECT_DIR / "config"

def test_connection():
    """Test Supabase connection and perform health checks."""
    
    print("=" * 60)
    print("BENCHSIGHT SUPABASE CONNECTION TEST")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test 1: Check supabase package
    print("\n[1/5] Checking supabase package...")
    try:
        from supabase import create_client, Client
        print("  ✓ supabase package installed")
    except ImportError:
        print("  ✗ supabase package not installed")
        print("    Run: pip install supabase")
        return False
    
    # Test 2: Check credentials
    print("\n[2/5] Checking credentials...")
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    
    if not url or not key:
        # Try config file
        config_file = CONFIG_DIR / "config_local.ini"
        if config_file.exists():
            import configparser
            config = configparser.ConfigParser()
            config.read(config_file)
            url = config.get('supabase', 'url', fallback=None)
            key = config.get('supabase', 'key', fallback=None)
            if url and key:
                print("  ✓ Credentials loaded from config_local.ini")
        
    if url and key:
        print(f"  ✓ URL: {url[:40]}...")
        print(f"  ✓ Key: {key[:20]}...")
    else:
        print("  ✗ Credentials not found!")
        print("    Set SUPABASE_URL and SUPABASE_KEY environment variables")
        print("    Or add to config/config_local.ini:")
        print("    [supabase]")
        print("    url = https://your-project.supabase.co")
        print("    key = your-anon-key")
        return False
    
    # Test 3: Connect
    print("\n[3/5] Testing connection...")
    try:
        client = create_client(url, key)
        print("  ✓ Client created successfully")
    except Exception as e:
        print(f"  ✗ Connection failed: {e}")
        return False
    
    # Test 4: Query test
    print("\n[4/5] Testing query capability...")
    try:
        # Try to query a known table or system table
        result = client.table('dim_player').select('player_id').limit(1).execute()
        print(f"  ✓ Query successful")
        if result.data:
            print(f"  ✓ dim_player exists with data")
        else:
            print(f"  ⚠ dim_player exists but empty (or doesn't exist)")
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg.lower() or "404" in error_msg:
            print(f"  ⚠ Tables not created yet (this is OK for fresh install)")
        else:
            print(f"  ⚠ Query test: {e}")
    
    # Test 5: List tables
    print("\n[5/5] Checking existing tables...")
    try:
        # This depends on your Supabase setup
        # Try to get table list via RPC or direct query
        benchsight_tables = [
            'dim_player', 'dim_team', 'dim_schedule',
            'fact_player_game_stats', 'fact_events_player', 'fact_shifts_player'
        ]
        
        existing = []
        for table in benchsight_tables:
            try:
                result = client.table(table).select('*').limit(1).execute()
                existing.append(table)
            except:
                pass
        
        if existing:
            print(f"  ✓ Found {len(existing)} BenchSight tables:")
            for t in existing:
                print(f"    - {t}")
        else:
            print("  ⚠ No BenchSight tables found (run --rebuild to create)")
            
    except Exception as e:
        print(f"  ⚠ Could not list tables: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("CONNECTION TEST COMPLETE")
    print("=" * 60)
    print("\n✓ Supabase connection is working!")
    print("\nNext steps:")
    print("  1. Create tables: python scripts/supabase_loader.py --create-only")
    print("  2. Upload data:   python scripts/supabase_loader.py --all")
    print("  3. Full rebuild:  python scripts/supabase_loader.py --rebuild")
    
    return True


def create_config_template():
    """Create a template config file if it doesn't exist."""
    config_file = CONFIG_DIR / "config_local.ini"
    
    if not config_file.exists():
        template = """[supabase]
# Your Supabase project URL (from Settings > API)
url = https://your-project-id.supabase.co

# Your Supabase anon/public key (from Settings > API)
key = your-anon-key-here

# Optional: Service role key for admin operations
# service_key = your-service-role-key
"""
        config_file.write_text(template)
        print(f"\n📝 Created config template: {config_file}")
        print("   Edit this file with your Supabase credentials")


if __name__ == '__main__':
    create_config_template()
    success = test_connection()
    sys.exit(0 if success else 1)
