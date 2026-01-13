#!/usr/bin/env python3
"""
Supabase Database Explorer

Explores your Supabase database and shows:
- All tables and their row counts
- Sample data from each table
- View definitions
- Schema information
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config_loader import get_config

def get_all_tables_via_sql(client) -> List[str]:
    """Get all tables by querying PostgreSQL information_schema."""
    try:
        # Query information_schema to get all user tables
        # Exclude system schemas
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
        
        # Use RPC or direct SQL execution
        # Supabase Python client doesn't support raw SQL directly, so we'll try a different approach
        # We can use the REST API directly or try to query pg_catalog
        
        # Alternative: Try to get tables by querying pg_catalog via a function
        # Or we can try to query each table and see what exists
        
        # For now, let's try to use the REST API to get schema info
        # Actually, let's just try querying common patterns and also try to discover
        
        return []
    except Exception as e:
        print(f"Error querying schema: {e}")
        return []

def discover_tables_by_querying(client, known_prefixes: List[str] = None) -> List[str]:
    """Discover tables by trying common naming patterns."""
    if known_prefixes is None:
        known_prefixes = [
            'dim_', 'fact_', 'stage_', 'v_', 'vw_', 
            'fct_', 'stg_', 'tmp_', 'tbl_'
        ]
    
    discovered = []
    
    # Try to query information_schema via a view or function
    # Since we can't do raw SQL, let's try querying pg_tables if available
    # Or we can try common table names from the codebase
    
    # Actually, let's query the Supabase REST API metadata endpoint
    # Or use the management API
    
    return discovered

def get_table_info(client, table_name: str) -> Dict[str, Any]:
    """Get information about a table."""
    info = {
        'name': table_name,
        'count': None,
        'sample': None,
        'error': None
    }
    
    try:
        # Get row count
        count_result = client.table(table_name).select('*', count='exact').limit(0).execute()
        info['count'] = count_result.count
    except Exception as e:
        info['error'] = str(e)
        return info
    
    try:
        # Get sample data (first 3 rows)
        sample_result = client.table(table_name).select('*').limit(3).execute()
        if sample_result.data:
            info['sample'] = sample_result.data
    except Exception as e:
        if not info['error']:  # Don't overwrite count error
            info['error'] = str(e)
    
    return info

def get_all_tables_from_sql_file(client) -> List[str]:
    """Try to get table names from SQL files in the project."""
    sql_dir = project_root / "sql"
    tables = set()
    
    # Look for CREATE TABLE statements in SQL files
    for sql_file in sql_dir.rglob("*.sql"):
        try:
            content = sql_file.read_text()
            # Find CREATE TABLE statements
            import re
            matches = re.findall(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:public\.)?(\w+)', content, re.IGNORECASE)
            tables.update(matches)
            
            # Also find CREATE VIEW statements
            view_matches = re.findall(r'CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:public\.)?(\w+)', content, re.IGNORECASE)
            tables.update(view_matches)
        except:
            pass
    
    return sorted(list(tables))

def test_table_exists(client, table_name: str) -> bool:
    """Test if a table exists by trying to query it."""
    try:
        result = client.table(table_name).select('*', count='exact').limit(0).execute()
        return True
    except:
        return False

def explore_database():
    """Main exploration function."""
    print("=" * 80)
    print("SUPABASE DATABASE EXPLORER")
    print("=" * 80)
    print()
    
    # Load config
    try:
        config = get_config()
        if not config.is_configured:
            print("✗ Supabase credentials not configured")
            return False
    except Exception as e:
        print(f"✗ Failed to load config: {e}")
        return False
    
    # Connect
    try:
        from supabase import create_client
        client = create_client(config.supabase_url, config.supabase_service_key)
        print(f"✓ Connected to: {config.supabase_url}")
        print()
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False
    
    # Get table names from SQL files
    print("Discovering tables from SQL files...")
    sql_tables = get_all_tables_from_sql_file(client)
    print(f"  Found {len(sql_tables)} table/view names in SQL files")
    print()
    
    # Test which tables actually exist
    print("Testing which tables exist in database...")
    print("  (This may take a moment for 130+ tables...)")
    print()
    
    existing_tables = []
    tested = 0
    
    for table_name in sql_tables:
        tested += 1
        if tested % 20 == 0:
            print(f"  Tested {tested}/{len(sql_tables)} tables...", end='\r')
        
        if test_table_exists(client, table_name):
            existing_tables.append(table_name)
    
    print(f"  Tested {tested} tables, found {len(existing_tables)} existing tables")
    print()
    
    if not existing_tables:
        print("⚠ No tables found from SQL files. Trying alternative discovery method...")
        # Fallback: try some common table names
        common_tables = [
            'dim_schedule', 'dim_league', 'dim_team', 'dim_player', 'dim_season',
            'dim_game_type', 'dim_venue', 'dim_play_detail', 'dim_player_role',
            'fact_events', 'fact_shifts', 'fact_game_stats', 'fact_player_game_stats',
        ]
        
        for table_name in common_tables:
            if test_table_exists(client, table_name):
                existing_tables.append(table_name)
    
    if not existing_tables:
        print("✗ Could not discover any tables")
        print("  This might mean:")
        print("    - Tables don't exist yet (run upload.py)")
        print("    - RLS is blocking access")
        print("    - Service key lacks permissions")
        return False
    
    print(f"✓ Found {len(existing_tables)} accessible tables")
    print()
    print("=" * 80)
    print("TABLE SUMMARY")
    print("=" * 80)
    print()
    
    # Get info for each table (show progress for large numbers)
    table_info_list = []
    total = len(existing_tables)
    
    for i, table_name in enumerate(sorted(existing_tables), 1):
        print(f"Analyzing {table_name} ({i}/{total})...", end=' ', flush=True)
        info = get_table_info(client, table_name)
        table_info_list.append(info)
        
        if info['error']:
            print(f"✗ Error: {info['error'][:50]}")
        elif info['count'] is not None:
            print(f"✓ {info['count']:,} rows")
        else:
            print("✓ (count unavailable)")
    
    print()
    print("=" * 80)
    print("DETAILED TABLE INFORMATION")
    print("=" * 80)
    print()
    
    # Group by prefix for easier reading
    by_prefix = {}
    for info in table_info_list:
        prefix = info['name'].split('_')[0] if '_' in info['name'] else 'other'
        if prefix not in by_prefix:
            by_prefix[prefix] = []
        by_prefix[prefix].append(info)
    
    for prefix in sorted(by_prefix.keys()):
        print(f"\n📁 {prefix.upper()} Tables ({len(by_prefix[prefix])} tables)")
        print("=" * 80)
        
        for info in sorted(by_prefix[prefix], key=lambda x: x['name']):
            print(f"\n  📊 {info['name']}")
            
            if info['error']:
                print(f"    Error: {info['error']}")
            else:
                if info['count'] is not None:
                    print(f"    Rows: {info['count']:,}")
                
                if info['sample']:
                    print(f"    Sample: {len(info['sample'])} rows available")
                    # Show first row column names
                    if info['sample']:
                        cols = list(info['sample'][0].keys())[:5]
                        print(f"    Columns: {', '.join(cols)}" + (f" ... (+{len(info['sample'][0].keys()) - 5} more)" if len(info['sample'][0].keys()) > 5 else ""))
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total tables found: {len(existing_tables)}")
    print(f"Total rows across all tables: {sum(i['count'] or 0 for i in table_info_list):,}")
    print()
    print("=" * 80)
    print("EXPLORATION COMPLETE")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = explore_database()
    sys.exit(0 if success else 1)
