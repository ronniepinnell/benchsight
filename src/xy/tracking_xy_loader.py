#!/usr/bin/env python3
"""
Tracking XY Loader - Load XY data from tracking Excel files with XY sheets.

This module extends the ETL to load XY data from tracking files that have:
- `xy_puck` sheet (long format - one row per point per event)
- `xy_player` sheet (long format - one row per point per player per event)
- `video` sheet (video data for fact_video table)
- `events` sheet with additional XY columns:
  - highlight video flag and video URL
  - puck_xy_start, puck_xy_stop (non-adjusted - don't use adjusted columns)
  - net_x, net_y (shot target location)
  - is_xy_adjusted (flag indicating if XY data is adjusted)

This is designed to be optional and not break existing ETL.

USAGE:
    from src.xy.tracking_xy_loader import load_tracking_xy_data
    
    # Load XY data from a tracking file
    xy_data = load_tracking_xy_data(
        tracking_path=Path('data/raw/games/19038/19038_tracking.xlsx'),
        game_id='19038',
        test_mode=True  # Don't add to current tables, just return data
    )
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, Dict, List
import logging
from src.core.table_writer import save_output_table

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path('data/output')

# Rink constants
GOAL_LINE_X = 89.0
POINT_NUMBERS = list(range(1, 11))


def calculate_distance_to_net(x: float, y: float, attacking_right: bool = True) -> Optional[float]:
    """Calculate distance from point to net center."""
    if pd.isna(x) or pd.isna(y):
        return None
    goal_x = GOAL_LINE_X if attacking_right else -GOAL_LINE_X
    return round(np.sqrt((goal_x - x)**2 + y**2), 1)


def calculate_angle_to_net(x: float, y: float, attacking_right: bool = True) -> Optional[float]:
    """Calculate angle from point to net center (in degrees)."""
    if pd.isna(x) or pd.isna(y):
        return None
    goal_x = GOAL_LINE_X if attacking_right else -GOAL_LINE_X
    dx = goal_x - x
    dy = y
    if dx <= 0:
        return None
    angle = np.degrees(np.arctan2(abs(dy), dx))
    return round(angle, 1)


def load_tracking_xy_puck_long(tracking_path: Path, game_id: str, test_mode: bool = False) -> pd.DataFrame:
    """
    Load puck XY data from 'xy_puck' sheet in tracking file (long format).
    
    Expected columns:
    - event_id or event_index (required)
    - game_id (optional, will be set)
    - point_number (required, 1-10)
    - x, y (required)
    - is_stop (optional - flag indicating this is the stop point)
    - timestamp (optional)
    """
    if not tracking_path.exists():
        logger.warning(f"  Tracking file not found: {tracking_path}")
        return pd.DataFrame()
    
    try:
        xl = pd.ExcelFile(tracking_path)
        if 'xy_puck' not in xl.sheet_names:
            logger.info("  No 'xy_puck' sheet found in tracking file")
            return pd.DataFrame()
        
        df = pd.read_excel(tracking_path, sheet_name='xy_puck', dtype=str)
        logger.info(f"  Loaded {len(df)} rows from 'xy_puck' sheet")
        
        if len(df) == 0:
            return pd.DataFrame()
        
        # Normalize column names (case-insensitive matching)
        df.columns = df.columns.str.strip()
        
        # Build column mapping dictionary
        col_mapping = {}
        
        # Map event identifier columns
        for col in df.columns:
            col_lower = str(col).lower()
            if 'event_index' in col_lower and 'event_id' not in df.columns:
                col_mapping[col] = 'event_id'
            elif 'event_key' in col_lower and 'event_id' not in df.columns:
                col_mapping[col] = 'event_id'
        
        # Map point number columns
        for col in df.columns:
            col_lower = str(col).lower()
            if ('point_num' in col_lower or 'point' == col_lower or 'xy_slot' == col_lower or 'slot' == col_lower) and 'point_number' not in df.columns:
                col_mapping[col] = 'point_number'

        # Map X coordinate columns
        for col in df.columns:
            col_lower = str(col).lower()
            if any(pattern in col_lower for pattern in ['puck_x', 'coord_x', '_x']) and 'x' not in df.columns:
                # Prioritize puck_x over coord_x
                if 'puck' in col_lower:
                    if 'x' not in col_mapping.values():
                        col_mapping[col] = 'x'
                elif 'coord' in col_lower and 'x' not in col_mapping.values():
                    col_mapping[col] = 'x'
                elif col_lower.endswith('_x') and 'x' not in col_mapping.values():
                    col_mapping[col] = 'x'
        
        # Map Y coordinate columns
        for col in df.columns:
            col_lower = str(col).lower()
            if any(pattern in col_lower for pattern in ['puck_y', 'coord_y', '_y']) and 'y' not in df.columns:
                # Prioritize puck_y over coord_y
                if 'puck' in col_lower:
                    if 'y' not in col_mapping.values():
                        col_mapping[col] = 'y'
                elif 'coord' in col_lower and 'y' not in col_mapping.values():
                    col_mapping[col] = 'y'
                elif col_lower.endswith('_y') and 'y' not in col_mapping.values():
                    col_mapping[col] = 'y'
        
        # Map is_stop flag columns
        for col in df.columns:
            col_lower = str(col).lower()
            if any(pattern in col_lower for pattern in ['is_stop', 'stop_point', 'stop_flag']) and 'is_stop' not in df.columns:
                col_mapping[col] = 'is_stop'
        
        # Apply mappings
        for old_col, new_col in col_mapping.items():
            if old_col in df.columns:
                df[new_col] = df[old_col]
        
        # Ensure game_id and event_id
        if 'game_id' not in df.columns:
            df['game_id'] = game_id
        else:
            df['game_id'] = df['game_id'].fillna(game_id)
        
        # Convert event_index to event_id if needed
        # The column mapping may have copied event_index values into event_id,
        # so also check if event_id values are raw indices (no 'EV' prefix)
        from src.core.key_utils import format_key
        if 'event_id' in df.columns:
            sample_eid = str(df['event_id'].iloc[0]).strip() if len(df) > 0 else ''
            if sample_eid and not sample_eid.startswith('EV'):
                # event_id contains raw event_index values - format them
                source_col = 'event_index' if 'event_index' in df.columns else 'event_id'
                df['event_id'] = df[source_col].apply(
                    lambda v: format_key('EV', game_id, str(v).strip())
                )
        elif 'event_index' in df.columns:
            df['event_id'] = df['event_index'].apply(
                lambda v: format_key('EV', game_id, str(v).strip())
            )

        # Required columns check
        required = ['event_id', 'game_id', 'x', 'y']
        missing = [col for col in required if col not in df.columns]
        if missing:
            logger.error(f"  Missing required columns: {missing}")
            return pd.DataFrame()

        # Ensure point_number exists (if missing, infer from row number or sequence)
        if 'point_number' not in df.columns:
            # Try to infer from index or create sequential numbers per event
            if 'event_id' in df.columns:
                df = df.sort_values(['event_id', df.index.name if df.index.name else 'index']).reset_index(drop=True)
                df['point_number'] = df.groupby('event_id').cumcount() + 1
            else:
                df['point_number'] = df.groupby(df.index).cumcount() + 1
            logger.warning("  point_number not found, inferred from row sequence")
        
        # Ensure point_number is numeric
        if 'point_number' in df.columns:
            df['point_number'] = pd.to_numeric(df['point_number'], errors='coerce').fillna(1).astype(int)
        
        # Build records
        records = []
        for idx, row in df.iterrows():
            event_id = str(row.get('event_id', ''))
            if not event_id or event_id == 'nan':
                logger.debug(f"  Row {idx}: Skipping - missing event_id")
                continue
            
            point_num = int(row.get('point_number', 1))
            x = row.get('x')
            y = row.get('y')
            
            # Skip if coordinates are missing or invalid
            if pd.isna(x) or pd.isna(y):
                continue
            
            x_str = str(x).strip()
            y_str = str(y).strip()
            
            if x_str == '' or y_str == '' or x_str.lower() == 'nan' or y_str.lower() == 'nan':
                continue
            
            try:
                x_val = float(x)
                y_val = float(y)
                
                # Validate coordinates are reasonable (rink is roughly -100 to 100 x, -42.5 to 42.5 y)
                if abs(x_val) > 200 or abs(y_val) > 100:
                    logger.debug(f"  Row {idx}: Skipping - coordinates out of range: ({x_val}, {y_val})")
                    continue
                    
            except (ValueError, TypeError) as e:
                logger.debug(f"  Row {idx}: Skipping - invalid coordinates: {e}")
                continue
            
            # Determine is_start flag
            is_start = 0
            is_start_val = row.get('is_start') if 'is_start' in df.columns else None
            if pd.notna(is_start_val):
                is_start_str = str(is_start_val).strip().lower()
                if is_start_str in ['true', '1', 'yes', 't']:
                    is_start = 1
                try:
                    if int(float(is_start_val)) == 1:
                        is_start = 1
                except:
                    pass

            # Determine is_stop flag
            is_stop = 0
            is_stop_val = row.get('is_stop') if 'is_stop' in df.columns else None

            if pd.notna(is_stop_val):
                is_stop_str = str(is_stop_val).strip().lower()
                if is_stop_str in ['true', '1', 'yes', 't']:
                    is_stop = 1
                try:
                    if int(float(is_stop_val)) == 1:
                        is_stop = 1
                except:
                    pass

            # Try alternative stop column names
            if is_stop == 0:
                for col in df.columns:
                    if 'stop' in str(col).lower():
                        stop_val = row.get(col)
                        if pd.notna(stop_val):
                            stop_str = str(stop_val).strip().lower()
                            if stop_str in ['true', '1', 'yes', 't']:
                                is_stop = 1
                                break
                            try:
                                if int(float(stop_val)) == 1:
                                    is_stop = 1
                                    break
                            except:
                                pass

            # Get timestamp if available
            timestamp = None
            timestamp_cols = [c for c in df.columns if 'timestamp' in str(c).lower() or 'time' in str(c).lower()]
            for col in timestamp_cols:
                ts_val = row.get(col)
                if pd.notna(ts_val) and str(ts_val).strip() and str(ts_val).lower() != 'nan':
                    timestamp = str(ts_val).strip()
                    break

            record = {
                'puck_xy_key': f"PKL{game_id}{str(event_id)[-5:]}{point_num:02d}",
                'event_id': event_id,
                'game_id': game_id,
                'point_number': point_num,
                'x': x_val,
                'y': y_val,
                'is_start': is_start,
                'is_stop': is_stop,
                'distance_to_net': calculate_distance_to_net(x_val, y_val),
                'angle_to_net': calculate_angle_to_net(x_val, y_val),
                'timestamp': timestamp,
                '_export_timestamp': datetime.now().isoformat()
            }
            
            records.append(record)
        
        if records:
            result_df = pd.DataFrame(records)
            
            if not test_mode:
                save_output_table(result_df, 'fact_puck_xy_long', OUTPUT_DIR)
            
            logger.info(f"  Created {len(records):,} puck XY long records")
            return result_df
        else:
            logger.warning("  No puck XY records created")
            return pd.DataFrame()
        
    except Exception as e:
        logger.error(f"  Error loading xy_puck sheet: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def load_tracking_xy_player_long(tracking_path: Path, game_id: str, test_mode: bool = False) -> pd.DataFrame:
    """
    Load player XY data from 'xy_player' sheet in tracking file (long format).
    
    Expected columns:
    - event_id or event_index (required)
    - game_id (optional, will be set)
    - player_id (required)
    - player_name, player_role (optional)
    - point_number (required, 1-10)
    - x, y (required)
    - is_stop (optional)
    - timestamp (optional)
    """
    if not tracking_path.exists():
        logger.warning(f"  Tracking file not found: {tracking_path}")
        return pd.DataFrame()
    
    try:
        xl = pd.ExcelFile(tracking_path)
        if 'xy_player' not in xl.sheet_names:
            logger.info("  No 'xy_player' sheet found in tracking file")
            return pd.DataFrame()
        
        df = pd.read_excel(tracking_path, sheet_name='xy_player', dtype=str)
        logger.info(f"  Loaded {len(df)} rows from 'xy_player' sheet")
        
        if len(df) == 0:
            return pd.DataFrame()
        
        # Normalize column names (case-insensitive matching)
        df.columns = df.columns.str.strip()
        
        # Build column mapping dictionary
        col_mapping = {}
        
        # Map event identifier columns
        for col in df.columns:
            col_lower = str(col).lower()
            if 'event_index' in col_lower and 'event_id' not in df.columns:
                col_mapping[col] = 'event_id'
            elif 'event_key' in col_lower and 'event_id' not in df.columns:
                col_mapping[col] = 'event_id'
        
        # Map player identifier columns (prioritize player_id, then player_game, then player_name)
        for col in df.columns:
            col_lower = str(col).lower()
            if 'player_id' in col_lower or ('player' in col_lower and 'id' in col_lower):
                if 'player_id' not in col_mapping.values():
                    col_mapping[col] = 'player_id'
            elif 'player_game' in col_lower and 'player_id' not in col_mapping.values():
                col_mapping[col] = 'player_id'
            elif 'player_name' in col_lower and 'player_name' not in col_mapping.values():
                col_mapping[col] = 'player_name'
        
        # Map point number columns
        for col in df.columns:
            col_lower = str(col).lower()
            if ('point_num' in col_lower or 'point' == col_lower or 'xy_slot' == col_lower or 'slot' == col_lower) and 'point_number' not in df.columns:
                col_mapping[col] = 'point_number'

        # Map X coordinate columns
        for col in df.columns:
            col_lower = str(col).lower()
            if any(pattern in col_lower for pattern in ['player_x', 'coord_x', '_x']) and 'x' not in df.columns:
                # Prioritize player_x over coord_x
                if 'player' in col_lower:
                    if 'x' not in col_mapping.values():
                        col_mapping[col] = 'x'
                elif 'coord' in col_lower and 'x' not in col_mapping.values():
                    col_mapping[col] = 'x'
                elif col_lower.endswith('_x') and 'x' not in col_mapping.values():
                    col_mapping[col] = 'x'
        
        # Map Y coordinate columns
        for col in df.columns:
            col_lower = str(col).lower()
            if any(pattern in col_lower for pattern in ['player_y', 'coord_y', '_y']) and 'y' not in df.columns:
                # Prioritize player_y over coord_y
                if 'player' in col_lower:
                    if 'y' not in col_mapping.values():
                        col_mapping[col] = 'y'
                elif 'coord' in col_lower and 'y' not in col_mapping.values():
                    col_mapping[col] = 'y'
                elif col_lower.endswith('_y') and 'y' not in col_mapping.values():
                    col_mapping[col] = 'y'
        
        # Map is_stop flag columns
        for col in df.columns:
            col_lower = str(col).lower()
            if any(pattern in col_lower for pattern in ['is_stop', 'stop_point', 'stop_flag']) and 'is_stop' not in df.columns:
                col_mapping[col] = 'is_stop'
        
        # Map player role columns
        for col in df.columns:
            col_lower = str(col).lower()
            if 'player_role' in col_lower or ('role' in col_lower and 'player' in col_lower):
                if 'player_role' not in col_mapping.values():
                    col_mapping[col] = 'player_role'
        
        # Apply mappings
        for old_col, new_col in col_mapping.items():
            if old_col in df.columns:
                df[new_col] = df[old_col]
        
        # Ensure game_id
        if 'game_id' not in df.columns:
            df['game_id'] = game_id
        else:
            df['game_id'] = df['game_id'].fillna(game_id)
        
        # Convert event_index to event_id if needed
        # The column mapping may have copied event_index values into event_id,
        # so also check if event_id values are raw indices (no 'EV' prefix)
        from src.core.key_utils import format_key
        if 'event_id' in df.columns:
            sample_eid = str(df['event_id'].iloc[0]).strip() if len(df) > 0 else ''
            if sample_eid and not sample_eid.startswith('EV'):
                source_col = 'event_index' if 'event_index' in df.columns else 'event_id'
                df['event_id'] = df[source_col].apply(
                    lambda v: format_key('EV', game_id, str(v).strip())
                )
        elif 'event_index' in df.columns:
            df['event_id'] = df['event_index'].apply(
                lambda v: format_key('EV', game_id, str(v).strip())
            )

        # Required columns check (event_id, player identifier, x, y)
        required = ['event_id', 'game_id', 'x', 'y']
        
        # Check for player identifier (player_id, player_game, or player_name)
        has_player_id = 'player_id' in df.columns
        has_player_game = 'player_game' in df.columns
        has_player_name = 'player_name' in df.columns
        
        if not (has_player_id or has_player_game or has_player_name):
            logger.error(f"  Missing player identifier: need player_id, player_game, or player_name")
            return pd.DataFrame()
        
        missing = [col for col in required if col not in df.columns]
        if missing:
            logger.error(f"  Missing required columns: {missing}")
            return pd.DataFrame()
        
        # Ensure point_number exists (if missing, infer from row number or sequence)
        if 'point_number' not in df.columns:
            # Try to infer from index or create sequential numbers per event+player
            if 'event_id' in df.columns and 'player_id' in df.columns:
                df = df.sort_values(['event_id', 'player_id', df.index.name if df.index.name else 'index']).reset_index(drop=True)
                df['point_number'] = df.groupby(['event_id', 'player_id']).cumcount() + 1
            elif 'event_id' in df.columns:
                df = df.sort_values(['event_id', df.index.name if df.index.name else 'index']).reset_index(drop=True)
                df['point_number'] = df.groupby('event_id').cumcount() + 1
            else:
                df['point_number'] = df.groupby(df.index).cumcount() + 1
            logger.warning("  point_number not found, inferred from row sequence")
        
        # Ensure point_number is numeric
        if 'point_number' in df.columns:
            df['point_number'] = pd.to_numeric(df['point_number'], errors='coerce').fillna(1).astype(int)
        
        # Build records
        records = []
        for idx, row in df.iterrows():
            event_id = str(row.get('event_id', ''))
            if not event_id or event_id == 'nan':
                logger.debug(f"  Row {idx}: Skipping - missing event_id")
                continue
            
            # Get player identifier (try multiple sources)
            player_id = None
            if 'player_id' in df.columns:
                player_id = str(row.get('player_id', '')).strip()
            if not player_id or player_id == 'nan':
                if 'player_game' in df.columns:
                    player_id = str(row.get('player_game', '')).strip()
                elif 'player_name' in df.columns:
                    # Use player_name as temporary identifier (should be resolved to player_id later)
                    player_id = str(row.get('player_name', '')).strip()
            
            if not player_id or player_id == 'nan':
                logger.debug(f"  Row {idx}: Skipping - missing player identifier")
                continue
            
            point_num = int(row.get('point_number', 1))
            x = row.get('x')
            y = row.get('y')
            
            # Skip if coordinates are missing or invalid
            if pd.isna(x) or pd.isna(y):
                continue
            
            x_str = str(x).strip()
            y_str = str(y).strip()
            
            if x_str == '' or y_str == '' or x_str.lower() == 'nan' or y_str.lower() == 'nan':
                continue
            
            try:
                x_val = float(x)
                y_val = float(y)
                
                # Validate coordinates are reasonable
                if abs(x_val) > 200 or abs(y_val) > 100:
                    logger.debug(f"  Row {idx}: Skipping - coordinates out of range: ({x_val}, {y_val})")
                    continue
                    
            except (ValueError, TypeError) as e:
                logger.debug(f"  Row {idx}: Skipping - invalid coordinates: {e}")
                continue
            
            # Get player_name (if not already set)
            player_name = row.get('player_name') if 'player_name' in df.columns else None
            if pd.isna(player_name) or str(player_name).strip() == '' or str(player_name).lower() == 'nan':
                player_name = None
            
            # Get player_role (if available)
            player_role = row.get('player_role') if 'player_role' in df.columns else None
            if pd.isna(player_role) or str(player_role).strip() == '' or str(player_role).lower() == 'nan':
                player_role = None
            
            # Determine is_event_team flag
            is_event_team = None
            if 'is_event_team' in df.columns:
                is_event_team_val = row.get('is_event_team')
                if pd.notna(is_event_team_val):
                    is_event_team_str = str(is_event_team_val).strip().lower()
                    if is_event_team_str in ['true', '1', 'yes', 't']:
                        is_event_team = True
                    try:
                        is_event_team = int(float(is_event_team_val)) == 1
                    except:
                        pass
            
            # If not set, try to infer from player_role
            if is_event_team is None and player_role:
                is_event_team = 'event_player' in str(player_role).lower() or 'event_team' in str(player_role).lower()
            
            # Determine is_start flag
            is_start = 0
            is_start_val = row.get('is_start') if 'is_start' in df.columns else None
            if pd.notna(is_start_val):
                is_start_str = str(is_start_val).strip().lower()
                if is_start_str in ['true', '1', 'yes', 't']:
                    is_start = 1
                try:
                    if int(float(is_start_val)) == 1:
                        is_start = 1
                except:
                    pass

            # Determine is_stop flag (similar to puck XY)
            is_stop = 0
            is_stop_val = row.get('is_stop') if 'is_stop' in df.columns else None

            if pd.notna(is_stop_val):
                is_stop_str = str(is_stop_val).strip().lower()
                if is_stop_str in ['true', '1', 'yes', 't']:
                    is_stop = 1
                try:
                    if int(float(is_stop_val)) == 1:
                        is_stop = 1
                except:
                    pass

            # Try alternative stop column names
            if is_stop == 0:
                for col in df.columns:
                    if 'stop' in str(col).lower():
                        stop_val = row.get(col)
                        if pd.notna(stop_val):
                            stop_str = str(stop_val).strip().lower()
                            if stop_str in ['true', '1', 'yes', 't']:
                                is_stop = 1
                                break
                            try:
                                if int(float(stop_val)) == 1:
                                    is_stop = 1
                                    break
                            except:
                                pass

            # Get timestamp if available
            timestamp = None
            timestamp_cols = [c for c in df.columns if 'timestamp' in str(c).lower() or 'time' in str(c).lower()]
            for col in timestamp_cols:
                ts_val = row.get(col)
                if pd.notna(ts_val) and str(ts_val).strip() and str(ts_val).lower() != 'nan':
                    timestamp = str(ts_val).strip()
                    break

            # Generate player_xy_key (use last 4 chars of player_id)
            player_id_suffix = str(player_id)[-4:] if len(str(player_id)) >= 4 else str(player_id).zfill(4)
            player_xy_key = f"PXL{game_id}{str(event_id)[-5:]}{player_id_suffix}{point_num:02d}"

            record = {
                'player_xy_key': player_xy_key,
                'event_id': event_id,
                'game_id': game_id,
                'player_id': player_id,
                'player_name': player_name,
                'player_role': player_role,
                'is_event_team': bool(is_event_team) if is_event_team is not None else None,
                'point_number': point_num,
                'x': x_val,
                'y': y_val,
                'is_start': is_start,
                'is_stop': is_stop,
                'distance_to_net': calculate_distance_to_net(x_val, y_val),
                'angle_to_net': calculate_angle_to_net(x_val, y_val),
                'timestamp': timestamp,
                '_export_timestamp': datetime.now().isoformat()
            }
            
            records.append(record)
        
        if records:
            result_df = pd.DataFrame(records)
            
            if not test_mode:
                save_output_table(result_df, 'fact_player_xy_long', OUTPUT_DIR)
            
            logger.info(f"  Created {len(records):,} player XY long records")
            return result_df
        else:
            logger.warning("  No player XY records created")
            return pd.DataFrame()
        
    except Exception as e:
        logger.error(f"  Error loading xy_player sheet: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def load_tracking_video(tracking_path: Path, game_id: str, test_mode: bool = False) -> pd.DataFrame:
    """
    Load video data from 'video' sheet in tracking file.
    
    This transforms video sheet data into fact_video format with proper column mapping.
    
    Args:
        tracking_path: Path to tracking Excel file
        game_id: Game ID
        test_mode: If True, don't save to output tables, just return data
    
    Returns:
        DataFrame with fact_video schema:
        - video_key, game_id, video_type_id, video_type, video_description
        - video_url, duration_seconds
        - period_1_start, period_2_start, period_3_start
        - _export_timestamp
    """
    if not tracking_path.exists():
        return pd.DataFrame()
    
    try:
        xl = pd.ExcelFile(tracking_path)
        if 'video' not in xl.sheet_names:
            logger.info("  No 'video' sheet found in tracking file")
            return pd.DataFrame()
        
        df = pd.read_excel(tracking_path, sheet_name='video', dtype=str)
        logger.info(f"  Loaded {len(df)} rows from 'video' sheet")
        
        if len(df) == 0:
            return pd.DataFrame()
        
        # Normalize column names (case-insensitive, handle spaces/underscores)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('-', '_')
        
        # Try to find game_id in data if not already set
        if 'game_id' in df.columns:
            game_ids = df['game_id'].dropna().unique()
            if len(game_ids) > 0:
                game_id_from_data = str(game_ids[0]).strip()
                if game_id_from_data and game_id_from_data.isdigit():
                    game_id = game_id_from_data
        
        # Load dim_video_type for mapping if available
        video_type_map = {}
        try:
            from src.core.table_loader import load_table
            dim_video_type = load_table('dim_video_type')
            if len(dim_video_type) > 0:
                for _, row in dim_video_type.iterrows():
                    code = str(row.get('video_type_code', '')).strip().upper()
                    vid_id = str(row.get('video_type_id', '')).strip()
                    if code and vid_id:
                        video_type_map[code] = vid_id
        except:
            pass
        
        # Extract video data - handle multiple rows (one per video type or single row)
        records = []
        for idx, row in df.iterrows():
            # Generate video_key and extract video type
            video_type = None
            video_type_id = None
            if 'video_type' in df.columns:
                video_type = str(row.get('video_type', '')).strip()
            if not video_type or video_type.lower() in ['nan', 'none', '']:
                video_type = 'Full_Ice'  # Default
            
            # Map video_type to video_type_id
            if video_type.upper() in video_type_map:
                video_type_id = video_type_map[video_type.upper()]
            else:
                video_type_id = 'VT0001'  # Default to Full_Ice
            
            # Extract video description
            video_description = None
            desc_cols = ['description', 'video_description', 'desc', 'notes', 'comment']
            for col in desc_cols:
                if col in df.columns:
                    val = row.get(col)
                    if pd.notna(val) and str(val).strip() and str(val).lower() != 'nan':
                        video_description = str(val).strip()
                        break
            
            # If no description, create one from video type
            if not video_description:
                video_type_descriptions = {
                    'Full_Ice': 'Full ice camera view of entire game',
                    'Broadcast': 'Broadcast/television feed of the game',
                    'Highlights': 'Compilation of game highlights',
                    'Goalie': 'Goalie camera view',
                    'Overhead': 'Overhead camera view',
                    'Other': 'Other video type'
                }
                video_description = video_type_descriptions.get(video_type, f'{video_type} video')
            
            video_key = f"V{game_id}{video_type[:4].upper()}"
            
            # Extract video URL - try multiple column variations
            video_url = None
            url_columns = ['url_1', 'url', 'video_url', 'youtube_url', 'url1', 'video_link']
            for col in url_columns:
                if col in df.columns:
                    val = row.get(col)
                    if pd.notna(val) and str(val).strip() and str(val).lower() != 'nan':
                        video_url = str(val).strip()
                        break
            
            # Extract duration
            duration_seconds = None
            duration_cols = ['duration_seconds', 'duration', 'video_duration', 'total_duration', 'length_seconds']
            for col in duration_cols:
                if col in df.columns:
                    val = row.get(col)
                    if pd.notna(val) and str(val).strip() and str(val).lower() != 'nan':
                        try:
                            duration_seconds = str(int(float(str(val))))
                        except:
                            duration_seconds = str(val).strip()
                        break
            
            # Extract period start times
            period_1_start = None
            period_2_start = None
            period_3_start = None
            
            # Try various column name patterns
            p1_cols = ['period_1_start', 'p1_start', 'period1_start', 'period_1', 'p1', 'period1']
            p2_cols = ['period_2_start', 'p2_start', 'period2_start', 'period_2', 'p2', 'period2']
            p3_cols = ['period_3_start', 'p3_start', 'period3_start', 'period_3', 'p3', 'period3']
            
            for col in p1_cols:
                if col in df.columns:
                    val = row.get(col)
                    if pd.notna(val) and str(val).strip() and str(val).lower() != 'nan':
                        try:
                            period_1_start = str(int(float(str(val))))
                        except:
                            period_1_start = str(val).strip()
                        break
            
            for col in p2_cols:
                if col in df.columns:
                    val = row.get(col)
                    if pd.notna(val) and str(val).strip() and str(val).lower() != 'nan':
                        try:
                            period_2_start = str(int(float(str(val))))
                        except:
                            period_2_start = str(val).strip()
                        break
            
            for col in p3_cols:
                if col in df.columns:
                    val = row.get(col)
                    if pd.notna(val) and str(val).strip() and str(val).lower() != 'nan':
                        try:
                            period_3_start = str(int(float(str(val))))
                        except:
                            period_3_start = str(val).strip()
                        break
            
            # Create record
            record = {
                'video_key': video_key,
                'game_id': game_id,
                'video_type_id': video_type_id,
                'video_type': video_type,
                'video_description': video_description,
                'video_url': video_url if video_url else None,
                'duration_seconds': duration_seconds if duration_seconds else None,
                'period_1_start': period_1_start if period_1_start else None,
                'period_2_start': period_2_start if period_2_start else None,
                'period_3_start': period_3_start if period_3_start else None,
                '_export_timestamp': datetime.now().isoformat()
            }
            records.append(record)
        
        if records:
            result_df = pd.DataFrame(records)
            
            if not test_mode:
                save_output_table(result_df, 'fact_video', OUTPUT_DIR)
            
            logger.info(f"  Created {len(records):,} video records")
            return result_df
        else:
            logger.warning("  No video records created")
            return pd.DataFrame()
        
    except Exception as e:
        logger.error(f"  Error loading video sheet: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def extract_xy_from_events_sheet(events_df: pd.DataFrame, game_id: str) -> Dict[str, pd.DataFrame]:
    """
    Extract XY data from events sheet columns.
    
    Extracts from events sheet:
    - player_x_sta/player_y_sta, player_x_sto/player_y_sto (non-adjusted) -> These represent puck XY start/stop
      Note: User said "puck xy start stop" but they appear as player_x/y columns in events sheet
    - net_x, net_y -> fact_shot_xy (shot target location)
    - is_xy_adjusted -> Flag column (added if not present)
    - video flag/URL -> Will be handled separately in fact_events
    
    IMPORTANT: Do NOT use adjusted columns. User specified "dont use the adjusted columns".
    The adjusted columns are identified by checking which set of player_x/y columns has "adjusted" in name
    or by comparing values (if one set matches and another doesn't, the different one is adjusted).
    
    Returns dict with 'puck_xy_wide' and 'shot_xy' DataFrames.
    """
    results = {}
    
    # Identify player XY columns (these represent puck position in events sheet per user description)
    # User said "puck xy start stop" - these appear as player_x_sta/sto, player_y_sta/sto
    player_x_sta_cols = [c for c in events_df.columns if 'player_x_sta' in str(c).lower() or ('player' in str(c).lower() and 'x' in str(c).lower() and 'sta' in str(c).lower())]
    player_y_sta_cols = [c for c in events_df.columns if 'player_y_sta' in str(c).lower() or ('player' in str(c).lower() and 'y' in str(c).lower() and 'sta' in str(c).lower())]
    player_x_sto_cols = [c for c in events_df.columns if 'player_x_sto' in str(c).lower() or ('player' in str(c).lower() and 'x' in str(c).lower() and 'sto' in str(c).lower())]
    player_y_sto_cols = [c for c in events_df.columns if 'player_y_sto' in str(c).lower() or ('player' in str(c).lower() and 'y' in str(c).lower() and 'sto' in str(c).lower())]
    
    # Identify adjusted vs unadjusted columns
    # Adjusted columns will have "adjusted" in name OR be the second set when values differ
    unadjusted_x_sta = None
    unadjusted_y_sta = None
    unadjusted_x_sto = None
    unadjusted_y_sto = None
    
    # Strategy: Use first column that doesn't have "adjusted" in name
    for col in player_x_sta_cols:
        if 'adjusted' not in str(col).lower():
            unadjusted_x_sta = col
            break
    for col in player_y_sta_cols:
        if 'adjusted' not in str(col).lower():
            unadjusted_y_sta = col
            break
    for col in player_x_sto_cols:
        if 'adjusted' not in str(col).lower():
            unadjusted_x_sto = col
            break
    for col in player_y_sto_cols:
        if 'adjusted' not in str(col).lower():
            unadjusted_y_sto = col
            break
    
    # If no explicit "adjusted" in name, use first occurrence (usually unadjusted)
    if not unadjusted_x_sta and player_x_sta_cols:
        unadjusted_x_sta = player_x_sta_cols[0]
    if not unadjusted_y_sta and player_y_sta_cols:
        unadjusted_y_sta = player_y_sta_cols[0]
    if not unadjusted_x_sto and player_x_sto_cols:
        unadjusted_x_sto = player_x_sto_cols[0]
    if not unadjusted_y_sto and player_y_sto_cols:
        unadjusted_y_sto = player_y_sto_cols[0]
    
    # Check if we have puck XY data (player_x/y start/stop represents puck position)
    has_puck_xy = unadjusted_x_sta and unadjusted_y_sta
    
    # Extract puck XY start/stop from events (using non-adjusted player_x/y columns)
    # Note: User said "puck xy start stop" but these appear as player_x/y_sta/sto in events sheet
    if has_puck_xy:
        puck_records = []
        
        # Find event_id or event_index column
        event_id_col = None
        for col in events_df.columns:
            if 'event_id' in str(col).lower():
                event_id_col = col
                break
            if 'event_index' in str(col).lower() and 'tracking' not in str(col).lower():
                event_id_col = col
                break
        
        if not event_id_col:
            # Try to generate event_id
            from src.core.key_utils import format_key
            if 'event_index' in events_df.columns:
                events_df['event_id'] = events_df.apply(
                    lambda r: format_key('EV', game_id, str(r.get('event_index', '')).strip()),
                    axis=1
                )
                event_id_col = 'event_id'
            else:
                logger.warning("  No event_id or event_index column found in events sheet")
                return results
        
        for _, row in events_df.iterrows():
            event_id = str(row.get(event_id_col, ''))
            if not event_id or event_id == 'nan':
                continue
            
            # Get puck XY start/stop from non-adjusted player_x/y columns
            puck_x_start = row.get(unadjusted_x_sta) if unadjusted_x_sta else None
            puck_y_start = row.get(unadjusted_y_sta) if unadjusted_y_sta else None
            puck_x_stop = row.get(unadjusted_x_sto) if unadjusted_x_sto else None
            puck_y_stop = row.get(unadjusted_y_sto) if unadjusted_y_sto else None
            
            # Determine is_xy_adjusted flag
            # Check if adjusted columns exist and have different values from unadjusted
            is_adjusted = 0
            
            # Method 1: Check if is_xy_adjusted column exists in events
            if 'is_xy_adjusted' in events_df.columns:
                is_adjusted_val = row.get('is_xy_adjusted')
                if pd.notna(is_adjusted_val):
                    try:
                        is_adjusted = 1 if int(float(is_adjusted_val)) == 1 else 0
                    except (ValueError, TypeError):
                        pass
            
            # Method 2: Check if adjusted columns exist and values differ
            if is_adjusted == 0:
                adjusted_x_sta_cols = [c for c in player_x_sta_cols if 'adjusted' in str(c).lower()]
                if adjusted_x_sta_cols and unadjusted_x_sta:
                    adjusted_val = row.get(adjusted_x_sta_cols[0])
                    unadjusted_val = row.get(unadjusted_x_sta)
                    if pd.notna(adjusted_val) and pd.notna(unadjusted_val):
                        try:
                            if abs(float(adjusted_val) - float(unadjusted_val)) > 0.01:  # Allow small rounding differences
                                is_adjusted = 1
                        except (ValueError, TypeError):
                            pass
            
            # Method 3: If multiple sets of columns exist, second set is usually adjusted
            # This is a fallback if no explicit "adjusted" in name
            if is_adjusted == 0 and len(player_x_sta_cols) > 1:
                # Check if values in second column differ significantly from first
                if unadjusted_x_sta and len(player_x_sta_cols) > 1:
                    first_val = row.get(player_x_sta_cols[0])
                    second_val = row.get(player_x_sta_cols[1])
                    if pd.notna(first_val) and pd.notna(second_val):
                        try:
                            if abs(float(first_val) - float(second_val)) > 0.01:
                                # Second set is different, check if it matches our unadjusted (first)
                                if player_x_sta_cols[1] == unadjusted_x_sta:
                                    # We're using first, so second is adjusted
                                    pass  # is_adjusted stays 0
                                else:
                                    # We're using second (which has adjusted in name or is different)
                                    is_adjusted = 1
                        except (ValueError, TypeError):
                            pass
            
            # Use start coordinates if stop not available
            if pd.notna(puck_x_start) and pd.notna(puck_y_start):
                try:
                    puck_x_start_val = float(puck_x_start)
                    puck_y_start_val = float(puck_y_start)
                    
                    # Use stop if available, otherwise use start (same point)
                    puck_x_end = float(puck_x_stop) if (pd.notna(puck_x_stop) and str(puck_x_stop).strip() and 
                                                       str(puck_x_stop).lower() != 'nan') else puck_x_start_val
                    puck_y_end = float(puck_y_stop) if (pd.notna(puck_y_stop) and str(puck_y_stop).strip() and 
                                                       str(puck_y_stop).lower() != 'nan') else puck_y_start_val
                    
                    # Determine point_count (2 if stop differs from start, 1 if same)
                    point_count = 2 if (pd.notna(puck_x_stop) and pd.notna(puck_y_stop) and 
                                       puck_x_end != puck_x_start_val and puck_y_end != puck_y_start_val) else 1
                    
                    record = {
                        'puck_xy_key': f"PKW{game_id}{str(event_id)[-5:]}",
                        'event_id': event_id,
                        'game_id': game_id,
                        'puck_x_start': puck_x_start_val,
                        'puck_y_start': puck_y_start_val,
                        'puck_x_end': puck_x_end,
                        'puck_y_end': puck_y_end,
                        'point_count': point_count,
                        'is_xy_adjusted': is_adjusted,
                        '_export_timestamp': datetime.now().isoformat()
                    }
                    puck_records.append(record)
                except (ValueError, TypeError) as e:
                    logger.debug(f"  Error converting puck XY to float: {e}")
                    pass
        
        if puck_records:
            results['puck_xy_wide'] = pd.DataFrame(puck_records)
            logger.info(f"  Extracted {len(puck_records)} puck XY records from events sheet (non-adjusted)")
    
    # Extract net XY (shot target) from events
    # Find event_type column to identify shots
    event_type_col = None
    for col in events_df.columns:
        if 'event_type' in str(col).lower() or 'type' in str(col).lower():
            event_type_col = col
            break
    
    if event_type_col:
        shot_mask = events_df[event_type_col].astype(str).str.lower().isin(['shot', 'goal'])
        shot_events = events_df[shot_mask] if shot_mask.any() else pd.DataFrame()
    else:
        # Try play_detail1 or play_detail2 for shot indicators
        play_detail_cols = [c for c in events_df.columns if 'play_detail' in str(c).lower() or 'event_detail' in str(c).lower()]
        if play_detail_cols:
            shot_mask = events_df[play_detail_cols[0]].astype(str).str.lower().str.contains('shot|goal', na=False, regex=True)
            shot_events = events_df[shot_mask] if shot_mask.any() else pd.DataFrame()
        else:
            shot_events = pd.DataFrame()
    
    if len(shot_events) > 0:
        # Find net_x and net_y columns (non-adjusted)
        net_x_col = None
        net_y_col = None
        
        for col in events_df.columns:
            col_lower = str(col).lower()
            if 'net' in col_lower and 'x' in col_lower and 'adjusted' not in col_lower and 'xy' not in col_lower:
                net_x_col = col
            if 'net' in col_lower and 'y' in col_lower and 'adjusted' not in col_lower and 'xy' not in col_lower:
                net_y_col = col
        
        # Also try alternative names
        if not net_x_col:
            for col in events_df.columns:
                if 'net_x' in str(col).lower() or ('net' in str(col).lower() and '_x' in str(col).lower()):
                    net_x_col = col
                    break
        if not net_y_col:
            for col in events_df.columns:
                if 'net_y' in str(col).lower() or ('net' in str(col).lower() and '_y' in str(col).lower()):
                    net_y_col = col
                    break
        
        if net_x_col and net_y_col:
            shot_records = []
            for _, row in shot_events.iterrows():
                event_id = str(row.get(event_id_col, ''))
                if not event_id or event_id == 'nan':
                    continue
                
                # Get player_id from event_player columns
                player_id = None
                for col in events_df.columns:
                    if 'event_player' in str(col).lower() and 'id' in str(col).lower():
                        player_id = str(row.get(col, ''))
                        break
                if not player_id or player_id == 'nan':
                    # Try player_game or player_id
                    if 'player_game' in events_df.columns:
                        player_id = str(row.get('player_game', ''))
                    elif 'player_id' in events_df.columns:
                        player_id = str(row.get('player_id', ''))
                
                net_x = row.get(net_x_col)
                net_y = row.get(net_y_col)
                
                if pd.notna(net_x) and pd.notna(net_y) and str(net_x).strip() and str(net_y).strip() and str(net_x).lower() != 'nan' and str(net_y).lower() != 'nan':
                    try:
                        record = {
                            'shot_xy_key': f"SXY{game_id}{str(event_id)[-5:]}",
                            'game_id': game_id,
                            'event_id': event_id,
                            'player_id': player_id,
                            'target_x': float(net_x),
                            'target_y': float(net_y),
                            '_export_timestamp': datetime.now().isoformat()
                        }
                        shot_records.append(record)
                    except (ValueError, TypeError) as e:
                        logger.debug(f"  Error converting net_x/y to float: {e}")
                        pass
            
            if shot_records:
                results['shot_xy'] = pd.DataFrame(shot_records)
                logger.info(f"  Extracted {len(shot_records)} shot XY records (net targets) from events sheet")
    
    return results


def load_tracking_xy_data(
    tracking_path: Path,
    game_id: str,
    events_df: Optional[pd.DataFrame] = None,
    test_mode: bool = True
) -> Dict[str, pd.DataFrame]:
    """
    Load all XY data from a tracking file with XY sheets.
    
    Args:
        tracking_path: Path to tracking Excel file
        game_id: Game ID
        events_df: Optional events DataFrame (to extract XY from events sheet columns)
        test_mode: If True, don't save to output tables, just return data
    
    Returns:
        Dictionary with table names and DataFrames:
        - 'puck_xy_long': fact_puck_xy_long DataFrame
        - 'player_xy_long': fact_player_xy_long DataFrame
        - 'puck_xy_wide': fact_puck_xy_wide DataFrame (from events sheet)
        - 'shot_xy': fact_shot_xy DataFrame (from events sheet net_x/y)
        - 'video': fact_video DataFrame
    """
    logger.info(f"\nLoading XY data from tracking file: {tracking_path.name}")
    
    results = {}
    
    # Load puck XY long from sheet
    puck_long = load_tracking_xy_puck_long(tracking_path, game_id, test_mode)
    if len(puck_long) > 0:
        results['puck_xy_long'] = puck_long
        if not test_mode:
            save_output_table(puck_long, 'fact_puck_xy_long', OUTPUT_DIR)
    
    # Load player XY long from sheet
    player_long = load_tracking_xy_player_long(tracking_path, game_id, test_mode)
    if len(player_long) > 0:
        results['player_xy_long'] = player_long
        if not test_mode:
            save_output_table(player_long, 'fact_player_xy_long', OUTPUT_DIR)
    
    # Extract XY from events sheet columns (puck start/stop, net XY)
    if events_df is not None and len(events_df) > 0:
        events_xy = extract_xy_from_events_sheet(events_df, game_id)
        results.update(events_xy)
        
        if not test_mode:
            if 'puck_xy_wide' in events_xy:
                save_output_table(events_xy['puck_xy_wide'], 'fact_puck_xy_wide', OUTPUT_DIR)
            if 'shot_xy' in events_xy:
                save_output_table(events_xy['shot_xy'], 'fact_shot_xy', OUTPUT_DIR)
    
    # Load video sheet
    video_df = load_tracking_video(tracking_path, game_id, test_mode)
    if len(video_df) > 0:
        results['video'] = video_df
        if not test_mode:
            # Save to fact_video (adjust table name if needed)
            save_output_table(video_df, 'fact_video', OUTPUT_DIR)
    
    logger.info(f"  Loaded XY data for game {game_id}: {len(results)} tables")
    return results


def examine_tracking_file(tracking_path: Path) -> None:
    """Examine tracking file structure and print details."""
    if not tracking_path.exists():
        print(f"ERROR: File not found: {tracking_path}")
        return
    
    print("="*80)
    print(f"EXAMINING: {tracking_path.name}")
    print("="*80)
    
    try:
        import pandas as pd
        xl = pd.ExcelFile(tracking_path)
        print(f"\nSheets found ({len(xl.sheet_names)}): {xl.sheet_names}")
        
        for sheet_name in xl.sheet_names:
            print("\n" + "="*80)
            print(f"SHEET: '{sheet_name}'")
            print("="*80)
            
            df = pd.read_excel(xl, sheet_name=sheet_name, nrows=5)
            print(f"Shape: {df.shape[0]} rows (showing first 5), {df.shape[1]} columns")
            
            print(f"\nAll columns ({len(df.columns)}):")
            for i, col in enumerate(df.columns, 1):
                markers = []
                if 'xy' in col.lower(): markers.append('XY')
                if 'puck' in col.lower(): markers.append('PUCK')
                if 'player' in col.lower(): markers.append('PLAYER')
                if 'net' in col.lower(): markers.append('NET')
                if 'video' in col.lower(): markers.append('VIDEO')
                if 'highlight' in col.lower(): markers.append('HIGHLIGHT')
                if 'adjusted' in col.lower(): markers.append('ADJ')
                if 'stop' in col.lower(): markers.append('STOP')
                marker = ' [' + ', '.join(markers) + ']' if markers else ''
                print(f"  {i:3d}. {col}{marker}")
            
            # Show non-null sample data for XY/Video columns
            xy_cols = [c for c in df.columns if any(m in c.lower() for m in ['xy', 'puck', 'net', 'video', 'highlight', 'stop'])]
            if xy_cols:
                print(f"\nSample XY/Video data (first non-null rows):")
                sample = df[xy_cols].dropna(how='all').head(3)
                if len(sample) > 0:
                    for idx, row in sample.iterrows():
                        print(f"  Row {idx}:")
                        for col in xy_cols:
                            val = row.get(col)
                            if pd.notna(val) and str(val).strip():
                                print(f"    {col}: {val}")
            
            # Special handling for shifts sheet
            if sheet_name.lower() == 'shifts':
                print(f"\n=== SHIFTS SHEET ANALYSIS ===")
                shift_cols = [c for c in df.columns if any(m in c.lower() for m in ['shift', 'period', 'home_', 'away_', 'forward', 'defense', 'goalie'])]
                print(f"Shift-specific columns ({len(shift_cols)}):")
                for col in shift_cols[:25]:  # Show first 25
                    print(f"  - {col}")
                if len(shift_cols) > 25:
                    print(f"  ... and {len(shift_cols) - 25} more")
                
                # Check for expected shift columns
                expected_shift_cols = [
                    'shift_index', 'Period', 'period',
                    'shift_start_min', 'shift_start_sec', 'shift_end_min', 'shift_end_sec',
                    'shift_start_type', 'shift_stop_type',
                    'home_forward_1', 'home_forward_2', 'home_forward_3',
                    'away_forward_1', 'away_forward_2', 'away_forward_3',
                    'home_defense_1', 'home_defense_2',
                    'away_defense_1', 'away_defense_2',
                    'home_goalie', 'away_goalie',
                    'strength', 'shift_duration'
                ]
                found_cols = [c for c in expected_shift_cols if c in df.columns]
                missing_cols = [c for c in expected_shift_cols if c not in df.columns]
                print(f"\nExpected shift columns:")
                print(f"  Found: {len(found_cols)}/{len(expected_shift_cols)}")
                if found_cols:
                    print(f"    ✓ {', '.join(found_cols[:10])}{'...' if len(found_cols) > 10 else ''}")
                if missing_cols:
                    print(f"  Missing: {len(missing_cols)} - {', '.join(missing_cols[:10])}{'...' if len(missing_cols) > 10 else ''}")
            
            # Special handling for xy_player sheet
            if sheet_name.lower() in ['xy_player', 'xyplayer', 'player_xy']:
                print(f"\n=== XY_PLAYER SHEET ANALYSIS ===")
                xy_cols = [c for c in df.columns if any(m in c.lower() for m in ['x', 'y', 'coord', 'player'])]
                event_cols = [c for c in df.columns if 'event' in c.lower()]
                player_cols = [c for c in df.columns if 'player' in c.lower()]
                point_cols = [c for c in df.columns if 'point' in c.lower()]
                stop_cols = [c for c in df.columns if 'stop' in c.lower()]
                
                print(f"Coordinate columns ({len(xy_cols)}): {', '.join(xy_cols[:10])}{'...' if len(xy_cols) > 10 else ''}")
                print(f"Event identifier columns ({len(event_cols)}): {', '.join(event_cols)}")
                print(f"Player identifier columns ({len(player_cols)}): {', '.join(player_cols[:10])}{'...' if len(player_cols) > 10 else ''}")
                print(f"Point number columns ({len(point_cols)}): {', '.join(point_cols)}")
                print(f"Stop flag columns ({len(stop_cols)}): {', '.join(stop_cols)}")
                
                # Check for expected columns
                found_x = any('x' in str(c).lower() for c in df.columns)
                found_y = any('y' in str(c).lower() for c in df.columns)
                found_event = any('event' in str(c).lower() for c in df.columns)
                found_player = any('player' in str(c).lower() for c in df.columns)
                found_point = any('point' in str(c).lower() for c in df.columns)
                
                print(f"\nRequired columns check:")
                print(f"  X coordinate: {'✓' if found_x else '✗'}")
                print(f"  Y coordinate: {'✓' if found_y else '✗'}")
                print(f"  Event identifier: {'✓' if found_event else '✗'}")
                print(f"  Player identifier: {'✓' if found_player else '✗'}")
                print(f"  Point number: {'✓' if found_point else '⚠ (will infer)'}")
            
            # Special handling for xy_puck sheet
            if sheet_name.lower() in ['xy_puck', 'xypuck', 'puck_xy']:
                print(f"\n=== XY_PUCK SHEET ANALYSIS ===")
                xy_cols = [c for c in df.columns if any(m in c.lower() for m in ['x', 'y', 'coord', 'puck'])]
                event_cols = [c for c in df.columns if 'event' in c.lower()]
                point_cols = [c for c in df.columns if 'point' in c.lower()]
                stop_cols = [c for c in df.columns if 'stop' in c.lower()]
                
                print(f"Coordinate columns ({len(xy_cols)}): {', '.join(xy_cols[:10])}{'...' if len(xy_cols) > 10 else ''}")
                print(f"Event identifier columns ({len(event_cols)}): {', '.join(event_cols)}")
                print(f"Point number columns ({len(point_cols)}): {', '.join(point_cols)}")
                print(f"Stop flag columns ({len(stop_cols)}): {', '.join(stop_cols)}")
                
                # Check for expected columns
                expected_xy_cols = ['x', 'y', 'puck_x', 'puck_y', 'coord_x', 'coord_y']
                expected_event_cols = ['event_id', 'event_index', 'event_key']
                expected_point_cols = ['point_number', 'point_num', 'point']
                
                found_x = any('x' in str(c).lower() for c in df.columns)
                found_y = any('y' in str(c).lower() for c in df.columns)
                found_event = any('event' in str(c).lower() for c in df.columns)
                found_point = any('point' in str(c).lower() for c in df.columns)
                
                print(f"\nRequired columns check:")
                print(f"  X coordinate: {'✓' if found_x else '✗'}")
                print(f"  Y coordinate: {'✓' if found_y else '✗'}")
                print(f"  Event identifier: {'✓' if found_event else '✗'}")
                print(f"  Point number: {'✓' if found_point else '⚠ (will infer)'}")
            
            # Special handling for video sheet
            if sheet_name.lower() == 'video':
                print(f"\n=== VIDEO SHEET ANALYSIS ===")
                video_cols = [c for c in df.columns if any(m in c.lower() for m in ['video', 'url', 'duration', 'period', 'description'])]
                print(f"Video-specific columns ({len(video_cols)}):")
                for col in video_cols:
                    print(f"  - {col}")
                
                # Check for expected video columns
                expected_video_cols = [
                    'video_type', 'video_url', 'url', 'url_1',
                    'duration_seconds', 'duration',
                    'period_1_start', 'period_2_start', 'period_3_start',
                    'p1_start', 'p2_start', 'p3_start',
                    'description', 'video_description'
                ]
                found_cols = [c for c in expected_video_cols if c in df.columns]
                missing_cols = [c for c in expected_video_cols if c not in df.columns]
                print(f"\nExpected video columns:")
                print(f"  Found: {len(found_cols)}/{len(expected_video_cols)}")
                if found_cols:
                    print(f"    ✓ {', '.join(found_cols)}")
                if missing_cols:
                    print(f"  Missing: {len(missing_cols)} - {', '.join(missing_cols[:10])}{'...' if len(missing_cols) > 10 else ''}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    import sys
    from pathlib import Path
    
    # Get file path from command line or use default
    if len(sys.argv) > 1:
        test_path = Path(sys.argv[1])
    else:
        # Try multiple possible locations
        possible_paths = [
            Path('data/19038_tracking.xlsx'),
            Path('data/raw/19038_tracking.xlsx'),
            Path('/Users/ronniepinnell/Documents/Documents - Ronnie\'s MacBook Pro - 1/Programming_HD/Hockey/Benchsight/git/benchsight/data/19038_tracking.xlsx'),
        ]
        test_path = None
        for p in possible_paths:
            if p.exists():
                test_path = p
                break
        
        if not test_path:
            # Use workspace root from user_info
            workspace_root = Path.cwd()
            test_path = workspace_root / 'data' / '19038_tracking.xlsx'
    
    if test_path.exists():
        print("\n=== EXAMINING FILE STRUCTURE ===\n")
        examine_tracking_file(test_path)
        
        print("\n\n=== TESTING XY DATA LOAD ===\n")
        results = load_tracking_xy_data(test_path, '19038', test_mode=True)
        print(f"\nTest load complete: {len(results)} tables")
        for name, df in results.items():
            print(f"  {name}: {len(df)} rows")
    else:
        print(f"Test file not found: {test_path}")
        print("Tried paths:")
        for p in possible_paths if 'possible_paths' in locals() else [test_path]:
            print(f"  - {p} (exists: {p.exists()})")
