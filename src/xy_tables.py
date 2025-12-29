#!/usr/bin/env python3
"""
XY Tables - Player, Puck, and Shot coordinate tables.

Creates both long and wide format tables for:
- Player XY (up to 10 points per player per event)
- Puck XY (up to 10 points per event)
- Shot XY (shot location with net_location FK)

Also creates dimension tables:
- dim_net_location (target location on net)
- dim_rink_coord (coordinate zone descriptors)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path('data/output')


def create_dim_net_location():
    """Create dimension table for net target locations."""
    logger.info("Creating dim_net_location...")
    
    rows = [
        {'net_location_id': 'NL0001', 'net_location_code': 'GH', 'net_location_name': 'Glove High', 'x_pct': 0.25, 'y_pct': 0.75},
        {'net_location_id': 'NL0002', 'net_location_code': 'GL', 'net_location_name': 'Glove Low', 'x_pct': 0.25, 'y_pct': 0.25},
        {'net_location_id': 'NL0003', 'net_location_code': 'BH', 'net_location_name': 'Blocker High', 'x_pct': 0.75, 'y_pct': 0.75},
        {'net_location_id': 'NL0004', 'net_location_code': 'BL', 'net_location_name': 'Blocker Low', 'x_pct': 0.75, 'y_pct': 0.25},
        {'net_location_id': 'NL0005', 'net_location_code': '5H', 'net_location_name': 'Five Hole', 'x_pct': 0.50, 'y_pct': 0.10},
        {'net_location_id': 'NL0006', 'net_location_code': 'TL', 'net_location_name': 'Top Left', 'x_pct': 0.15, 'y_pct': 0.90},
        {'net_location_id': 'NL0007', 'net_location_code': 'TR', 'net_location_name': 'Top Right', 'x_pct': 0.85, 'y_pct': 0.90},
        {'net_location_id': 'NL0008', 'net_location_code': 'TM', 'net_location_name': 'Top Middle', 'x_pct': 0.50, 'y_pct': 0.90},
        {'net_location_id': 'NL0009', 'net_location_code': 'ML', 'net_location_name': 'Mid Left', 'x_pct': 0.15, 'y_pct': 0.50},
        {'net_location_id': 'NL0010', 'net_location_code': 'MR', 'net_location_name': 'Mid Right', 'x_pct': 0.85, 'y_pct': 0.50},
    ]
    
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / 'dim_net_location.csv', index=False)
    logger.info(f"  ✓ dim_net_location: {len(df)} rows")
    return df


def create_dim_rink_coord():
    """Create dimension table for rink coordinate zones."""
    logger.info("Creating dim_rink_coord...")
    
    # Rink zones based on standard hockey rink (200ft x 85ft, centered at 0,0)
    rows = [
        # Offensive zone
        {'rink_coord_id': 'RC0001', 'rink_coord_code': 'OZ_SLOT', 'rink_coord_name': 'Offensive Zone - Slot', 'x_min': 54, 'x_max': 89, 'y_min': -22, 'y_max': 22},
        {'rink_coord_id': 'RC0002', 'rink_coord_code': 'OZ_HIGH', 'rink_coord_name': 'Offensive Zone - High', 'x_min': 25, 'x_max': 54, 'y_min': -42, 'y_max': 42},
        {'rink_coord_id': 'RC0003', 'rink_coord_code': 'OZ_LEFT', 'rink_coord_name': 'Offensive Zone - Left Wing', 'x_min': 54, 'x_max': 89, 'y_min': 22, 'y_max': 42},
        {'rink_coord_id': 'RC0004', 'rink_coord_code': 'OZ_RIGHT', 'rink_coord_name': 'Offensive Zone - Right Wing', 'x_min': 54, 'x_max': 89, 'y_min': -42, 'y_max': -22},
        {'rink_coord_id': 'RC0005', 'rink_coord_code': 'OZ_CREASE', 'rink_coord_name': 'Offensive Zone - Crease', 'x_min': 84, 'x_max': 100, 'y_min': -4, 'y_max': 4},
        {'rink_coord_id': 'RC0006', 'rink_coord_code': 'OZ_CORNER_L', 'rink_coord_name': 'Offensive Zone - Left Corner', 'x_min': 72, 'x_max': 100, 'y_min': 26, 'y_max': 42},
        {'rink_coord_id': 'RC0007', 'rink_coord_code': 'OZ_CORNER_R', 'rink_coord_name': 'Offensive Zone - Right Corner', 'x_min': 72, 'x_max': 100, 'y_min': -42, 'y_max': -26},
        
        # Neutral zone
        {'rink_coord_id': 'RC0008', 'rink_coord_code': 'NZ_CENTER', 'rink_coord_name': 'Neutral Zone - Center', 'x_min': -25, 'x_max': 25, 'y_min': -22, 'y_max': 22},
        {'rink_coord_id': 'RC0009', 'rink_coord_code': 'NZ_LEFT', 'rink_coord_name': 'Neutral Zone - Left', 'x_min': -25, 'x_max': 25, 'y_min': 22, 'y_max': 42},
        {'rink_coord_id': 'RC0010', 'rink_coord_code': 'NZ_RIGHT', 'rink_coord_name': 'Neutral Zone - Right', 'x_min': -25, 'x_max': 25, 'y_min': -42, 'y_max': -22},
        
        # Defensive zone
        {'rink_coord_id': 'RC0011', 'rink_coord_code': 'DZ_SLOT', 'rink_coord_name': 'Defensive Zone - Slot', 'x_min': -89, 'x_max': -54, 'y_min': -22, 'y_max': 22},
        {'rink_coord_id': 'RC0012', 'rink_coord_code': 'DZ_HIGH', 'rink_coord_name': 'Defensive Zone - High', 'x_min': -54, 'x_max': -25, 'y_min': -42, 'y_max': 42},
        {'rink_coord_id': 'RC0013', 'rink_coord_code': 'DZ_LEFT', 'rink_coord_name': 'Defensive Zone - Left Wing', 'x_min': -89, 'x_max': -54, 'y_min': 22, 'y_max': 42},
        {'rink_coord_id': 'RC0014', 'rink_coord_code': 'DZ_RIGHT', 'rink_coord_name': 'Defensive Zone - Right Wing', 'x_min': -89, 'x_max': -54, 'y_min': -42, 'y_max': -22},
        {'rink_coord_id': 'RC0015', 'rink_coord_code': 'DZ_CREASE', 'rink_coord_name': 'Defensive Zone - Crease', 'x_min': -100, 'x_max': -84, 'y_min': -4, 'y_max': 4},
        {'rink_coord_id': 'RC0016', 'rink_coord_code': 'DZ_CORNER_L', 'rink_coord_name': 'Defensive Zone - Left Corner', 'x_min': -100, 'x_max': -72, 'y_min': 26, 'y_max': 42},
        {'rink_coord_id': 'RC0017', 'rink_coord_code': 'DZ_CORNER_R', 'rink_coord_name': 'Defensive Zone - Right Corner', 'x_min': -100, 'x_max': -72, 'y_min': -42, 'y_max': -26},
        
        # Behind nets
        {'rink_coord_id': 'RC0018', 'rink_coord_code': 'OZ_BEHIND', 'rink_coord_name': 'Behind Offensive Net', 'x_min': 89, 'x_max': 100, 'y_min': -11, 'y_max': 11},
        {'rink_coord_id': 'RC0019', 'rink_coord_code': 'DZ_BEHIND', 'rink_coord_name': 'Behind Defensive Net', 'x_min': -100, 'x_max': -89, 'y_min': -11, 'y_max': 11},
    ]
    
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / 'dim_rink_coord.csv', index=False)
    logger.info(f"  ✓ dim_rink_coord: {len(df)} rows")
    return df


def get_rink_coord_id(x, y, rink_coords_df):
    """Determine rink_coord_id from x,y coordinates."""
    if pd.isna(x) or pd.isna(y):
        return None
    
    for _, row in rink_coords_df.iterrows():
        if row['x_min'] <= x <= row['x_max'] and row['y_min'] <= y <= row['y_max']:
            return row['rink_coord_id']
    return None


def create_fact_player_xy_long():
    """Create empty player XY table (long format)."""
    logger.info("Creating fact_player_xy_long schema...")
    
    columns = [
        'player_xy_key',      # PXY{game_id}{event_index}{player_id}{point_num}
        'game_id',
        'event_index',
        'event_key',
        'player_id',
        'player_key',
        'team_id',
        'team_venue',
        'point_number',       # 1-10
        'x',
        'y',
        'timestamp',          # Video timestamp for this point
        'rink_coord_id',      # FK to dim_rink_coord
        'rink_coord_id_home', # FK based on home perspective
        'rink_coord_id_away', # FK based on away perspective
    ]
    
    df = pd.DataFrame(columns=columns)
    df.to_csv(OUTPUT_DIR / 'fact_player_xy_long.csv', index=False)
    logger.info(f"  ✓ fact_player_xy_long: schema created (0 rows - no data yet)")
    return df


def create_fact_player_xy_wide():
    """Create empty player XY table (wide format)."""
    logger.info("Creating fact_player_xy_wide schema...")
    
    columns = [
        'player_xy_key',      # PXY{game_id}{event_index}{player_id}
        'game_id',
        'event_index',
        'event_key',
        'player_id',
        'player_key',
        'team_id',
        'team_venue',
        'point_count',        # How many points in this event (1-10)
    ]
    
    # Add x1-x10, y1-y10, timestamp1-10, rink_coord_id_1-10
    for i in range(1, 11):
        columns.extend([
            f'x_{i}',
            f'y_{i}',
            f'timestamp_{i}',
            f'rink_coord_id_{i}',
        ])
    
    df = pd.DataFrame(columns=columns)
    df.to_csv(OUTPUT_DIR / 'fact_player_xy_wide.csv', index=False)
    logger.info(f"  ✓ fact_player_xy_wide: schema created (0 rows - no data yet)")
    return df


def create_fact_puck_xy_long():
    """Create empty puck XY table (long format)."""
    logger.info("Creating fact_puck_xy_long schema...")
    
    columns = [
        'puck_xy_key',        # PKY{game_id}{event_index}{point_num}
        'game_id',
        'event_index',
        'event_key',
        'point_number',       # 1-10
        'x',
        'y',
        'z',                  # Height (for aerial pucks)
        'timestamp',
        'rink_coord_id',
        'rink_coord_id_home',
        'rink_coord_id_away',
    ]
    
    df = pd.DataFrame(columns=columns)
    df.to_csv(OUTPUT_DIR / 'fact_puck_xy_long.csv', index=False)
    logger.info(f"  ✓ fact_puck_xy_long: schema created (0 rows - no data yet)")
    return df


def create_fact_puck_xy_wide():
    """Create empty puck XY table (wide format)."""
    logger.info("Creating fact_puck_xy_wide schema...")
    
    columns = [
        'puck_xy_key',        # PKY{game_id}{event_index}
        'game_id',
        'event_index',
        'event_key',
        'point_count',
    ]
    
    for i in range(1, 11):
        columns.extend([
            f'x_{i}',
            f'y_{i}',
            f'z_{i}',
            f'timestamp_{i}',
            f'rink_coord_id_{i}',
        ])
    
    df = pd.DataFrame(columns=columns)
    df.to_csv(OUTPUT_DIR / 'fact_puck_xy_wide.csv', index=False)
    logger.info(f"  ✓ fact_puck_xy_wide: schema created (0 rows - no data yet)")
    return df


def create_fact_shot_xy():
    """Create empty shot XY table."""
    logger.info("Creating fact_shot_xy schema...")
    
    columns = [
        'shot_xy_key',        # SXY{game_id}{event_index}
        'game_id',
        'event_index',
        'event_key',
        'player_id',
        'player_key',
        'team_id',
        'team_venue',
        'period',
        'period_id',
        
        # Shot origin
        'shot_x',
        'shot_y',
        'shot_rink_coord_id',
        'shot_rink_coord_id_home',
        'shot_rink_coord_id_away',
        'shot_distance',      # Distance to net
        'shot_angle',         # Angle to net center
        
        # Shot target (on net)
        'target_x',           # X position on net (0-1)
        'target_y',           # Y position on net (0-1)
        'net_location_id',    # FK to dim_net_location
        
        # Shot result
        'shot_type',          # Wrist, slap, snap, backhand, etc.
        'shot_result',        # Goal, save, miss, block
        'is_goal',
        'is_on_net',
        
        # Context
        'strength_id',
        'goalie_player_id',
        'xg',                 # Expected goal value
        
        # Video
        'running_video_time',
    ]
    
    df = pd.DataFrame(columns=columns)
    df.to_csv(OUTPUT_DIR / 'fact_shot_xy.csv', index=False)
    logger.info(f"  ✓ fact_shot_xy: schema created (0 rows - no data yet)")
    return df


def main():
    print("=" * 70)
    print("XY TABLES BUILDER")
    print("=" * 70)
    
    # Create dimension tables
    create_dim_net_location()
    create_dim_rink_coord()
    
    # Create fact table schemas (empty - no data yet)
    create_fact_player_xy_long()
    create_fact_player_xy_wide()
    create_fact_puck_xy_long()
    create_fact_puck_xy_wide()
    create_fact_shot_xy()
    
    print("\n" + "=" * 70)
    print("COMPLETE - XY table schemas created")
    print("Tables are empty, ready for data population")
    print("=" * 70)


if __name__ == '__main__':
    main()
