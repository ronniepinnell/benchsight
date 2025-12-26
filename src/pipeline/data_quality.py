"""
=============================================================================
DATA QUALITY, LOGGING & GAME STATUS MODULE
=============================================================================
File: src/pipeline/data_quality.py

PURPOSE:
    1. Track game processing status (fully tracked, partially tracked, not tracked)
    2. Log data quality issues (nulls, errors, anomalies)
    3. Track what data types are present (shifts, events, xy, shots, video)
    4. Create fact_game_status table with comprehensive logging
    5. Detect and log data issues for correction at source

TRACKED ISSUES:
    - Blank columns
    - Null game_numbers, player_ids
    - Excel errors (#N/A, #SPILL, #VALUE, etc.)
    - Shifts with faceoff start but no stoppage
    - Events with duration > 2 minutes
    - 18-minute times (non-period start)
    - Missing end time components
    - Negative durations
    - Join failures (blanks from FK lookups)

=============================================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json
import re

from src.database.connection import execute_sql
from src.database.table_operations import (
    load_dataframe_to_table,
    table_exists,
    get_row_count,
    read_query,
    drop_table
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Excel error patterns
EXCEL_ERRORS = ['#N/A', '#SPILL', '#VALUE', '#REF', '#DIV/0!', '#NAME?', '#NULL!', '#NUM!', '#ERROR']


class GameDataQualityChecker:
    """
    Comprehensive data quality checker for game tracking data.
    """
    
    def __init__(self, game_id: int, tracking_file: Path):
        self.game_id = game_id
        self.tracking_file = tracking_file
        self.issues = []
        self.warnings = []
        self.stats = {}
        
    def run_all_checks(self) -> Dict:
        """Run all data quality checks."""
        logger.info(f"Running data quality checks for game {self.game_id}")
        
        result = {
            'game_id': self.game_id,
            'check_timestamp': datetime.now().isoformat(),
            'issues': [],
            'warnings': [],
            'data_present': {},
            'time_coverage': {},
            'blank_columns': {},
            'null_counts': {},
            'error_cells': [],
            'anomalies': []
        }
        
        if not self.tracking_file.exists():
            result['issues'].append(f"Tracking file not found: {self.tracking_file}")
            return result
        
        try:
            xlsx = pd.ExcelFile(self.tracking_file)
            
            # Check what sheets exist
            result['sheets_present'] = xlsx.sheet_names
            
            # Check events
            if 'events' in xlsx.sheet_names:
                events_df = pd.read_excel(xlsx, sheet_name='events')
                result['data_present']['events'] = True
                result['events_rows'] = len(events_df)
                
                # Run event checks
                self._check_events(events_df, result)
            else:
                result['data_present']['events'] = False
            
            # Check shifts
            if 'shifts' in xlsx.sheet_names:
                shifts_df = pd.read_excel(xlsx, sheet_name='shifts')
                result['data_present']['shifts'] = True
                result['shifts_rows'] = len(shifts_df)
                
                # Run shift checks
                self._check_shifts(shifts_df, result)
            else:
                result['data_present']['shifts'] = False
            
            # Check game_rosters
            if 'game_rosters' in xlsx.sheet_names:
                roster_df = pd.read_excel(xlsx, sheet_name='game_rosters')
                result['data_present']['game_rosters'] = True
                result['roster_rows'] = len(roster_df)
            else:
                result['data_present']['game_rosters'] = False
            
            # Check for XY data
            result['data_present']['xy_events'] = self._check_xy_data_exists()
            
            # Check for shots data
            result['data_present']['shots'] = self._check_shots_data_exists()
            
            # Check for video times
            result['data_present']['video'] = self._check_video_data_exists()
            
            # Calculate time coverage
            if 'events' in xlsx.sheet_names:
                result['time_coverage'] = self._calculate_time_coverage(events_df)
            
            # Determine tracking status
            result['tracking_status'] = self._determine_tracking_status(result)
            
        except Exception as e:
            result['issues'].append(f"Error reading tracking file: {str(e)}")
            
        return result
    
    def _check_events(self, df: pd.DataFrame, result: Dict) -> None:
        """Check events data for quality issues."""
        
        # Check for blank columns
        blank_cols = []
        for col in df.columns:
            if df[col].isna().all() or (df[col].astype(str).str.strip() == '').all():
                blank_cols.append(col)
        result['blank_columns']['events'] = blank_cols
        
        # Check for null game_numbers and player_ids
        null_counts = {}
        for col in ['player_game_number', 'player_id']:
            if col in df.columns:
                null_count = df[col].isna().sum()
                if null_count > 0:
                    null_counts[col] = int(null_count)
        result['null_counts']['events'] = null_counts
        
        # Check for Excel errors in all columns
        for col in df.columns:
            str_col = df[col].astype(str)
            for error in EXCEL_ERRORS:
                mask = str_col.str.contains(error, na=False, regex=False)
                if mask.any():
                    for idx in df[mask].index:
                        result['error_cells'].append({
                            'sheet': 'events',
                            'column': col,
                            'row': int(idx),
                            'error_type': error,
                            'value': str(df.loc[idx, col])
                        })
        
        # Check for duration > 2 minutes (120 seconds)
        if 'duration' in df.columns:
            long_duration = df[df['duration'] > 120]
            for idx, row in long_duration.iterrows():
                result['anomalies'].append({
                    'type': 'long_duration',
                    'sheet': 'events',
                    'row': int(idx),
                    'event_index': row.get('event_index'),
                    'duration': float(row['duration']),
                    'message': f"Event duration > 2 min: {row['duration']}s"
                })
        
        # Check for 18-minute times (except period starts)
        for col in ['event_start_min', 'event_end_min']:
            if col in df.columns:
                # 18 minutes is suspicious unless it's the first event of a period
                mask = df[col] == 18
                if 'event_index' in df.columns:
                    # Exclude first events (likely period starts)
                    first_of_period = df.groupby('period')['event_index'].transform('min')
                    suspicious = mask & (df['event_index'] != first_of_period)
                else:
                    suspicious = mask
                
                for idx in df[suspicious].index:
                    result['anomalies'].append({
                        'type': '18_minute_time',
                        'sheet': 'events',
                        'row': int(idx),
                        'column': col,
                        'message': f"18-minute time (non-period start)"
                    })
        
        # Check for minutes without seconds or vice versa
        if 'event_end_min' in df.columns and 'event_end_sec' in df.columns:
            has_min = df['event_end_min'].notna()
            has_sec = df['event_end_sec'].notna()
            mismatch = (has_min ^ has_sec)  # XOR - one but not both
            for idx in df[mismatch].index:
                result['anomalies'].append({
                    'type': 'incomplete_time',
                    'sheet': 'events',
                    'row': int(idx),
                    'message': f"End time has minute but no second or vice versa"
                })
        
        # Check for negative durations
        if 'duration' in df.columns:
            negative = df[df['duration'] < 0]
            for idx, row in negative.iterrows():
                result['anomalies'].append({
                    'type': 'negative_duration',
                    'sheet': 'events',
                    'row': int(idx),
                    'event_index': row.get('event_index'),
                    'duration': float(row['duration']),
                    'message': f"Negative duration: {row['duration']}s"
                })
        
        # Check for rows with many nulls in mostly-populated columns
        # Find columns that are >80% populated
        mostly_populated = [col for col in df.columns if df[col].notna().mean() > 0.8]
        if len(mostly_populated) > 0:
            null_per_row = df[mostly_populated].isna().sum(axis=1)
            high_null_rows = null_per_row[null_per_row >= len(mostly_populated) * 0.5]
            for idx in high_null_rows.index:
                result['anomalies'].append({
                    'type': 'sparse_row',
                    'sheet': 'events',
                    'row': int(idx),
                    'null_count': int(high_null_rows[idx]),
                    'message': f"Row has many nulls in usually-populated columns"
                })
    
    def _check_shifts(self, df: pd.DataFrame, result: Dict) -> None:
        """Check shifts data for quality issues."""
        
        # Check for blank columns
        blank_cols = []
        for col in df.columns:
            if df[col].isna().all() or (df[col].astype(str).str.strip() == '').all():
                blank_cols.append(col)
        result['blank_columns']['shifts'] = blank_cols
        
        # Check for shifts starting with faceoff but no stoppage time
        if 'shift_start_type' in df.columns and 'shift_stop_type' in df.columns:
            faceoff_starts = df['shift_start_type'].astype(str).str.lower().str.contains('faceoff|face-off|fo', na=False)
            no_stop = df['shift_stop_type'].isna() | (df['shift_stop_type'].astype(str).str.strip() == '')
            problematic = faceoff_starts & no_stop
            
            for idx in df[problematic].index:
                result['anomalies'].append({
                    'type': 'faceoff_no_stop',
                    'sheet': 'shifts',
                    'row': int(idx),
                    'shift_index': df.loc[idx].get('shift_index'),
                    'message': f"Shift starts with faceoff but has no stoppage type"
                })
        
        # Check for Excel errors
        for col in df.columns:
            str_col = df[col].astype(str)
            for error in EXCEL_ERRORS:
                mask = str_col.str.contains(error, na=False, regex=False)
                if mask.any():
                    for idx in df[mask].index:
                        result['error_cells'].append({
                            'sheet': 'shifts',
                            'column': col,
                            'row': int(idx),
                            'error_type': error
                        })
        
        # Check for negative durations
        if 'shift_duration' in df.columns:
            negative = df[df['shift_duration'] < 0]
            for idx, row in negative.iterrows():
                result['anomalies'].append({
                    'type': 'negative_duration',
                    'sheet': 'shifts',
                    'row': int(idx),
                    'shift_index': row.get('shift_index'),
                    'duration': float(row['shift_duration']),
                    'message': f"Negative shift duration: {row['shift_duration']}s"
                })
    
    def _check_xy_data_exists(self) -> bool:
        """Check if XY data exists for this game."""
        game_dir = self.tracking_file.parent
        xy_dir = game_dir / 'xy' / 'event_locations'
        if xy_dir.exists():
            csv_files = list(xy_dir.glob('*.csv'))
            return len(csv_files) > 0
        return False
    
    def _check_shots_data_exists(self) -> bool:
        """Check if shots data exists for this game."""
        game_dir = self.tracking_file.parent
        shots_dir = game_dir / 'shots'
        if shots_dir.exists():
            csv_files = list(shots_dir.glob('*.csv'))
            return len(csv_files) > 0
        return False
    
    def _check_video_data_exists(self) -> bool:
        """Check if video times data exists for this game."""
        game_dir = self.tracking_file.parent
        video_file = game_dir / f'{self.game_id}_video_times.xlsx'
        return video_file.exists()
    
    def _calculate_time_coverage(self, events_df: pd.DataFrame) -> Dict:
        """Calculate time coverage of tracking data."""
        coverage = {
            'periods_present': [],
            'full_game': False,
            'partial': False,
            'time_ranges': []
        }
        
        if 'period' not in events_df.columns:
            return coverage
        
        periods = events_df['period'].dropna().unique()
        coverage['periods_present'] = sorted([int(p) for p in periods if pd.notna(p)])
        
        # Check if we have all 3 regulation periods
        if set([1, 2, 3]).issubset(set(coverage['periods_present'])):
            coverage['full_game'] = True
        elif len(coverage['periods_present']) > 0:
            coverage['partial'] = True
        
        # Calculate time ranges per period
        for period in coverage['periods_present']:
            period_events = events_df[events_df['period'] == period]
            if 'event_start_min' in period_events.columns:
                start_min = period_events['event_start_min'].max()  # Higher = earlier in period
                end_min = period_events['event_start_min'].min()    # Lower = later in period
                start_sec = period_events.loc[period_events['event_start_min'] == start_min, 'event_start_sec'].iloc[0] if 'event_start_sec' in period_events.columns else 0
                end_sec = period_events.loc[period_events['event_start_min'] == end_min, 'event_start_sec'].iloc[0] if 'event_start_sec' in period_events.columns else 0
                
                coverage['time_ranges'].append({
                    'period': int(period),
                    'from_min': int(start_min) if pd.notna(start_min) else None,
                    'from_sec': int(start_sec) if pd.notna(start_sec) else None,
                    'to_min': int(end_min) if pd.notna(end_min) else None,
                    'to_sec': int(end_sec) if pd.notna(end_sec) else None
                })
        
        return coverage
    
    def _determine_tracking_status(self, result: Dict) -> str:
        """Determine overall tracking status."""
        data_present = result.get('data_present', {})
        time_coverage = result.get('time_coverage', {})
        
        # Count what's tracked
        has_events = data_present.get('events', False)
        has_shifts = data_present.get('shifts', False)
        has_xy = data_present.get('xy_events', False)
        has_shots = data_present.get('shots', False)
        has_video = data_present.get('video', False)
        
        if not has_events and not has_shifts:
            return 'NOT_TRACKED'
        
        if time_coverage.get('full_game', False) and has_events and has_shifts:
            return 'FULLY_TRACKED'
        
        return 'PARTIALLY_TRACKED'


def check_game_data_quality(game_id: int, tracking_file: Path) -> Dict:
    """
    Run comprehensive data quality checks for a game.
    
    Args:
        game_id: Game identifier
        tracking_file: Path to tracking xlsx file
    
    Returns:
        Dictionary with all quality check results
    """
    checker = GameDataQualityChecker(game_id, tracking_file)
    return checker.run_all_checks()


def create_game_status_fact_table() -> None:
    """Create the fact_game_status table for tracking status."""
    execute_sql("""
        CREATE TABLE IF NOT EXISTS fact_game_status (
            game_id INTEGER PRIMARY KEY,
            tracking_status TEXT,
            check_timestamp TEXT,
            events_tracked INTEGER,
            shifts_tracked INTEGER,
            xy_tracked INTEGER,
            shots_tracked INTEGER,
            video_tracked INTEGER,
            events_rows INTEGER,
            shifts_rows INTEGER,
            periods_covered TEXT,
            time_ranges TEXT,
            blank_columns TEXT,
            null_counts TEXT,
            error_count INTEGER,
            anomaly_count INTEGER,
            issues TEXT,
            warnings TEXT,
            _processed_timestamp TEXT
        )
    """)


def save_game_quality_results(game_id: int, results: Dict) -> None:
    """
    Save quality check results to fact_game_status.
    
    Args:
        game_id: Game identifier
        results: Quality check results dictionary
    """
    create_game_status_fact_table()
    
    # Delete existing record for this game
    execute_sql("DELETE FROM fact_game_status WHERE game_id = :gid", {'gid': game_id})
    
    data_present = results.get('data_present', {})
    time_coverage = results.get('time_coverage', {})
    
    record = {
        'game_id': game_id,
        'tracking_status': results.get('tracking_status', 'UNKNOWN'),
        'check_timestamp': results.get('check_timestamp'),
        'events_tracked': 1 if data_present.get('events') else 0,
        'shifts_tracked': 1 if data_present.get('shifts') else 0,
        'xy_tracked': 1 if data_present.get('xy_events') else 0,
        'shots_tracked': 1 if data_present.get('shots') else 0,
        'video_tracked': 1 if data_present.get('video') else 0,
        'events_rows': results.get('events_rows', 0),
        'shifts_rows': results.get('shifts_rows', 0),
        'periods_covered': json.dumps(time_coverage.get('periods_present', [])),
        'time_ranges': json.dumps(time_coverage.get('time_ranges', [])),
        'blank_columns': json.dumps(results.get('blank_columns', {})),
        'null_counts': json.dumps(results.get('null_counts', {})),
        'error_count': len(results.get('error_cells', [])),
        'anomaly_count': len(results.get('anomalies', [])),
        'issues': json.dumps(results.get('issues', [])),
        'warnings': json.dumps(results.get('warnings', [])),
        '_processed_timestamp': datetime.now().isoformat()
    }
    
    df = pd.DataFrame([record])
    load_dataframe_to_table(df, 'fact_game_status', 'append')
    logger.info(f"Saved quality results for game {game_id}: {results.get('tracking_status')}")


def create_data_issues_log_table() -> None:
    """Create detailed issues log table."""
    execute_sql("""
        CREATE TABLE IF NOT EXISTS log_data_issues (
            issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            issue_type TEXT,
            sheet_name TEXT,
            column_name TEXT,
            row_number INTEGER,
            event_index INTEGER,
            shift_index INTEGER,
            description TEXT,
            value TEXT,
            severity TEXT,
            check_timestamp TEXT
        )
    """)


def save_detailed_issues(game_id: int, results: Dict) -> None:
    """
    Save detailed issues to log_data_issues table.
    
    Args:
        game_id: Game identifier
        results: Quality check results dictionary
    """
    create_data_issues_log_table()
    
    # Delete existing issues for this game
    execute_sql("DELETE FROM log_data_issues WHERE game_id = :gid", {'gid': game_id})
    
    timestamp = results.get('check_timestamp')
    records = []
    
    # Add error cells
    for error in results.get('error_cells', []):
        records.append({
            'game_id': game_id,
            'issue_type': 'excel_error',
            'sheet_name': error.get('sheet'),
            'column_name': error.get('column'),
            'row_number': error.get('row'),
            'description': f"Excel error: {error.get('error_type')}",
            'value': error.get('value'),
            'severity': 'ERROR',
            'check_timestamp': timestamp
        })
    
    # Add anomalies
    for anomaly in results.get('anomalies', []):
        records.append({
            'game_id': game_id,
            'issue_type': anomaly.get('type'),
            'sheet_name': anomaly.get('sheet'),
            'column_name': anomaly.get('column'),
            'row_number': anomaly.get('row'),
            'event_index': anomaly.get('event_index'),
            'shift_index': anomaly.get('shift_index'),
            'description': anomaly.get('message'),
            'value': str(anomaly.get('duration')) if 'duration' in anomaly else None,
            'severity': 'WARNING',
            'check_timestamp': timestamp
        })
    
    if records:
        df = pd.DataFrame(records)
        load_dataframe_to_table(df, 'log_data_issues', 'append')
        logger.info(f"Saved {len(records)} issues for game {game_id}")


def run_quality_checks_for_game(game_id: int, tracking_file: Path) -> Dict:
    """
    Run full quality checks and save results.
    
    Args:
        game_id: Game identifier
        tracking_file: Path to tracking file
    
    Returns:
        Quality check results
    """
    results = check_game_data_quality(game_id, tracking_file)
    save_game_quality_results(game_id, results)
    save_detailed_issues(game_id, results)
    return results


def get_game_status_summary() -> pd.DataFrame:
    """Get summary of all game tracking statuses."""
    if not table_exists('fact_game_status'):
        return pd.DataFrame()
    
    return read_query("""
        SELECT 
            game_id,
            tracking_status,
            events_tracked,
            shifts_tracked,
            xy_tracked,
            shots_tracked,
            video_tracked,
            events_rows,
            shifts_rows,
            error_count,
            anomaly_count,
            check_timestamp
        FROM fact_game_status
        ORDER BY game_id
    """)
