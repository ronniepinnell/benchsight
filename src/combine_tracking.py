"""
Combine all game tracking files into unified fact tables.
Reads from: data/raw/games/{gid}/{gid}_tracking.xlsx
Outputs: 
  - fact_events_tracking.csv
  - fact_shifts_tracking.csv
  - fact_event_coordinates.csv (placeholder for now)
"""

import pandas as pd
import os
from datetime import datetime

GAMES_DIR = 'data/raw/games'
OUTPUT_DIR = 'data/output'

def load_tracking_file(game_id, game_path):
    """Load events and shifts from a single tracking file."""
    
    # Find tracking file
    tracking_file = None
    for f in os.listdir(game_path):
        if f.endswith('_tracking.xlsx') or f == '_tracking.xlsx':
            tracking_file = os.path.join(game_path, f)
            break
    
    if not tracking_file or not os.path.exists(tracking_file):
        return None, None
    
    try:
        xl = pd.ExcelFile(tracking_file)
        sheets = xl.sheet_names
        
        events_df = None
        shifts_df = None
        
        if 'events' in sheets:
            events_df = pd.read_excel(xl, 'events')
            events_df['game_id'] = game_id
            events_df['_source_file'] = os.path.basename(tracking_file)
        
        if 'shifts' in sheets:
            shifts_df = pd.read_excel(xl, 'shifts')
            shifts_df['game_id'] = game_id
            shifts_df['_source_file'] = os.path.basename(tracking_file)
        
        return events_df, shifts_df
        
    except Exception as e:
        print(f"  ERROR loading {tracking_file}: {e}")
        return None, None


def standardize_events(df):
    """Standardize event columns to match schema."""
    
    # Core columns we want in output
    output_cols = [
        'game_id',
        'event_index',
        'shift_index',
        'linked_event_index',
        'sequence_index',
        'play_index',
        'period',
        'Type',
        'event_detail',
        'event_detail_2',
        'event_successful',
        'event_team_zone',
        'team_venue',
        'player_game_number',
        'player_role',
        'event_start_min',
        'event_start_sec',
        'event_end_min',
        'event_end_sec',
        'time_start_total_seconds',
        'time_end_total_seconds',
        'duration',
        'play_detail1',
        'play_detail_2',
        'play_detail_successful',
        'pressured_pressurer',
        'home_team',
        'away_team',
        '_source_file'
    ]
    
    # Create output dataframe with available columns
    result = pd.DataFrame()
    for col in output_cols:
        if col in df.columns:
            result[col] = df[col]
        else:
            result[col] = None
    
    return result


def standardize_shifts(df):
    """Standardize shift columns to match schema."""
    
    output_cols = [
        'game_id',
        'shift_index',
        'Period',
        'shift_start_min',
        'shift_start_sec',
        'shift_end_min',
        'shift_end_sec',
        'shift_start_total_seconds',
        'shift_end_total_seconds',
        'shift_duration',
        'shift_start_type',
        'shift_stop_type',
        'situation',
        'strength',
        'home_team_strength',
        'away_team_strength',
        'home_goals',
        'away_goals',
        'home_forward_1',
        'home_forward_2',
        'home_forward_3',
        'home_defense_1',
        'home_defense_2',
        'home_goalie',
        'home_xtra',
        'away_forward_1',
        'away_forward_2',
        'away_forward_3',
        'away_defense_1',
        'away_defense_2',
        'away_goalie',
        'away_xtra',
        'home_team',
        'away_team',
        '_source_file'
    ]
    
    result = pd.DataFrame()
    for col in output_cols:
        if col in df.columns:
            result[col] = df[col]
        else:
            result[col] = None
    
    return result


def combine_all_tracking():
    """Main function to combine all tracking files."""
    
    print("=" * 50)
    print("COMBINING ALL TRACKING FILES")
    print("=" * 50)
    
    all_events = []
    all_shifts = []
    
    # Get all game folders
    game_folders = sorted([d for d in os.listdir(GAMES_DIR) 
                          if os.path.isdir(os.path.join(GAMES_DIR, d))])
    
    print(f"\nFound {len(game_folders)} game folders")
    
    for gid in game_folders:
        game_path = os.path.join(GAMES_DIR, gid)
        print(f"\nProcessing {gid}...")
        
        events_df, shifts_df = load_tracking_file(gid, game_path)
        
        if events_df is not None:
            events_df = standardize_events(events_df)
            all_events.append(events_df)
            print(f"  Events: {len(events_df)} rows")
        else:
            print(f"  Events: NONE")
        
        if shifts_df is not None:
            shifts_df = standardize_shifts(shifts_df)
            all_shifts.append(shifts_df)
            print(f"  Shifts: {len(shifts_df)} rows")
        else:
            print(f"  Shifts: NONE")
    
    # Combine all
    print("\n" + "=" * 50)
    print("COMBINING...")
    
    if all_events:
        combined_events = pd.concat(all_events, ignore_index=True)
        combined_events['_export_timestamp'] = datetime.now().isoformat()
        
        # Save
        events_path = os.path.join(OUTPUT_DIR, 'fact_events_tracking.csv')
        combined_events.to_csv(events_path, index=False)
        print(f"fact_events_tracking.csv: {len(combined_events)} rows")
    
    if all_shifts:
        combined_shifts = pd.concat(all_shifts, ignore_index=True)
        combined_shifts['_export_timestamp'] = datetime.now().isoformat()
        
        # Save
        shifts_path = os.path.join(OUTPUT_DIR, 'fact_shifts_tracking.csv')
        combined_shifts.to_csv(shifts_path, index=False)
        print(f"fact_shifts_tracking.csv: {len(combined_shifts)} rows")
    
    # Create empty coordinates table with schema
    coords_df = pd.DataFrame(columns=[
        'event_id', 'game_id', 'entity_type', 'entity_slot', 
        'sequence', 'x', 'y', '_export_timestamp'
    ])
    coords_path = os.path.join(OUTPUT_DIR, 'fact_event_coordinates.csv')
    coords_df.to_csv(coords_path, index=False)
    print(f"fact_event_coordinates.csv: 0 rows (schema only)")
    
    print("\n" + "=" * 50)
    print("DONE")
    print("=" * 50)


if __name__ == '__main__':
    combine_all_tracking()
