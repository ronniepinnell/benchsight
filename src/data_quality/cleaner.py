#!/usr/bin/env python3
"""
BENCHSIGHT DATA QUALITY FRAMEWORK
=================================

This module provides systematic data cleaning, validation, and correction
for raw tracking data (events and shifts).

Three-layer approach:
1. STANDARDIZATION - Normalize naming, spelling, formatting
2. VALIDATION - Detect anomalies, flag issues  
3. CORRECTION - Auto-fix known patterns

Run this BEFORE main ETL processing.

Usage:
    from src.data_quality.cleaner import DataQualityCleaner
    cleaner = DataQualityCleaner(game_id=18969)
    events_df, shifts_df, qa_report = cleaner.process()

Version: 6.5.22
Date: January 6, 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# CONFIGURATION - STANDARDIZATION MAPPINGS
# ============================================================

# Term mappings: old_term -> standard_term
TERM_STANDARDIZATION = {
    # Hyphens to underscores
    'goal-scored': 'Goal_Scored',
    'shot-goal': 'Shot_Goal',
    'zone-entry': 'Zone_Entry',
    'zone-exit': 'Zone_Exit',
    'pass-completed': 'Pass_Completed',
    'pass-missed': 'Pass_Missed',
    'faceoff-aftergoal': 'Faceoff_AfterGoal',
    'faceoff-won': 'Faceoff_Won',
    'faceoff-lost': 'Faceoff_Lost',
    'shot-onnetsaved': 'Shot_OnNetSaved',
    'shot-missed': 'Shot_Missed',
    'shot-blocked': 'Shot_Blocked',
    'turnover-giveaway': 'Turnover_Giveaway',
    'turnover-takeaway': 'Turnover_Takeaway',
    
    # Common misspellings
    'posession': 'Possession',
    'possesion': 'Possession',
    'faecoff': 'Faceoff',
    'faceoof': 'Faceoff',
    'turnonver': 'Turnover',
    'givaway': 'Giveaway',
    'takeawy': 'Takeaway',
    'breakot': 'Breakout',
    'brekout': 'Breakout',
    
    # Case variations (lowercase to standard)
    'goal_scored': 'Goal_Scored',
    'shot_goal': 'Shot_Goal',
    'zone_entry': 'Zone_Entry',
    'zone_exit': 'Zone_Exit',
    
    # Shot type variations
    'goal-wrist': 'Goal_Wrist',
    'goal-slap': 'Goal_Slap',
    'goal-backhand': 'Goal_Backhand',
    'goal-tip': 'Goal_Tip',
    'goal-snap': 'Goal_Snap',
    'goal-poke': 'Goal_Poke',
}

# Event type standardization
EVENT_TYPE_MAPPING = {
    'goal': 'Goal',
    'shot': 'Shot',
    'pass': 'Pass',
    'faceoff': 'Faceoff',
    'turnover': 'Turnover',
    'possession': 'Possession',
    'stoppage': 'Stoppage',
    'penalty': 'Penalty',
    'deadice': 'DeadIce',
    'zone_entry_exit': 'Zone_Entry_Exit',
    'zone entry exit': 'Zone_Entry_Exit',
    'loosepuck': 'LoosePuck',
    'rebound': 'Rebound',
    'save': 'Save',
    'intermission': 'Intermission',
    'play': 'Play',
}

# Columns to check for term standardization
COLUMNS_TO_STANDARDIZE = [
    'event_type', 'event_type_', 'Type',
    'event_detail', 'event_detail_',
    'event_detail_2', 'event_detail_2_',
    'play_detail1', 'play_detail1_',
    'play_detail2', 'play_detail_2',
]


# ============================================================
# VALIDATION THRESHOLDS
# ============================================================

@dataclass
class ValidationThresholds:
    """Configurable thresholds for data validation."""
    
    # Duration thresholds (seconds)
    min_event_duration: float = 0.0  # Can be 0 for instant events
    max_event_duration: float = 300.0  # 5 minutes max for single event
    min_shift_duration: float = 5.0  # Minimum shift length
    max_shift_duration: float = 180.0  # 3 minutes max shift
    
    # Time thresholds
    max_period_minutes: int = 20  # Max time in a period
    max_game_minutes: int = 70  # Max game length including OT
    
    # Count thresholds
    max_events_per_game: int = 3000  # Flag if more
    min_events_per_game: int = 100  # Flag if fewer
    max_shifts_per_game: int = 500
    min_shifts_per_game: int = 20
    
    # Player thresholds
    max_players_per_event: int = 14  # 7 per team max
    max_toi_per_game: float = 60.0  # Minutes


# ============================================================
# DATA QUALITY ISSUE TYPES
# ============================================================

@dataclass
class DataQualityIssue:
    """Represents a single data quality issue."""
    
    game_id: int
    table: str  # 'events' or 'shifts'
    row_index: int
    column: str
    issue_type: str
    severity: str  # 'error', 'warning', 'info'
    old_value: str
    new_value: Optional[str] = None
    auto_fixed: bool = False
    description: str = ""


# ============================================================
# STANDARDIZATION LAYER
# ============================================================

class DataStandardizer:
    """Standardize raw data - naming conventions, spelling, formatting."""
    
    def __init__(self):
        # Build reverse mapping for case-insensitive lookup
        self.term_map = {}
        for old, new in TERM_STANDARDIZATION.items():
            self.term_map[old.lower()] = new
        
        self.event_type_map = {}
        for old, new in EVENT_TYPE_MAPPING.items():
            self.event_type_map[old.lower()] = new
    
    def standardize_term(self, value: str) -> Tuple[str, bool]:
        """
        Standardize a single term.
        Returns (standardized_value, was_changed).
        """
        if pd.isna(value):
            return value, False
        
        original = str(value)
        lookup_key = original.lower().replace(' ', '_')
        
        # Check term mapping
        if lookup_key in self.term_map:
            return self.term_map[lookup_key], True
        
        # Convert hyphens to underscores
        if '-' in original:
            converted = original.replace('-', '_')
            # Title case each part
            parts = converted.split('_')
            standardized = '_'.join(p.capitalize() for p in parts)
            return standardized, True
        
        return original, False
    
    def standardize_event_type(self, value: str) -> Tuple[str, bool]:
        """Standardize event_type value."""
        if pd.isna(value):
            return value, False
        
        original = str(value)
        lookup_key = original.lower().strip()
        
        if lookup_key in self.event_type_map:
            return self.event_type_map[lookup_key], True
        
        return original, False
    
    def standardize_dataframe(self, df: pd.DataFrame, table_name: str) -> Tuple[pd.DataFrame, List[DataQualityIssue]]:
        """
        Standardize all applicable columns in dataframe.
        Returns (standardized_df, list of issues).
        """
        df = df.copy()
        issues = []
        
        # Get game_id if available
        game_id = df['game_id'].iloc[0] if 'game_id' in df.columns else 0
        
        for col in COLUMNS_TO_STANDARDIZE:
            if col not in df.columns:
                continue
            
            for idx in df.index:
                old_value = df.at[idx, col]
                
                if 'type' in col.lower():
                    new_value, changed = self.standardize_event_type(old_value)
                else:
                    new_value, changed = self.standardize_term(old_value)
                
                if changed:
                    df.at[idx, col] = new_value
                    issues.append(DataQualityIssue(
                        game_id=game_id,
                        table=table_name,
                        row_index=idx,
                        column=col,
                        issue_type='term_standardization',
                        severity='info',
                        old_value=str(old_value),
                        new_value=new_value,
                        auto_fixed=True,
                        description=f"Standardized '{old_value}' to '{new_value}'"
                    ))
        
        return df, issues


# ============================================================
# VALIDATION LAYER
# ============================================================

class DataValidator:
    """Validate data and flag anomalies."""
    
    def __init__(self, thresholds: ValidationThresholds = None):
        self.thresholds = thresholds or ValidationThresholds()
    
    def validate_events(self, df: pd.DataFrame, game_id: int) -> List[DataQualityIssue]:
        """Validate events dataframe."""
        issues = []
        
        # 1. Check event count
        if len(df) > self.thresholds.max_events_per_game:
            issues.append(DataQualityIssue(
                game_id=game_id, table='events', row_index=-1, column='row_count',
                issue_type='high_event_count', severity='warning',
                old_value=str(len(df)),
                description=f"Event count {len(df)} exceeds threshold {self.thresholds.max_events_per_game}"
            ))
        
        if len(df) < self.thresholds.min_events_per_game:
            issues.append(DataQualityIssue(
                game_id=game_id, table='events', row_index=-1, column='row_count',
                issue_type='low_event_count', severity='warning',
                old_value=str(len(df)),
                description=f"Event count {len(df)} below threshold {self.thresholds.min_events_per_game}"
            ))
        
        # 2. Check for duplicate event_index values (within same game)
        if 'event_index' in df.columns:
            dup_mask = df.duplicated(subset=['event_index'], keep=False)
            if dup_mask.any():
                # This is expected - multiple rows per event (one per player)
                pass  # Not an error
        
        # 3. Check duration columns
        duration_cols = [c for c in df.columns if 'duration' in c.lower()]
        for col in duration_cols:
            if col not in df.columns:
                continue
            
            # Negative duration
            neg_mask = df[col] < self.thresholds.min_event_duration
            for idx in df[neg_mask].index:
                issues.append(DataQualityIssue(
                    game_id=game_id, table='events', row_index=idx, column=col,
                    issue_type='negative_duration', severity='error',
                    old_value=str(df.at[idx, col]),
                    description=f"Negative duration: {df.at[idx, col]}"
                ))
            
            # Excessive duration
            high_mask = df[col] > self.thresholds.max_event_duration
            for idx in df[high_mask].index:
                issues.append(DataQualityIssue(
                    game_id=game_id, table='events', row_index=idx, column=col,
                    issue_type='excessive_duration', severity='warning',
                    old_value=str(df.at[idx, col]),
                    description=f"Duration {df.at[idx, col]}s exceeds {self.thresholds.max_event_duration}s"
                ))
        
        # 4. Check time columns (start should be <= end within same period)
        if all(c in df.columns for c in ['event_start_min', 'event_start_sec', 'event_end_min', 'event_end_sec']):
            df_check = df.copy()
            df_check['start_total'] = df_check['event_start_min'] * 60 + df_check['event_start_sec']
            df_check['end_total'] = df_check['event_end_min'] * 60 + df_check['event_end_sec']
            
            # Note: In hockey, time counts DOWN, so start > end is normal
            # But negative times are errors
            neg_start = df_check['start_total'] < 0
            neg_end = df_check['end_total'] < 0
            
            for idx in df_check[neg_start].index:
                issues.append(DataQualityIssue(
                    game_id=game_id, table='events', row_index=idx, column='event_start',
                    issue_type='negative_time', severity='error',
                    old_value=f"{df.at[idx, 'event_start_min']}:{df.at[idx, 'event_start_sec']}",
                    description="Negative start time"
                ))
        
        # 5. Check period values
        if 'period' in df.columns:
            invalid_periods = df[~df['period'].isin([1, 2, 3, 4, 'OT', '1', '2', '3', '4'])]
            for idx in invalid_periods.index:
                issues.append(DataQualityIssue(
                    game_id=game_id, table='events', row_index=idx, column='period',
                    issue_type='invalid_period', severity='error',
                    old_value=str(df.at[idx, 'period']),
                    description=f"Invalid period value: {df.at[idx, 'period']}"
                ))
        
        # 6. Check for required columns with all nulls
        required_cols = ['event_type', 'event_detail', 'period']
        for col in required_cols:
            if col in df.columns and df[col].isna().all():
                issues.append(DataQualityIssue(
                    game_id=game_id, table='events', row_index=-1, column=col,
                    issue_type='all_null_column', severity='error',
                    old_value='ALL NULL',
                    description=f"Required column {col} is entirely null"
                ))
        
        # 7. Check player count per event
        if 'player_game_number' in df.columns and 'event_index' in df.columns:
            player_counts = df.groupby('event_index')['player_game_number'].nunique()
            high_count = player_counts[player_counts > self.thresholds.max_players_per_event]
            for event_idx, count in high_count.items():
                issues.append(DataQualityIssue(
                    game_id=game_id, table='events', row_index=-1, column='player_count',
                    issue_type='excessive_players', severity='warning',
                    old_value=str(count),
                    description=f"Event {event_idx} has {count} players (max {self.thresholds.max_players_per_event})"
                ))
        
        return issues
    
    def validate_shifts(self, df: pd.DataFrame, game_id: int) -> List[DataQualityIssue]:
        """Validate shifts dataframe."""
        issues = []
        
        # 1. Check shift count
        if len(df) > self.thresholds.max_shifts_per_game:
            issues.append(DataQualityIssue(
                game_id=game_id, table='shifts', row_index=-1, column='row_count',
                issue_type='high_shift_count', severity='warning',
                old_value=str(len(df)),
                description=f"Shift count {len(df)} exceeds {self.thresholds.max_shifts_per_game}"
            ))
        
        # 2. Check duration
        if 'duration' in df.columns:
            # Short shifts
            short_mask = (df['duration'] > 0) & (df['duration'] < self.thresholds.min_shift_duration)
            for idx in df[short_mask].index:
                issues.append(DataQualityIssue(
                    game_id=game_id, table='shifts', row_index=idx, column='duration',
                    issue_type='short_shift', severity='info',
                    old_value=str(df.at[idx, 'duration']),
                    description=f"Shift duration {df.at[idx, 'duration']}s below {self.thresholds.min_shift_duration}s"
                ))
            
            # Long shifts
            long_mask = df['duration'] > self.thresholds.max_shift_duration
            for idx in df[long_mask].index:
                issues.append(DataQualityIssue(
                    game_id=game_id, table='shifts', row_index=idx, column='duration',
                    issue_type='long_shift', severity='warning',
                    old_value=str(df.at[idx, 'duration']),
                    description=f"Shift duration {df.at[idx, 'duration']}s exceeds {self.thresholds.max_shift_duration}s"
                ))
            
            # Negative duration
            neg_mask = df['duration'] < 0
            for idx in df[neg_mask].index:
                issues.append(DataQualityIssue(
                    game_id=game_id, table='shifts', row_index=idx, column='duration',
                    issue_type='negative_duration', severity='error',
                    old_value=str(df.at[idx, 'duration']),
                    description=f"Negative shift duration: {df.at[idx, 'duration']}"
                ))
        
        # 3. Check for duplicate shifts (same player, same time)
        if all(c in df.columns for c in ['player_game_number', 'period', 'shift_start_min']):
            dup_cols = ['player_game_number', 'period', 'shift_start_min']
            dups = df[df.duplicated(subset=dup_cols, keep=False)]
            if len(dups) > 0:
                for idx in dups.index:
                    issues.append(DataQualityIssue(
                        game_id=game_id, table='shifts', row_index=idx, column='shift_key',
                        issue_type='duplicate_shift', severity='warning',
                        old_value=f"P{df.at[idx, 'period']} {df.at[idx, 'shift_start_min']}min #{df.at[idx, 'player_game_number']}",
                        description="Possible duplicate shift entry"
                    ))
        
        return issues


# ============================================================
# CORRECTION LAYER
# ============================================================

class DataCorrector:
    """Auto-correct known data issues."""
    
    def __init__(self, blb_schedule: pd.DataFrame):
        """
        Initialize with BLB schedule for authoritative home/away data.
        
        Args:
            blb_schedule: DataFrame from dim_schedule with game_id, home_team_id, away_team_id
        """
        self.blb_schedule = blb_schedule
        self._build_schedule_lookup()
    
    def _build_schedule_lookup(self):
        """Build lookup for quick access to schedule data."""
        self.schedule_lookup = {}
        for _, row in self.blb_schedule.iterrows():
            game_id = row['game_id']
            self.schedule_lookup[game_id] = {
                'home_team_id': row.get('home_team_id'),
                'away_team_id': row.get('away_team_id'),
                'home_team_name': row.get('home_team_name'),
                'away_team_name': row.get('away_team_name'),
                'home_goals': row.get('home_total_goals', row.get('home_team_goals')),
                'away_goals': row.get('away_total_goals', row.get('away_team_goals')),
            }
    
    def correct_venue_swap(self, df: pd.DataFrame, game_id: int) -> Tuple[pd.DataFrame, List[DataQualityIssue]]:
        """
        Check and correct home/away if swapped vs BLB schedule.
        
        Returns:
            (corrected_df, list of correction issues)
        """
        issues = []
        
        if game_id not in self.schedule_lookup:
            return df, issues
        
        sched = self.schedule_lookup[game_id]
        df = df.copy()
        
        # Check if home_team column exists
        home_col = None
        away_col = None
        for col in ['home_team', 'home_team_name']:
            if col in df.columns:
                home_col = col
                break
        for col in ['away_team', 'away_team_name']:
            if col in df.columns:
                away_col = col
                break
        
        if not home_col or not away_col:
            return df, issues
        
        # Get current values from tracking
        tracking_home = df[home_col].iloc[0] if len(df) > 0 else None
        tracking_away = df[away_col].iloc[0] if len(df) > 0 else None
        
        # Compare to BLB schedule
        blb_home = sched.get('home_team_name') or sched.get('home_team_id')
        blb_away = sched.get('away_team_name') or sched.get('away_team_id')
        
        # Check if swapped
        if tracking_home == blb_away and tracking_away == blb_home:
            # SWAPPED! Correct it
            logger.warning(f"Game {game_id}: Home/Away SWAPPED - correcting to match BLB schedule")
            
            # Swap the values
            df[home_col] = blb_home
            df[away_col] = blb_away
            
            # Also swap _id columns if present
            if 'home_team_id' in df.columns and 'away_team_id' in df.columns:
                df['home_team_id'] = sched['home_team_id']
                df['away_team_id'] = sched['away_team_id']
            
            # Swap zone columns if present
            zone_swaps = [
                ('home_team_zone', 'away_team_zone'),
                ('home_team_zone_', 'away_team_zone_'),
            ]
            for home_zone, away_zone in zone_swaps:
                if home_zone in df.columns and away_zone in df.columns:
                    df[home_zone], df[away_zone] = df[away_zone].copy(), df[home_zone].copy()
            
            issues.append(DataQualityIssue(
                game_id=game_id, table='events', row_index=-1, column='home_team',
                issue_type='venue_swap_corrected', severity='warning',
                old_value=f"Home={tracking_home}, Away={tracking_away}",
                new_value=f"Home={blb_home}, Away={blb_away}",
                auto_fixed=True,
                description=f"Swapped home/away to match BLB schedule"
            ))
        
        return df, issues


# ============================================================
# MAIN DATA QUALITY CLEANER
# ============================================================

class DataQualityCleaner:
    """
    Main class for data quality processing.
    
    Usage:
        cleaner = DataQualityCleaner(blb_schedule_df)
        events, shifts, report = cleaner.process_game(game_id, events_df, shifts_df)
    """
    
    def __init__(self, blb_schedule: pd.DataFrame, thresholds: ValidationThresholds = None):
        self.standardizer = DataStandardizer()
        self.validator = DataValidator(thresholds)
        self.corrector = DataCorrector(blb_schedule)
        self.all_issues: List[DataQualityIssue] = []
    
    def process_game(
        self, 
        game_id: int, 
        events_df: pd.DataFrame, 
        shifts_df: Optional[pd.DataFrame] = None
    ) -> Tuple[pd.DataFrame, Optional[pd.DataFrame], List[DataQualityIssue]]:
        """
        Process a single game's data through all quality layers.
        
        Args:
            game_id: Game identifier
            events_df: Raw events dataframe
            shifts_df: Raw shifts dataframe (optional)
        
        Returns:
            (cleaned_events, cleaned_shifts, issues_list)
        """
        issues = []
        
        # Layer 1: Standardization
        events_df, std_issues = self.standardizer.standardize_dataframe(events_df, 'events')
        issues.extend(std_issues)
        
        if shifts_df is not None:
            shifts_df, shift_std_issues = self.standardizer.standardize_dataframe(shifts_df, 'shifts')
            issues.extend(shift_std_issues)
        
        # Layer 2: Correction (before validation so we validate corrected data)
        events_df, correction_issues = self.corrector.correct_venue_swap(events_df, game_id)
        issues.extend(correction_issues)
        
        # Layer 3: Validation
        validation_issues = self.validator.validate_events(events_df, game_id)
        issues.extend(validation_issues)
        
        if shifts_df is not None:
            shift_validation_issues = self.validator.validate_shifts(shifts_df, game_id)
            issues.extend(shift_validation_issues)
        
        # Store all issues
        self.all_issues.extend(issues)
        
        return events_df, shifts_df, issues
    
    def generate_qa_report(self) -> pd.DataFrame:
        """Generate QA report dataframe from all issues."""
        if not self.all_issues:
            return pd.DataFrame()
        
        records = []
        for issue in self.all_issues:
            records.append({
                'game_id': issue.game_id,
                'table': issue.table,
                'row_index': issue.row_index,
                'column': issue.column,
                'issue_type': issue.issue_type,
                'severity': issue.severity,
                'old_value': issue.old_value,
                'new_value': issue.new_value,
                'auto_fixed': issue.auto_fixed,
                'description': issue.description,
            })
        
        return pd.DataFrame(records)
    
    def get_issue_summary(self) -> Dict:
        """Get summary statistics of issues."""
        if not self.all_issues:
            return {'total': 0, 'errors': 0, 'warnings': 0, 'auto_fixed': 0}
        
        return {
            'total': len(self.all_issues),
            'errors': sum(1 for i in self.all_issues if i.severity == 'error'),
            'warnings': sum(1 for i in self.all_issues if i.severity == 'warning'),
            'info': sum(1 for i in self.all_issues if i.severity == 'info'),
            'auto_fixed': sum(1 for i in self.all_issues if i.auto_fixed),
            'by_type': pd.Series([i.issue_type for i in self.all_issues]).value_counts().to_dict(),
        }


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def load_blb_schedule(blb_path: Path = Path('data/raw/BLB_Tables.xlsx')) -> pd.DataFrame:
    """Load schedule from BLB file."""
    if blb_path.exists():
        xl = pd.ExcelFile(blb_path)
        if 'Games' in xl.sheet_names:
            return pd.read_excel(xl, sheet_name='Games')
    
    # Fallback to dim_schedule
    schedule_path = Path('data/output/dim_schedule.csv')
    if schedule_path.exists():
        return pd.read_csv(schedule_path)
    
    return pd.DataFrame()


def create_cleaner(blb_path: Path = None) -> DataQualityCleaner:
    """Create a DataQualityCleaner with default settings."""
    if blb_path is None:
        blb_path = Path('data/raw/BLB_Tables.xlsx')
    
    schedule = load_blb_schedule(blb_path)
    return DataQualityCleaner(schedule)


if __name__ == '__main__':
    # Example usage
    print("BenchSight Data Quality Framework")
    print("=" * 40)
    
    # Create cleaner
    cleaner = create_cleaner()
    
    # Process a test game
    import pandas as pd
    test_events = pd.DataFrame({
        'game_id': [18969, 18969],
        'event_type': ['goal', 'shot'],
        'event_detail': ['goal-scored', 'shot-missed'],
        'period': [1, 1],
        'event_start_min': [5, 6],
        'event_start_sec': [30, 45],
    })
    
    cleaned, _, issues = cleaner.process_game(18969, test_events)
    
    print(f"\nProcessed {len(test_events)} events")
    print(f"Issues found: {len(issues)}")
    
    summary = cleaner.get_issue_summary()
    print(f"Summary: {summary}")
