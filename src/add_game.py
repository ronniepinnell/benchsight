"""
Add Game Script
Adds a single game and its data to Supabase without overwriting existing data.

Usage:
    python3 src/add_game.py 19045
    python3 src/add_game.py 19045 --with-tracking
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime

try:
    from supabase import create_client, Client
except ImportError:
    print("Install supabase: pip3 install supabase")
    sys.exit(1)

# Config
SUPABASE_URL = "https://uuaowslhpgyiudmbvqze.supabase.co"
SUPABASE_KEY = "sb_publishable_t1lIOebbbCjAu_YBKc8tLg_B_zH_l73"
BLB_FILE = "data/BLB_Tables.xlsx"
GAMES_DIR = "data/raw/games"


def clean_value(v):
    """Clean a single value."""
    if v is None:
        return None
    if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
        return None
    if pd.isna(v):
        return None
    if isinstance(v, str) and v.lower() in ('nan', 'none', 'null', ''):
        return None
    return v


def clean_record(record):
    """Clean all values in a record."""
    return {k.lower().lstrip('\ufeff'): clean_value(v) for k, v in record.items()}


def check_game_exists(supabase: Client, game_id: int) -> bool:
    """Check if game already exists in database."""
    result = supabase.table('dim_schedule').select('game_id').eq('game_id', game_id).execute()
    return len(result.data) > 0


def add_schedule(supabase: Client, game_id: int) -> bool:
    """Add game to dim_schedule from BLB_Tables."""
    print(f"  Adding to dim_schedule...")
    
    try:
        df = pd.read_excel(BLB_FILE, sheet_name='dim_schedule')
        game_row = df[df['game_id'] == game_id]
        
        if len(game_row) == 0:
            print(f"  ERROR: Game {game_id} not found in BLB_Tables dim_schedule")
            return False
        
        record = clean_record(game_row.iloc[0].to_dict())
        supabase.table('dim_schedule').insert(record).execute()
        print(f"  ✓ dim_schedule: 1 row")
        return True
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def add_roster(supabase: Client, game_id: int) -> int:
    """Add game roster from BLB_Tables."""
    print(f"  Adding to fact_gameroster...")
    
    try:
        df = pd.read_excel(BLB_FILE, sheet_name='fact_gameroster')
        game_rows = df[df['game_id'] == game_id]
        
        if len(game_rows) == 0:
            print(f"  WARNING: No roster found for game {game_id}")
            return 0
        
        records = [clean_record(r) for r in game_rows.to_dict(orient='records')]
        
        # Upload in batches
        batch_size = 50
        total = 0
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            supabase.table('fact_gameroster').insert(batch).execute()
            total += len(batch)
        
        print(f"  ✓ fact_gameroster: {total} rows")
        return total
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return 0


def add_tracking(supabase: Client, game_id: int) -> dict:
    """Add tracking data from game folder."""
    results = {'events': 0, 'shifts': 0}
    
    game_path = os.path.join(GAMES_DIR, str(game_id))
    if not os.path.exists(game_path):
        print(f"  No tracking folder found: {game_path}")
        return results
    
    # Find tracking file
    tracking_file = None
    for f in os.listdir(game_path):
        if f.endswith('_tracking.xlsx') or f == '_tracking.xlsx':
            tracking_file = os.path.join(game_path, f)
            break
    
    if not tracking_file:
        print(f"  No tracking file found in {game_path}")
        return results
    
    print(f"  Loading tracking from {tracking_file}...")
    
    try:
        xl = pd.ExcelFile(tracking_file)
        
        # Events
        if 'events' in xl.sheet_names:
            print(f"  Adding to fact_events_tracking...")
            df = pd.read_excel(xl, 'events')
            df['game_id'] = game_id
            df['_source_file'] = os.path.basename(tracking_file)
            df['_export_timestamp'] = datetime.now().isoformat()
            
            records = [clean_record(r) for r in df.to_dict(orient='records')]
            
            batch_size = 100
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                try:
                    supabase.table('fact_events_tracking').insert(batch).execute()
                    results['events'] += len(batch)
                except Exception as e:
                    print(f"    Batch error: {e}")
            
            print(f"  ✓ fact_events_tracking: {results['events']} rows")
        
        # Shifts
        if 'shifts' in xl.sheet_names:
            print(f"  Adding to fact_shifts_tracking...")
            df = pd.read_excel(xl, 'shifts')
            df['game_id'] = game_id
            df['_source_file'] = os.path.basename(tracking_file)
            df['_export_timestamp'] = datetime.now().isoformat()
            
            records = [clean_record(r) for r in df.to_dict(orient='records')]
            
            for i in range(0, len(records), 50):
                batch = records[i:i + 50]
                try:
                    supabase.table('fact_shifts_tracking').insert(batch).execute()
                    results['shifts'] += len(batch)
                except Exception as e:
                    print(f"    Batch error: {e}")
            
            print(f"  ✓ fact_shifts_tracking: {results['shifts']} rows")
        
    except Exception as e:
        print(f"  ERROR loading tracking: {e}")
    
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 src/add_game.py <game_id> [--with-tracking]")
        print("Example: python3 src/add_game.py 19045")
        print("         python3 src/add_game.py 19045 --with-tracking")
        sys.exit(1)
    
    game_id = int(sys.argv[1])
    with_tracking = '--with-tracking' in sys.argv
    
    print("=" * 50)
    print(f"ADD GAME: {game_id}")
    print("=" * 50)
    
    # Connect
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Check if exists
    if check_game_exists(supabase, game_id):
        print(f"WARNING: Game {game_id} already exists in database!")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
    
    # Add schedule
    if not add_schedule(supabase, game_id):
        print("Failed to add schedule. Aborting.")
        sys.exit(1)
    
    # Add roster
    add_roster(supabase, game_id)
    
    # Add tracking if requested
    if with_tracking:
        add_tracking(supabase, game_id)
    else:
        print(f"\n  TIP: Add --with-tracking to also upload events/shifts")
    
    print("\n" + "=" * 50)
    print("DONE")
    print("=" * 50)


if __name__ == "__main__":
    main()
