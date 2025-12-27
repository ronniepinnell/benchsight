"""
Supabase Upload Script
Uploads all CSV files to Supabase PostgreSQL database.

Usage:
    pip install supabase --break-system-packages
    python src/supabase_upload.py
"""

import os
import pandas as pd
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://uuaowslhpgyiudmbvqze.supabase.co"
SUPABASE_KEY = "sb_publishable_t1lIOebbbCjAu_YBKc8tLg_B_zH_l73"

OUTPUT_DIR = "data/output"

# Table upload order (dimensions first, then facts)
UPLOAD_ORDER = [
    # Core dimensions
    ("dim_league", "dim_league.csv"),
    ("dim_season", "dim_season.csv"),
    ("dim_team", "dim_team.csv"),
    ("dim_player", "dim_player.csv"),
    ("dim_schedule", "dim_schedule.csv"),
    ("dim_rinkboxcoord", "dim_rinkboxcoord.csv"),
    ("dim_rinkcoordzones", "dim_rinkcoordzones.csv"),
    ("dim_video", "dim_video.csv"),
    
    # Lookup dimensions
    ("dim_event_type", "dim_event_type.csv"),
    ("dim_event_detail", "dim_event_detail.csv"),
    ("dim_play_detail", "dim_play_detail.csv"),
    ("dim_strength", "dim_strength.csv"),
    ("dim_situation", "dim_situation.csv"),
    ("dim_position", "dim_position.csv"),
    ("dim_zone", "dim_zone.csv"),
    ("dim_period", "dim_period.csv"),
    ("dim_venue", "dim_venue.csv"),
    ("dim_shot_type", "dim_shot_type.csv"),
    ("dim_pass_type", "dim_pass_type.csv"),
    ("dim_shift_type", "dim_shift_type.csv"),
    ("dim_skill_tier", "dim_skill_tier.csv"),
    ("dim_player_role", "dim_player_role.csv"),
    ("dim_danger_zone", "dim_danger_zone.csv"),
    ("dim_time_bucket", "dim_time_bucket.csv"),
    
    # Fact tables
    ("fact_gameroster", "fact_gameroster.csv"),
    ("fact_events_tracking", "fact_events_tracking.csv"),
    ("fact_events_long", "fact_events_long.csv"),
    ("fact_event_players_tracking", "fact_event_players_tracking.csv"),
    ("fact_shifts_tracking", "fact_shifts_tracking.csv"),
    ("fact_shift_players_tracking", "fact_shift_players_tracking.csv"),
    ("fact_playergames", "fact_playergames.csv"),
    ("fact_box_score_tracking", "fact_box_score_tracking.csv"),
    ("fact_linked_events_tracking", "fact_linked_events_tracking.csv"),
    ("fact_sequences_tracking", "fact_sequences_tracking.csv"),
    ("fact_plays_tracking", "fact_plays_tracking.csv"),
    ("fact_event_coordinates", "fact_event_coordinates.csv"),
]


def clean_dataframe(df):
    """Clean dataframe for Supabase upload."""
    # Replace NaN with None
    df = df.where(pd.notnull(df), None)
    
    # Remove BOM from column names
    df.columns = [col.lstrip('\ufeff') for col in df.columns]
    
    # Convert column names to lowercase
    df.columns = [col.lower() for col in df.columns]
    
    return df


def upload_table(supabase: Client, table_name: str, csv_path: str, batch_size: int = 500):
    """Upload a CSV file to a Supabase table."""
    
    full_path = os.path.join(OUTPUT_DIR, csv_path)
    
    if not os.path.exists(full_path):
        print(f"  SKIP: {csv_path} not found")
        return 0
    
    try:
        df = pd.read_csv(full_path)
        df = clean_dataframe(df)
        
        if len(df) == 0:
            print(f"  SKIP: {table_name} is empty")
            return 0
        
        # Convert to list of dicts
        records = df.to_dict(orient='records')
        
        # Upload in batches
        total_uploaded = 0
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            try:
                result = supabase.table(table_name).insert(batch).execute()
                total_uploaded += len(batch)
            except Exception as e:
                print(f"  ERROR batch {i//batch_size + 1}: {e}")
                # Try one-by-one for failed batch
                for record in batch:
                    try:
                        supabase.table(table_name).insert(record).execute()
                        total_uploaded += 1
                    except Exception as e2:
                        pass  # Skip failed records
        
        print(f"  ✓ {table_name}: {total_uploaded}/{len(records)} rows")
        return total_uploaded
        
    except Exception as e:
        print(f"  ERROR: {table_name} - {e}")
        return 0


def main():
    print("=" * 60)
    print("SUPABASE DATA UPLOAD")
    print("=" * 60)
    print(f"URL: {SUPABASE_URL}")
    print(f"Tables to upload: {len(UPLOAD_ORDER)}")
    print("=" * 60)
    
    # Connect to Supabase
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    total_rows = 0
    
    for table_name, csv_file in UPLOAD_ORDER:
        print(f"\nUploading {table_name}...")
        rows = upload_table(supabase, table_name, csv_file)
        total_rows += rows
    
    print("\n" + "=" * 60)
    print(f"COMPLETE: {total_rows} total rows uploaded")
    print("=" * 60)


if __name__ == "__main__":
    main()
