"""
Standardize play_detail and event code values across all games.

This module normalizes:
- play_detail1, play_detail_2 values (prefixed → simple names)
- event_type, event_detail, event_detail_2 values (hyphens → underscores, consolidations)

Usage:
    from src.transformation.standardize_play_details import standardize_tracking_data
    df = standardize_tracking_data(df, dim_tables_path)
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Set, Optional, Tuple
import logging
import re

logger = logging.getLogger(__name__)


# =============================================================================
# EVENT CODE STANDARDIZATION MAPPINGS
# =============================================================================
# Standard format: Category_Detail (underscores, no hyphens, no slashes)

# dim_event_detail: Consolidate duplicate hyphen codes → underscore versions
EVENT_DETAIL_MAPPINGS = {
    # Hyphen → Underscore duplicates
    'Pass-Completed': 'Pass_Completed',
    'Pass-Missed': 'Pass_Missed',
    'Save-Freeze': 'Save_Freeze',
    'Shot-Blocked': 'Shot_Blocked',
    'Shot-OnNet': 'Shot_OnNetSaved',
    'Stoppage-Freeze': 'Stoppage_Freeze',
    'Stoppage-Play': 'Stoppage_Play',
    'Turnover-Giveaway': 'Turnover_Giveaway',
    'Turnover-Takeaway': 'Turnover_Takeaway',
    'Zone-Entry': 'Zone_Entry',
    'Zone-Exit': 'Zone_Exit',
    
    # Consolidate OnNetSaved variations
    'Shot_DeflectedOnNetSaved': 'Shot_OnNetSaved',
    'Shot_TippedOnNetSaved': 'Shot_OnNetSaved',
    
    # Consolidate Shot*Goal variations to Shot_Goal
    'Shot_OnNetTippedGoal': 'Shot_Goal',
}

# dim_event_detail_2: All hyphens → underscores, slashes → underscores
# This is built dynamically but here are explicit typo fixes
EVENT_DETAIL_2_TYPO_FIXES = {
    'Play-SeperateFromPuck': 'Play_SeparateFromPuck',
    'Play_SeperateFromPuck': 'Play_SeparateFromPuck',
}


def standardize_event_code(code: str) -> str:
    """
    Standardize a single event code value.
    
    Rules:
    1. Apply explicit mappings (EVENT_DETAIL_MAPPINGS, EVENT_DETAIL_2_TYPO_FIXES)
    2. Convert hyphens to underscores
    3. Convert slashes to underscores
    
    Args:
        code: Raw event code string
        
    Returns:
        Standardized code string
    """
    if pd.isna(code) or not isinstance(code, str):
        return code
    
    # Check explicit mappings first
    if code in EVENT_DETAIL_MAPPINGS:
        return EVENT_DETAIL_MAPPINGS[code]
    if code in EVENT_DETAIL_2_TYPO_FIXES:
        return EVENT_DETAIL_2_TYPO_FIXES[code]
    
    # Convert hyphens and slashes to underscores
    standardized = code.replace('-', '_').replace('/', '_')
    
    return standardized


def standardize_event_codes_df(
    df: pd.DataFrame,
    columns: list = None,
    log_changes: bool = True
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Standardize event code columns in a DataFrame.
    
    Args:
        df: DataFrame with event code columns
        columns: List of columns to standardize. Default: event_type, event_detail, event_detail_2
        log_changes: Whether to log changes
        
    Returns:
        Tuple of (standardized DataFrame, dict of change counts per column)
    """
    if columns is None:
        columns = ['event_type', 'event_detail', 'event_detail_2', 'Type']
    
    change_counts = {}
    
    for col in columns:
        if col not in df.columns:
            continue
            
        original = df[col].copy()
        df[col] = df[col].apply(standardize_event_code)
        
        # Count changes
        changes = (original != df[col]) & original.notna()
        change_counts[col] = changes.sum()
        
        if log_changes and change_counts[col] > 0:
            logger.info(f"  Standardized {col}: {change_counts[col]:,} values changed")
            
            # Log sample of changes for debugging
            changed_mask = changes
            if changed_mask.any():
                samples = df.loc[changed_mask, [col]].head(5)
                originals = original[changed_mask].head(5)
                for orig, new in zip(originals, samples[col]):
                    logger.debug(f"    {orig} → {new}")
    
    return df, change_counts

# Forced mappings for base names that don't have a direct simple equivalent
# Maps missing base names → closest existing simple code
# NOTE: AssistSecondary, CrashNet, Cycle, Forecheck, Pressure, QuickUp, Reverse, Surf, Contain
#       are now defined in dim_play_detail (src/models/dimensions.py) and don't need mapping
FORCED_BASE_MAPPINGS = {
    # Typo fix
    'FroceWide': 'ForceWide',
    
    # PuckRecovery* → PuckRecoveryRetreival* (existing pattern)
    'PuckRecoveryDumpIn': 'PuckRecoveryRetreivalDumpIn',
    'PuckRecoveryFaceoff': 'PuckRecoveryRetreivalFaceoff',
    'PuckRecoveryOther': 'PuckRecoveryRetreivalOther',
    'PuckRecoveryPass': 'PuckRecoveryRetreivalPass',
    'PuckRecoveryRebound': 'PuckRecoveryRetreivalRebound',
    'PuckRecoveryShot': 'PuckRecoveryRetreivalShot',
    'PuckRecoveryTurnover': 'PuckRecoveryRetreivalTurnover',
    
    # PuckRetreival* (short form) → PuckRecoveryRetreival* (full form)
    'PuckRetreivalFaceoff': 'PuckRecoveryRetreivalFaceoff',
    'PuckRetreivalOther': 'PuckRecoveryRetreivalOther',
    'PuckRetreivalPass': 'PuckRecoveryRetreivalPass',
    'PuckRetreivalRebound': 'PuckRecoveryRetreivalRebound',
    'PuckRetreivalShot': 'PuckRecoveryRetreivalShot',
    'PuckRetreivalTurnover': 'PuckRecoveryRetreivalTurnover',
    
    # PuckRetrieval* (correct spelling) → PuckRecoveryRetreival* (existing pattern)
    'PuckRetrievalDumpIn': 'PuckRecoveryRetreivalDumpIn',
    'PuckRetrievalRebound': 'PuckRecoveryRetreivalRebound',
    'PuckRetrievalShot': 'PuckRecoveryRetreivalShot',
    
    # Semantic matches for remaining unmapped values
    'CededZoneExit': 'CededZoneEntry',
    'DriveNetWide': 'DriveWide',
    'OpenIceDeke': 'Deke',
}


def load_dimension_codes(dim_path: Path) -> Dict[str, Set[str]]:
    """Load valid codes from dimension tables and merge with constants."""
    codes = {}
    
    dim_files = {
        'event_type': 'dim_event_type.csv',
        'event_detail': 'dim_event_detail.csv', 
        'event_detail_2': 'dim_event_detail_2.csv',
        'play_detail': 'dim_play_detail.csv',
        'play_detail_2': 'dim_play_detail_2.csv',
    }
    
    for key, filename in dim_files.items():
        filepath = dim_path / filename
        if filepath.exists():
            df = pd.read_csv(filepath)
            code_col = f'{key}_code' if key != 'event_type' else 'event_type_code'
            if code_col in df.columns:
                codes[key] = set(df[code_col].dropna().unique())
            else:
                for col in df.columns:
                    if 'code' in col.lower():
                        codes[key] = set(df[col].dropna().unique())
                        break
    
    # ALWAYS merge play_detail with PLAY_DETAILS constants to ensure new values are available
    try:
        from src.models.dimensions import PLAY_DETAILS
        play_detail_constants = set(p['play_detail'] for p in PLAY_DETAILS)
        if 'play_detail' in codes:
            codes['play_detail'] = codes['play_detail'] | play_detail_constants
        else:
            codes['play_detail'] = play_detail_constants
        logger.info(f"Merged PLAY_DETAILS constants: {len(codes['play_detail'])} total play_detail codes")
    except ImportError:
        logger.warning("Could not load PLAY_DETAILS from dimensions.py")
    
    return codes


def build_normalization_mapping(valid_codes: Set[str], to_simple: bool = True, tracking_values: Set[str] = None) -> Dict[str, str]:
    """
    Build mapping from prefixed values to simple/standard values.
    
    Includes:
    1. Direct mappings where simple version exists (e.g., Defensive_PlayPossession-StickCheck → StickCheck)
    2. Forced mappings where no simple version exists (uses FORCED_BASE_MAPPINGS)
    
    Args:
        valid_codes: Set of all valid codes from dimension table (used to identify simple targets)
        to_simple: If True, map prefixed → simple. If False, do nothing.
        tracking_values: Optional set of actual values from tracking data to map
    
    Returns:
        Dict mapping source → target format
    """
    if not to_simple:
        return {}
    
    mapping = {}
    
    # Identify simple codes from dimension table (targets for mapping)
    simple_codes = set()
    for code in valid_codes:
        if not code.startswith(('Offensive', 'Defensive', 'Recovery')):
            simple_codes.add(code)
    
    # If tracking_values provided, build mappings for those
    # Otherwise, build mappings for prefixed codes in valid_codes
    values_to_map = tracking_values if tracking_values else valid_codes
    
    # Build mappings for all prefixed values
    for code in values_to_map:
        if code and isinstance(code, str) and code.startswith(('Offensive', 'Defensive', 'Recovery')):
            if '-' in code:
                base = code.split('-')[-1]
                
                # Option 1: Direct mapping if simple version exists
                if base in simple_codes:
                    mapping[code] = base
                # Option 2: Forced mapping if base is in FORCED_BASE_MAPPINGS
                elif base in FORCED_BASE_MAPPINGS:
                    target = FORCED_BASE_MAPPINGS[base]
                    # Verify target exists
                    if target in simple_codes or target in valid_codes:
                        mapping[code] = target
    
    return mapping


def standardize_column(
    df: pd.DataFrame, 
    column: str, 
    mapping: Dict[str, str],
    log_changes: bool = True
) -> Tuple[pd.DataFrame, int]:
    """
    Apply mapping to standardize a column.
    
    Returns:
        Tuple of (modified DataFrame, count of changes made)
    """
    if column not in df.columns:
        return df, 0
    
    changes = 0
    
    def normalize(val):
        nonlocal changes
        if pd.isna(val):
            return val
        if val in mapping:
            changes += 1
            return mapping[val]
        return val
    
    df[column] = df[column].apply(normalize)
    
    if log_changes and changes > 0:
        logger.info(f"Column {column}: normalized {changes} values")
    
    return df, changes


def standardize_tracking_data(
    df: pd.DataFrame,
    dim_path: Optional[Path] = None,
    normalize_to_simple: bool = True
) -> pd.DataFrame:
    """
    Standardize all event codes and play_detail columns in tracking data.
    
    This function:
    1. Standardizes event_type, event_detail, event_detail_2 (hyphens → underscores, consolidations)
    2. Standardizes play_detail1, play_detail_2 (prefixed → simple names)
    
    Args:
        df: Tracking DataFrame (fact_event_players or similar)
        dim_path: Path to dimension table CSVs (default: data/output/)
        normalize_to_simple: If True, convert prefixed names to simple/standard names
    
    Returns:
        Standardized DataFrame
    """
    if dim_path is None:
        dim_path = Path('data/output')
    
    # =========================================================================
    # STEP 1: Standardize event codes (hyphens → underscores, consolidations)
    # =========================================================================
    logger.info("Standardizing event codes (hyphens → underscores)...")
    df, event_changes = standardize_event_codes_df(
        df, 
        columns=['event_type', 'event_detail', 'event_detail_2', 'Type'],
        log_changes=True
    )
    total_event_changes = sum(event_changes.values())
    
    # =========================================================================
    # STEP 2: Standardize play_detail values (prefixed → simple)
    # =========================================================================
    logger.info("Standardizing play_detail values (prefixed → simple)...")
    
    # Load valid codes from dimension tables
    dim_codes = load_dimension_codes(dim_path)
    
    # Columns to standardize
    column_mapping = {
        'play_detail1': 'play_detail',
        'play_detail_2': 'play_detail_2',
    }
    
    total_play_changes = 0
    
    for col, dim_key in column_mapping.items():
        if col in df.columns and dim_key in dim_codes:
            valid_codes = dim_codes[dim_key]
            # Get actual values from tracking data to build mappings
            tracking_values = set(df[col].dropna().unique())
            mapping = build_normalization_mapping(valid_codes, to_simple=normalize_to_simple, tracking_values=tracking_values)
            df, changes = standardize_column(df, col, mapping)
            total_play_changes += changes
    
    logger.info(f"Standardization complete: {total_event_changes} event codes + {total_play_changes} play_detail values normalized")
    
    return df


def validate_against_dimensions(
    df: pd.DataFrame,
    dim_path: Optional[Path] = None
) -> Dict[str, Dict]:
    """
    Validate tracking data against dimension tables.
    """
    if dim_path is None:
        dim_path = Path('data/output')
    
    dim_codes = load_dimension_codes(dim_path)
    
    column_mapping = {
        'Type': 'event_type',
        'event_detail': 'event_detail',
        'event_detail_2': 'event_detail_2',
        'play_detail1': 'play_detail',
        'play_detail_2': 'play_detail_2',
    }
    
    results = {}
    
    for col, dim_key in column_mapping.items():
        if col in df.columns and dim_key in dim_codes:
            valid_codes = dim_codes[dim_key]
            tracking_values = set(df[col].dropna().unique())
            
            in_tracking_not_dim = tracking_values - valid_codes
            
            # Count prefixed vs simple
            prefixed = sum(1 for v in tracking_values if str(v).startswith(('Offensive', 'Defensive', 'Recovery')))
            simple = len(tracking_values) - prefixed
            
            results[col] = {
                'valid_codes': len(valid_codes),
                'tracking_values': len(tracking_values),
                'missing_from_dim': list(in_tracking_not_dim),
                'prefixed_count': prefixed,
                'simple_count': simple,
                'match': len(in_tracking_not_dim) == 0
            }
    
    return results


def get_standardization_report(
    df: pd.DataFrame,
    dim_path: Optional[Path] = None
) -> str:
    """Generate a human-readable standardization report."""
    if dim_path is None:
        dim_path = Path('data/output')
    
    dim_codes = load_dimension_codes(dim_path)
    mapping = build_normalization_mapping(dim_codes.get('play_detail', set()), to_simple=True)
    
    lines = ["=" * 70]
    lines.append("PLAY DETAIL STANDARDIZATION REPORT")
    lines.append("=" * 70)
    
    # Per-game analysis
    if 'game_id' in df.columns:
        lines.append("\nPer-Game Analysis (play_detail1):")
        for game_id in sorted(df['game_id'].unique()):
            game = df[df['game_id'] == game_id]
            pd1 = game['play_detail1'].dropna()
            
            prefixed = sum(1 for v in pd1 if str(v).startswith(('Offensive', 'Defensive', 'Recovery')))
            simple = len(pd1) - prefixed
            
            would_change = sum(1 for v in pd1 if v in mapping)
            
            lines.append(f"  Game {game_id}: {len(pd1)} values | {prefixed} prefixed, {simple} simple | {would_change} would normalize")
    
    # Mapping summary
    lines.append(f"\nNormalization mapping: {len(mapping)} prefixed → simple/standard conversions")
    lines.append(f"  Direct mappings: {sum(1 for k,v in mapping.items() if v == k.split('-')[-1])}")
    lines.append(f"  Forced mappings: {sum(1 for k,v in mapping.items() if v != k.split('-')[-1])}")
    
    return "\n".join(lines)


if __name__ == '__main__':
    import sys
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    # Load tracking data
    tracking = pd.read_csv('data/output/fact_event_players.csv', low_memory=False)
    
    # Show report before
    print(get_standardization_report(tracking, Path('data/output')))
    
    # Standardize
    print("\n" + "=" * 70)
    print("APPLYING STANDARDIZATION...")
    print("=" * 70)
    
    tracking_std = standardize_tracking_data(tracking.copy(), Path('data/output'), normalize_to_simple=True)
    
    # Show report after
    print("\n" + get_standardization_report(tracking_std, Path('data/output')))
