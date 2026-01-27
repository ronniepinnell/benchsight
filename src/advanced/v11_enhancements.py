"""
=============================================================================
V11 ENHANCEMENTS
=============================================================================
File: src/advanced/v11_enhancements.py
Version: 11.01
Created: January 7, 2026

Comprehensive enhancements for v11:
1. Create dim_shift_duration table
2. Add shift_duration_id FK to relevant tables
3. Validate and fix dimension tables
4. Create VERSION.txt stamp
5. Generate comprehensive HTML documentation
6. Add suspicious_stats_flag to fact_game_status
7. Clean up qa_suspicious_stats (remove duplicates, stale data)
=============================================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging
import html
from src.core.table_writer import save_output_table

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
OUTPUT_DIR = BASE_DIR / 'data' / 'output'
DOCS_DIR = BASE_DIR / 'docs'
HTML_DIR = DOCS_DIR / 'html'
HTML_TABLES_DIR = HTML_DIR / 'tables'

VERSION = "11.04"
VERSION_DATE = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _deduplicate_event_players(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate (event_index, player_id, role_team) rows.

    Same player on DIFFERENT teams is valid (two people share jersey number).
    Only fix when same player appears multiple times on the SAME team:
    - #8 as event_player_1 AND event_player_2 = duplicate (fix it)
    - #8 as event_player_1 AND opp_player_1 = valid (different people)

    Priority for keeping:
    1. Row with play_detail1 or play_detail_2 populated
    2. If both empty, keep lowest-numbered slot (event_player_1 > event_player_2)

    Args:
        df: DataFrame with event player data

    Returns:
        Deduplicated DataFrame
    """
    original_count = len(df)

    # Determine role_team from player_role (vectorized)
    df = df.copy()
    df['_role_team'] = None
    has_role = df['player_role'].notna()
    is_event_role = df['player_role'].str.startswith('event_', na=False)
    df.loc[has_role & is_event_role, '_role_team'] = 'event'
    df.loc[has_role & ~is_event_role, '_role_team'] = 'opp'

    # Find duplicates: same player_id on same team appearing multiple times in same event
    dup_counts = df.groupby(['event_index', 'player_id', '_role_team']).size()
    dup_combos = dup_counts[dup_counts > 1].index.tolist()

    if not dup_combos:
        df = df.drop(columns=['_role_team'])
        return df

    rows_to_drop = []

    for event_idx, player_id, role_team in dup_combos:
        if pd.isna(player_id) or pd.isna(role_team):
            continue

        # Get all rows for this event/player/team combination
        mask = (
            (df['event_index'] == event_idx) &
            (df['player_id'] == player_id) &
            (df['_role_team'] == role_team)
        )
        player_rows = df[mask]

        if len(player_rows) <= 1:
            continue

        # Priority 1: Keep row with play_detail1 or play_detail_2 populated
        has_detail1 = pd.Series(False, index=player_rows.index)
        has_detail2 = pd.Series(False, index=player_rows.index)

        if 'play_detail1' in player_rows.columns:
            has_detail1 = player_rows['play_detail1'].notna() & (player_rows['play_detail1'] != '')
        if 'play_detail_2' in player_rows.columns:
            has_detail2 = player_rows['play_detail_2'].notna() & (player_rows['play_detail_2'] != '')

        has_detail = player_rows[has_detail1 | has_detail2]

        if len(has_detail) > 0:
            # Keep the first row with details, drop others
            keep_idx = has_detail.index[0]
            drop_indices = [i for i in player_rows.index if i != keep_idx]
            rows_to_drop.extend(drop_indices)
        else:
            # Priority 2: Keep lowest-numbered slot
            def get_role_sort_key(idx):
                role = df.loc[idx, 'player_role']
                if pd.isna(role):
                    return 99
                try:
                    return int(str(role).split('_')[-1])
                except (ValueError, IndexError):
                    return 99

            sorted_indices = sorted(player_rows.index, key=get_role_sort_key)
            keep_idx = sorted_indices[0]
            drop_indices = sorted_indices[1:]
            rows_to_drop.extend(drop_indices)

    # Drop the duplicate rows and the temp column
    cleaned_df = df.drop(rows_to_drop)
    cleaned_df = cleaned_df.drop(columns=['_role_team'])

    removed = original_count - len(cleaned_df)
    if removed > 0:
        logger.info(f"  Removed {removed} duplicate player slots ({len(dup_combos)} events affected)")

    return cleaned_df


def create_dim_shift_duration() -> pd.DataFrame:
    """
    Create dimension table for shift duration buckets.
    
    Buckets based on typical hockey shift lengths:
    - Very Short: < 30 seconds (line change, quick out)
    - Short: 30-45 seconds (typical quick shift)
    - Normal: 45-60 seconds (standard shift)
    - Long: 60-90 seconds (extended shift)
    - Very Long: > 90 seconds (double shift, tired legs)
    """
    logger.info("Creating dim_shift_duration...")
    
    data = [
        {'shift_duration_id': 'SD01', 'duration_bucket': 'Very Short', 'min_seconds': 0, 'max_seconds': 30, 
         'description': 'Quick line change or partial shift', 'fatigue_level': 'Fresh', 'typical_scenario': 'Line change during play'},
        {'shift_duration_id': 'SD02', 'duration_bucket': 'Short', 'min_seconds': 30, 'max_seconds': 45, 
         'description': 'Quick but complete shift', 'fatigue_level': 'Fresh', 'typical_scenario': 'Fast pace, quick changes'},
        {'shift_duration_id': 'SD03', 'duration_bucket': 'Normal', 'min_seconds': 45, 'max_seconds': 60, 
         'description': 'Standard shift duration', 'fatigue_level': 'Moderate', 'typical_scenario': 'Typical game flow'},
        {'shift_duration_id': 'SD04', 'duration_bucket': 'Long', 'min_seconds': 60, 'max_seconds': 90, 
         'description': 'Extended shift', 'fatigue_level': 'Tired', 'typical_scenario': 'Extended zone time, PP/PK'},
        {'shift_duration_id': 'SD05', 'duration_bucket': 'Very Long', 'min_seconds': 90, 'max_seconds': 9999, 
         'description': 'Double shift or exhausted', 'fatigue_level': 'Exhausted', 'typical_scenario': 'Caught on ice, PP/PK'},
    ]
    
    df = pd.DataFrame(data)
    save_output_table(df, 'dim_shift_duration', OUTPUT_DIR)
    logger.info(f"  Created dim_shift_duration: {len(df)} rows")
    return df


def add_shift_duration_fks() -> Dict[str, int]:
    """Add shift_duration_id FK to shift tables."""
    logger.info("Adding shift_duration_id to tables...")
    
    results = {}
    
    # Load dimension
    dim_duration = pd.read_csv(OUTPUT_DIR / 'dim_shift_duration.csv')
    
    def get_duration_id(seconds):
        if pd.isna(seconds):
            return None
        seconds = float(seconds)
        for _, row in dim_duration.iterrows():
            if row['min_seconds'] <= seconds < row['max_seconds']:
                return row['shift_duration_id']
        return 'SD05'  # Default to very long
    
    # Add to fact_shifts
    shifts_tracking_path = OUTPUT_DIR / 'fact_shifts.csv'
    if shifts_tracking_path.exists():
        df = pd.read_csv(shifts_tracking_path, low_memory=False)
        if 'shift_duration' in df.columns:
            df['shift_duration_id'] = df['shift_duration'].apply(get_duration_id)
            save_output_table(df, shifts_tracking_path.stem, shifts_tracking_path.parent)
            results['fact_shifts'] = len(df)
            logger.info(f"  Added shift_duration_id to fact_shifts")
    
    # Add to fact_shift_players
    shifts_player_path = OUTPUT_DIR / 'fact_shift_players.csv'
    if shifts_player_path.exists():
        df = pd.read_csv(shifts_player_path, low_memory=False)
        if 'shift_duration' in df.columns:
            df['shift_duration_id'] = df['shift_duration'].apply(get_duration_id)
            save_output_table(df, shifts_player_path.stem, shifts_player_path.parent)
            results['fact_shift_players'] = len(df)
            logger.info(f"  Added shift_duration_id to fact_shift_players")
    
    # Add to fact_shifts
    shifts_path = OUTPUT_DIR / 'fact_shifts.csv'
    if shifts_path.exists():
        df = pd.read_csv(shifts_path, low_memory=False)
        if 'shift_duration' in df.columns:
            df['shift_duration_id'] = df['shift_duration'].apply(get_duration_id)
            save_output_table(df, shifts_path.stem, shifts_path.parent)
            results['fact_shifts'] = len(df)
            logger.info(f"  Added shift_duration_id to fact_shifts")
    
    return results


def add_event_index_to_tracking():
    """Add event_index and event_player_key columns to fact_event_players."""
    logger.info("Adding event_index to fact_event_players...")
    
    tracking_path = OUTPUT_DIR / 'fact_event_players.csv'
    if not tracking_path.exists():
        logger.warning("fact_event_players.csv not found")
        return
    
    df = pd.read_csv(tracking_path, low_memory=False)
    
    # Add event_index from event_id (extract sequence number)
    # EV1896901001 -> 1
    if 'event_index' not in df.columns:
        df['event_index'] = df['event_id'].str.extract(r'EV\d{5}(\d{5})')[0].astype(int)
        logger.info("  Added event_index")

    # Deduplicate before key generation - same player should not be in multiple slots
    df = _deduplicate_event_players(df)

    # Add event_player_key (format: EP{game_id:05d}{event_index:05d}{player_id})
    # player_id is string like P100001, use as-is (or NULL for missing)
    df['event_player_key'] = (
        'EP' + 
        df['game_id'].astype(str).str.zfill(5) + 
        df['event_index'].astype(str).str.zfill(5) + 
        df['player_id'].fillna('NULL').astype(str)
    )
    logger.info("  Added event_player_key")
    
    # Reorder columns - put key columns first
    key_cols = ['event_player_key', 'game_id', 'event_id', 'event_index', 'player_id', 'player_role']
    existing_key_cols = [c for c in key_cols if c in df.columns]
    other_cols = [c for c in df.columns if c not in key_cols]
    df = df[existing_key_cols + other_cols]
    
    save_output_table(df, tracking_path.stem, tracking_path.parent)
    logger.info(f"  Updated fact_event_players: {len(df)} rows, {len(df.columns)} columns")


def validate_dimension_tables() -> Dict[str, List[str]]:
    """Validate dimension table keys and structure."""
    logger.info("Validating dimension tables...")
    
    issues = {}
    
    # Expected structure for each dimension table
    expected = {
        'dim_event_detail_2': {
            'pk': 'event_detail_2_id',
            'pk_prefix': 'ED2_',
            'required_cols': ['event_detail_2_id', 'event_detail_2_code', 'event_detail_2_name']
        },
        'dim_play_detail_2': {
            'pk': 'play_detail_2_id',
            'pk_prefix': 'PD2_',
            'required_cols': ['play_detail_2_id', 'play_detail_2_code', 'play_detail_2_name']
        },
        'dim_position': {
            'pk': 'position_id',
            'pk_prefix': None,  # Numeric
            'required_cols': ['position_id', 'position_code', 'position_name']
        },
        'dim_venue': {
            'pk': 'venue_id',
            'pk_prefix': None,  # Numeric
            'required_cols': ['venue_id', 'venue_code', 'venue_name']
        },
        'dim_zone': {
            'pk': 'zone_id',
            'pk_prefix': None,  # Numeric
            'required_cols': ['zone_id', 'zone_code', 'zone_name']
        },
    }
    
    for table, spec in expected.items():
        table_issues = []
        path = OUTPUT_DIR / f'{table}.csv'
        
        if not path.exists():
            table_issues.append(f"Table file not found: {path}")
            issues[table] = table_issues
            continue
        
        try:
            df = pd.read_csv(path)
            if len(df) == 0:
                table_issues.append("Table is empty")
                issues[table] = table_issues
                continue
        except pd.errors.EmptyDataError:
            table_issues.append("Table file is empty (no columns)")
            issues[table] = table_issues
            continue
        except Exception as e:
            table_issues.append(f"Error reading table: {e}")
            issues[table] = table_issues
            continue
        
        # Check required columns
        missing_cols = [c for c in spec['required_cols'] if c not in df.columns]
        if missing_cols:
            table_issues.append(f"Missing columns: {missing_cols}")
        
        # Check PK exists and is unique
        pk = spec['pk']
        if pk in df.columns:
            if df[pk].duplicated().any():
                dupes = df[df[pk].duplicated()][pk].tolist()
                table_issues.append(f"Duplicate PKs: {dupes[:5]}")
            
            # Check PK prefix if specified
            if spec['pk_prefix']:
                bad_prefix = df[~df[pk].astype(str).str.startswith(spec['pk_prefix'])]
                if len(bad_prefix) > 0:
                    table_issues.append(f"PKs without proper prefix '{spec['pk_prefix']}': {len(bad_prefix)}")
        else:
            table_issues.append(f"Missing PK column: {pk}")
        
        if table_issues:
            issues[table] = table_issues
        else:
            logger.info(f"  ✓ {table}: Valid")
    
    return issues


def update_game_status_with_suspicious_flag():
    """Add suspicious_stats_flag to fact_game_status."""
    logger.info("Updating fact_game_status with suspicious_stats_flag...")
    
    game_status_path = OUTPUT_DIR / 'fact_game_status.csv'
    suspicious_path = OUTPUT_DIR / 'qa_suspicious_stats.csv'
    
    if not game_status_path.exists():
        logger.warning("fact_game_status.csv not found")
        return
    
    df = pd.read_csv(game_status_path)
    
    # Initialize flag
    df['suspicious_stats_flag'] = False
    df['suspicious_stats_count'] = 0
    df['suspicious_stats_summary'] = ''
    
    if suspicious_path.exists():
        suspicious = pd.read_csv(suspicious_path)
        
        # Group by game_id and count issues
        for game_id in df['game_id'].unique():
            # Filter by game_id, and optionally by resolved status if column exists
            game_suspicious = suspicious[suspicious['game_id'] == game_id]
            
            # If there's a resolved column, only count unresolved
            if 'resolved' in suspicious.columns:
                game_suspicious = game_suspicious[game_suspicious['resolved'] == False]
            
            if len(game_suspicious) > 0:
                df.loc[df['game_id'] == game_id, 'suspicious_stats_flag'] = True
                df.loc[df['game_id'] == game_id, 'suspicious_stats_count'] = len(game_suspicious)
                
                # Create summary based on available columns
                if 'category' in game_suspicious.columns:
                    categories = game_suspicious['category'].value_counts().to_dict()
                    summary = "; ".join([f"{cat}: {count}" for cat, count in categories.items()])
                elif 'flags' in game_suspicious.columns:
                    # New schema uses 'flags' instead of 'category'
                    flags = game_suspicious['flags'].value_counts().to_dict()
                    summary = "; ".join([f"{flag}: {count}" for flag, count in flags.items()])
                else:
                    summary = f"{len(game_suspicious)} issues"
                
                df.loc[df['game_id'] == game_id, 'suspicious_stats_summary'] = summary
    
    save_output_table(df, game_status_path.stem, game_status_path.parent)
    
    flagged_count = df['suspicious_stats_flag'].sum()
    logger.info(f"  Updated fact_game_status: {flagged_count} games with suspicious stats")


def clean_qa_suspicious_stats():
    """Clean up qa_suspicious_stats - remove duplicates and stale data."""
    logger.info("Cleaning qa_suspicious_stats...")
    
    suspicious_path = OUTPUT_DIR / 'qa_suspicious_stats.csv'
    if not suspicious_path.exists():
        logger.warning("qa_suspicious_stats.csv not found")
        return
    
    df = pd.read_csv(suspicious_path)
    original_count = len(df)
    
    # Get list of games that are actually tracked (if file exists)
    game_status_path = OUTPUT_DIR / 'fact_game_status.csv'
    if game_status_path.exists():
        game_status = pd.read_csv(game_status_path)
        if 'tracking_status' in game_status.columns:
            tracked_games = game_status[game_status['tracking_status'].isin(['COMPLETE', 'PARTIAL'])]['game_id'].tolist()
            # Filter to only tracked games
            df = df[df['game_id'].isin(tracked_games)]
    else:
        logger.warning("fact_game_status.csv not found, skipping game filter")
    
    # Remove duplicates based on available columns
    # Check which schema we have
    if 'category' in df.columns and 'stat' in df.columns:
        # Old schema
        dedup_cols = ['game_id', 'player_id', 'category', 'stat']
        sort_cols = ['game_id', 'category', 'stat']
    elif 'suspicious_key' in df.columns:
        # New schema
        dedup_cols = ['suspicious_key']
        sort_cols = ['game_id', 'player_id']
    else:
        # Fallback - just dedup by game and player
        dedup_cols = ['game_id', 'player_id']
        sort_cols = ['game_id', 'player_id']
    
    # Check all columns exist
    dedup_cols = [c for c in dedup_cols if c in df.columns]
    sort_cols = [c for c in sort_cols if c in df.columns]
    
    if dedup_cols:
        df = df.drop_duplicates(subset=dedup_cols, keep='first')
    
    if sort_cols:
        df = df.sort_values(sort_cols)
    
    save_output_table(df, suspicious_path.stem, suspicious_path.parent)
    
    logger.info(f"  Cleaned qa_suspicious_stats: {original_count} -> {len(df)} rows")
    return df


def create_version_stamp():
    """Create VERSION.txt in output directory and docs."""
    logger.info("Creating version stamp...")
    
    version_content = f"""BenchSight Data Warehouse
========================
Version: {VERSION}
Last Updated: {VERSION_DATE}
Generated By: ETL Pipeline v{VERSION}

Tables: {len(list(OUTPUT_DIR.glob('*.csv')))}
Games Tracked: {_count_tracked_games()}

This file is automatically updated when the ETL runs.
"""
    
    # Write to output directory
    (OUTPUT_DIR / 'VERSION.txt').write_text(version_content)
    
    # Write to docs directory
    (DOCS_DIR / 'VERSION.txt').write_text(version_content)
    
    logger.info(f"  Created VERSION.txt (v{VERSION})")


def _count_tracked_games() -> int:
    """Count number of tracked games."""
    try:
        game_status = pd.read_csv(OUTPUT_DIR / 'fact_game_status.csv')
        # Count games with COMPLETE or PARTIAL tracking
        tracked = game_status[game_status['tracking_status'].isin(['COMPLETE', 'PARTIAL'])]
        return len(tracked)
    except:
        return 0


def generate_html_documentation():
    """Generate comprehensive HTML documentation with table previews."""
    logger.info("Generating HTML documentation...")
    
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get all tables
    csv_files = sorted(OUTPUT_DIR.glob('*.csv'))
    
    # Categorize tables
    dim_tables = [f for f in csv_files if f.stem.startswith('dim_')]
    fact_tables = [f for f in csv_files if f.stem.startswith('fact_')]
    qa_tables = [f for f in csv_files if f.stem.startswith('qa_')]
    other_tables = [f for f in csv_files if not f.stem.startswith(('dim_', 'fact_', 'qa_'))]
    
    # Load suspicious stats for alerts
    suspicious_df = None
    if (OUTPUT_DIR / 'qa_suspicious_stats.csv').exists():
        suspicious_df = pd.read_csv(OUTPUT_DIR / 'qa_suspicious_stats.csv')
        # Filter to unresolved only if 'resolved' column exists
        if 'resolved' in suspicious_df.columns:
            suspicious_df = suspicious_df[suspicious_df['resolved'] == False]
    
    # Get list of documentation files
    doc_files = _get_documentation_files()
    
    # Generate main index with documentation links
    _generate_index_html(dim_tables, fact_tables, qa_tables, other_tables, suspicious_df, doc_files)
    
    # Generate individual table pages
    for csv_file in csv_files:
        _generate_table_html(csv_file, suspicious_df)
    
    # Generate suspicious stats alert page
    _generate_suspicious_stats_html(suspicious_df)
    
    logger.info(f"  Generated HTML docs for {len(csv_files)} tables")


def _get_documentation_files() -> Dict[str, List[Path]]:
    """Get all documentation files organized by category."""
    doc_files = {
        'core_docs': [],
        'guides': [],
        'references': [],
    }
    
    # Core docs in docs/
    core_docs = [
        ('LLM_REQUIREMENTS.md', 'LLM Requirements', 'Critical rules for working with this project'),
        ('LLM_HANDOFF.md', 'LLM Handoff', 'Architecture and context for new sessions'),
        ('HONEST_ASSESSMENT.md', 'Honest Assessment', 'Known issues and status'),
        ('VERIFICATION_STATUS.md', 'Verification Status', 'What has been verified'),
        ('CHANGELOG.md', 'Changelog', 'Version history'),
    ]
    
    for filename, title, desc in core_docs:
        path = DOCS_DIR / filename
        if path.exists():
            doc_files['core_docs'].append({'path': path, 'title': title, 'desc': desc})
    
    # Also check root level
    root_req = BASE_DIR / 'LLM_REQUIREMENTS.md'
    if root_req.exists() and not any(d['path'] == root_req for d in doc_files['core_docs']):
        doc_files['core_docs'].insert(0, {'path': root_req, 'title': 'LLM Requirements (Root)', 'desc': 'Primary requirements document'})
    
    return doc_files


def _generate_index_html(dim_tables, fact_tables, qa_tables, other_tables, suspicious_df, doc_files):
    """Generate main index.html with menu navigation only - NO tables on this page."""
    
    suspicious_count = len(suspicious_df) if suspicious_df is not None else 0
    total_tables = len(dim_tables) + len(fact_tables) + len(qa_tables) + len(other_tables)
    games_tracked = _count_tracked_games()
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BenchSight Documentation v{VERSION}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #4a4e69 100%); color: white; padding: 30px 40px; }}
        .header h1 {{ margin: 0 0 10px 0; font-size: 32px; }}
        .header .version {{ background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 14px; }}
        .header .subtitle {{ opacity: 0.8; font-size: 14px; margin-top: 10px; }}
        .nav {{ background: #4a4e69; padding: 0 40px; }}
        .nav a {{ color: white; text-decoration: none; padding: 15px 20px; display: inline-block; font-weight: 500; }}
        .nav a:hover {{ background: rgba(255,255,255,0.1); }}
        .nav a.active {{ background: rgba(255,255,255,0.2); }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 40px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px; margin: 30px 0; }}
        .summary-card {{ background: white; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .summary-card .number {{ font-size: 48px; font-weight: bold; color: #4a4e69; }}
        .summary-card .label {{ color: #888; margin-top: 8px; font-size: 14px; }}
        .cta {{ text-align: center; margin: 40px 0; }}
        .cta-btn {{ display: inline-block; background: #4a4e69; color: white; padding: 15px 40px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 18px; }}
        .cta-btn:hover {{ background: #3a3e59; }}
        .section {{ margin: 50px 0; }}
        .section h2 {{ color: #4a4e69; border-bottom: 2px solid #4a4e69; padding-bottom: 10px; }}
        .doc-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
        .doc-card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .doc-card h3 {{ margin-top: 0; color: #1a1a2e; }}
        .doc-card h3 a {{ color: #4a4e69; text-decoration: none; }}
        .doc-card h3 a:hover {{ text-decoration: underline; }}
        .doc-card p {{ color: #666; font-size: 14px; margin-bottom: 0; line-height: 1.6; }}
        .quick-start {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .quick-start h3 {{ margin-top: 0; color: #1a1a2e; }}
        .quick-start pre {{ background: #2d2d2d; color: #f8f8f2; padding: 20px; border-radius: 8px; overflow-x: auto; font-size: 14px; }}
        .alert {{ padding: 15px 20px; border-radius: 8px; margin: 20px 0; }}
        .alert-warning {{ background: #fff3cd; color: #856404; border: 1px solid #ffc107; }}
        .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #28a745; }}
        footer {{ text-align: center; padding: 40px; color: #888; font-size: 12px; border-top: 1px solid #ddd; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏒 BenchSight <span class="version">v{VERSION}</span></h1>
        <p class="subtitle">NORAD Hockey Analytics | {games_tracked} Games Tracked | {total_tables} Tables</p>
    </div>
    
    <nav class="nav">
        <a href="index.html" class="active">Home</a>
        <a href="tables.html">📊 Tables ({total_tables})</a>
        <a href="schema_diagram.html">🗂️ Schema</a>
        <a href="suspicious_stats.html">⚠️ QA ({suspicious_count})</a>
        <a href="../LLM_REQUIREMENTS.md">📋 Requirements</a>
    </nav>
    
    <div class="container">
        <div class="summary">
            <div class="summary-card">
                <div class="number">{len(dim_tables)}</div>
                <div class="label">Dimensions</div>
            </div>
            <div class="summary-card">
                <div class="number">{len(fact_tables)}</div>
                <div class="label">Facts</div>
            </div>
            <div class="summary-card">
                <div class="number">{len(qa_tables)}</div>
                <div class="label">QA Tables</div>
            </div>
            <div class="summary-card">
                <div class="number">{games_tracked}</div>
                <div class="label">Games</div>
            </div>
        </div>
        
        <div class="cta">
            <a href="tables.html" class="cta-btn">View All Tables →</a>
        </div>
        
        {'<div class="alert alert-warning">⚠️ ' + str(suspicious_count) + ' suspicious stats detected - <a href="suspicious_stats.html">View Details</a></div>' if suspicious_count > 0 else '<div class="alert alert-success">✓ All data quality checks passing</div>'}
        
        <div class="section">
            <h2>📚 Documentation</h2>
            <div class="doc-grid">
                <div class="doc-card">
                    <h3><a href="../LLM_REQUIREMENTS.md">LLM Requirements</a></h3>
                    <p>Critical rules and constraints. Read this first before making any changes.</p>
                </div>
                <div class="doc-card">
                    <h3><a href="tables.html">Data Dictionary</a></h3>
                    <p>Browse all {total_tables} tables with column schemas and data previews.</p>
                </div>
                <div class="doc-card">
                    <h3><a href="schema_diagram.html">Schema Diagram</a></h3>
                    <p>Visual representation of table relationships and key formats.</p>
                </div>
                <div class="doc-card">
                    <h3><a href="../docs/HONEST_ASSESSMENT.md">Honest Assessment</a></h3>
                    <p>Current status, what works well, and known limitations.</p>
                </div>
                <div class="doc-card">
                    <h3><a href="../docs/LLM_HANDOFF.md">LLM Handoff</a></h3>
                    <p>Architecture context for new chat sessions.</p>
                </div>
                <div class="doc-card">
                    <h3><a href="../docs/CHANGELOG.md">Changelog</a></h3>
                    <p>Version history and recent changes.</p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🚀 Quick Start</h2>
            <div class="quick-start">
                <h3>Run the ETL Pipeline</h3>
                <pre># Full ETL - process all games
python -m src.etl_orchestrator full

# Check status
python -m src.etl_orchestrator status

# Run tests
python3 -m pytest tests/test_etl.py -v</pre>
            </div>
        </div>
    </div>
    
    <footer>
        BenchSight v{VERSION} | NORAD Hockey Analytics<br>
        Generated: {VERSION_DATE} (US Mountain Time)
    </footer>
</body>
</html>"""
    
    (HTML_DIR / 'index.html').write_text(html_content)
    
    # Also generate tables.html page
    _generate_tables_html(dim_tables, fact_tables, qa_tables, other_tables)


def _generate_table_links(tables) -> str:
    """Generate HTML for table links."""
    links = []
    for f in tables:
        try:
            df = pd.read_csv(f, nrows=1)
            row_count = sum(1 for _ in open(f)) - 1  # Fast row count
            col_count = len(df.columns)
        except:
            row_count = 0
            col_count = 0
        
        links.append(f"""
            <div class="table-item">
                <a href="tables/{f.stem}.html">{f.stem}</a>
                <div class="table-meta">{row_count:,} rows × {col_count} cols</div>
            </div>
        """)
    
    return '\n'.join(links)


def _generate_tables_html(dim_tables, fact_tables, qa_tables, other_tables):
    """Generate tables.html with all table listings."""
    
    total = len(dim_tables) + len(fact_tables) + len(qa_tables) + len(other_tables)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tables - BenchSight v{VERSION}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #4a4e69 100%); color: white; padding: 20px 40px; }}
        .header h1 {{ margin: 0; }}
        .nav {{ background: #4a4e69; padding: 0 40px; }}
        .nav a {{ color: white; text-decoration: none; padding: 15px 20px; display: inline-block; font-weight: 500; }}
        .nav a:hover {{ background: rgba(255,255,255,0.1); }}
        .nav a.active {{ background: rgba(255,255,255,0.2); }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 40px; }}
        h2 {{ color: #4a4e69; border-bottom: 2px solid #4a4e69; padding-bottom: 10px; margin-top: 40px; }}
        .table-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }}
        .table-item {{ background: white; padding: 15px 18px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .table-item:hover {{ box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        .table-item a {{ color: #4a4e69; text-decoration: none; font-weight: 500; }}
        .table-item a:hover {{ color: #1a1a2e; text-decoration: underline; }}
        .table-item .meta {{ color: #888; font-size: 11px; }}
        footer {{ text-align: center; padding: 40px; color: #888; font-size: 12px; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 BenchSight Tables ({total})</h1>
    </div>
    
    <nav class="nav">
        <a href="index.html">Home</a>
        <a href="tables.html" class="active">📊 Tables ({total})</a>
        <a href="schema_diagram.html">🗂️ Schema</a>
        <a href="suspicious_stats.html">⚠️ QA</a>
        <a href="../LLM_REQUIREMENTS.md">📋 Requirements</a>
    </nav>
    
    <div class="container">
        <h2>📦 Dimension Tables ({len(dim_tables)})</h2>
        <div class="table-grid">
            {_generate_table_links(dim_tables)}
        </div>
        
        <h2>📈 Fact Tables ({len(fact_tables)})</h2>
        <div class="table-grid">
            {_generate_table_links(fact_tables)}
        </div>
        
        <h2>🔍 QA Tables ({len(qa_tables)})</h2>
        <div class="table-grid">
            {_generate_table_links(qa_tables)}
        </div>
        
        {f'<h2>📁 Other ({len(other_tables)})</h2><div class="table-grid">{_generate_table_links(other_tables)}</div>' if other_tables else ''}
    </div>
    
    <footer>
        BenchSight v{VERSION} | {VERSION_DATE}
    </footer>
</body>
</html>"""
    
    (HTML_DIR / 'tables.html').write_text(html_content)


def _generate_table_html(csv_file: Path, suspicious_df):
    """Generate HTML page for a single table."""
    
    table_name = csv_file.stem
    
    try:
        df = pd.read_csv(csv_file, low_memory=False)
        preview_df = df.head(20)
    except Exception as e:
        preview_df = pd.DataFrame()
        df = pd.DataFrame()
    
    # Check if this table has suspicious data
    has_suspicious = False
    suspicious_note = ""
    if suspicious_df is not None and len(suspicious_df) > 0:
        if 'game_id' in df.columns:
            game_ids = df['game_id'].unique()
            suspicious_games = suspicious_df[suspicious_df['game_id'].isin(game_ids)]
            if len(suspicious_games) > 0:
                has_suspicious = True
                suspicious_note = f"⚠️ {len(suspicious_games)} suspicious stat entries for games in this table"
    
    # Generate column info
    col_info = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null = df[col].notna().sum()
        null_pct = (1 - non_null / len(df)) * 100 if len(df) > 0 else 0
        col_info.append(f"<tr><td>{html.escape(col)}</td><td>{dtype}</td><td>{non_null:,}</td><td>{null_pct:.1f}%</td></tr>")
    
    # Generate preview table
    preview_html = preview_df.to_html(classes='data-table', index=False, escape=True) if len(preview_df) > 0 else "<p>No data</p>"
    
    alert_html = f'<div class="alert alert-danger">{suspicious_note}</div>' if has_suspicious else ''
    
    # Special visualizations for certain tables
    viz_html = ""
    if table_name == 'dim_net_location':
        viz_html = """
        <div class="card">
            <h2>🥅 Net Zone Visualization</h2>
            <p>Goal net divided into zones for shot placement tracking (goalie's perspective looking out):</p>
            <svg viewBox="0 0 300 200" style="max-width:400px; border:1px solid #ddd; background:#fff; margin: 20px 0;">
                <rect x="50" y="40" width="200" height="120" fill="none" stroke="#333" stroke-width="3"/>
                <line x1="116" y1="40" x2="116" y2="160" stroke="#999" stroke-width="1" stroke-dasharray="5,5"/>
                <line x1="183" y1="40" x2="183" y2="160" stroke="#999" stroke-width="1" stroke-dasharray="5,5"/>
                <line x1="50" y1="100" x2="250" y2="100" stroke="#999" stroke-width="1" stroke-dasharray="5,5"/>
                <text x="83" y="75" text-anchor="middle" font-size="11" fill="#333">Top</text>
                <text x="83" y="90" text-anchor="middle" font-size="11" fill="#333">Left</text>
                <text x="150" y="75" text-anchor="middle" font-size="11" fill="#333">Top</text>
                <text x="150" y="90" text-anchor="middle" font-size="11" fill="#333">Center</text>
                <text x="216" y="75" text-anchor="middle" font-size="11" fill="#333">Top</text>
                <text x="216" y="90" text-anchor="middle" font-size="11" fill="#333">Right</text>
                <text x="83" y="125" text-anchor="middle" font-size="11" fill="#333">Bottom</text>
                <text x="83" y="140" text-anchor="middle" font-size="11" fill="#333">Left</text>
                <text x="150" y="125" text-anchor="middle" font-size="11" fill="#333">Bottom</text>
                <text x="150" y="140" text-anchor="middle" font-size="11" fill="#333">Center</text>
                <text x="216" y="125" text-anchor="middle" font-size="11" fill="#333">Bottom</text>
                <text x="216" y="140" text-anchor="middle" font-size="11" fill="#333">Right</text>
                <circle cx="50" cy="40" r="4" fill="#c00"/>
                <circle cx="250" cy="40" r="4" fill="#c00"/>
                <circle cx="50" cy="160" r="4" fill="#c00"/>
                <circle cx="250" cy="160" r="4" fill="#c00"/>
                <text x="150" y="20" text-anchor="middle" font-size="12" font-weight="bold">Hockey Net - Shot Zones</text>
                <text x="150" y="185" text-anchor="middle" font-size="9" fill="#888">Posts shown in red</text>
            </svg>
        </div>
        """
    elif table_name == 'dim_zone':
        viz_html = """
        <div class="card">
            <h2>🏒 Rink Zone Visualization</h2>
            <p>Ice rink divided into three zones (home team perspective):</p>
            <svg viewBox="0 0 600 220" style="max-width:700px; border:1px solid #ddd; background:#fff; margin: 20px 0;">
                <rect x="10" y="30" width="580" height="160" rx="50" fill="#e8f4f8" stroke="#333" stroke-width="2"/>
                <line x1="300" y1="30" x2="300" y2="190" stroke="#c00" stroke-width="3"/>
                <line x1="175" y1="30" x2="175" y2="190" stroke="#00f" stroke-width="3"/>
                <line x1="425" y1="30" x2="425" y2="190" stroke="#00f" stroke-width="3"/>
                <line x1="60" y1="30" x2="60" y2="190" stroke="#c00" stroke-width="2"/>
                <line x1="540" y1="30" x2="540" y2="190" stroke="#c00" stroke-width="2"/>
                <rect x="30" y="90" width="30" height="40" fill="none" stroke="#c00" stroke-width="2"/>
                <rect x="540" y="90" width="30" height="40" fill="none" stroke="#c00" stroke-width="2"/>
                <text x="92" y="115" text-anchor="middle" font-size="18" font-weight="bold" fill="#333">DZ</text>
                <text x="92" y="135" text-anchor="middle" font-size="11" fill="#666">Defensive</text>
                <text x="300" y="115" text-anchor="middle" font-size="18" font-weight="bold" fill="#333">NZ</text>
                <text x="300" y="135" text-anchor="middle" font-size="11" fill="#666">Neutral</text>
                <text x="508" y="115" text-anchor="middle" font-size="18" font-weight="bold" fill="#333">OZ</text>
                <text x="508" y="135" text-anchor="middle" font-size="11" fill="#666">Offensive</text>
                <text x="300" y="15" text-anchor="middle" font-size="12" font-weight="bold">Ice Rink Zones</text>
                <text x="300" y="210" text-anchor="middle" font-size="9" fill="#888">Blue lines mark zone boundaries | Red line = center ice</text>
            </svg>
        </div>
        """
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{table_name} - BenchSight</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1600px; margin: 0 auto; }}
        h1 {{ color: #1a1a2e; }}
        .back-link {{ color: #4a4e69; text-decoration: none; }}
        .back-link:hover {{ text-decoration: underline; }}
        .meta {{ background: #e8e8e8; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .alert {{ padding: 15px 20px; border-radius: 8px; margin: 20px 0; font-weight: bold; }}
        .alert-danger {{ background: #f8d7da; color: #721c24; border: 2px solid #f5c6cb; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h2 {{ color: #4a4e69; margin-top: 0; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 13px; }}
        th {{ background: #4a4e69; color: white; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .data-table {{ overflow-x: auto; display: block; }}
        .columns-table {{ max-width: 600px; }}
        footer {{ margin-top: 40px; padding: 20px; text-align: center; color: #888; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <p><a href="../index.html" class="back-link">← Back to Index</a></p>
        <h1>{table_name}</h1>
        
        {alert_html}
        
        <div class="meta">
            <strong>Rows:</strong> {len(df):,} | 
            <strong>Columns:</strong> {len(df.columns)} |
            <strong>Last Updated:</strong> {VERSION_DATE} |
            <strong>Version:</strong> {VERSION}
        </div>
        
        {viz_html}
        
        <div class="card">
            <h2>Column Schema</h2>
            <table class="columns-table">
                <tr><th>Column</th><th>Type</th><th>Non-Null</th><th>Null %</th></tr>
                {''.join(col_info)}
            </table>
        </div>
        
        <div class="card">
            <h2>Data Preview (First 20 Rows)</h2>
            <div style="overflow-x: auto;">
                {preview_html}
            </div>
        </div>
        
        <footer>
            BenchSight v{VERSION} | Generated {VERSION_DATE}
        </footer>
    </div>
</body>
</html>"""
    
    # Ensure tables subfolder exists
    HTML_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    (HTML_TABLES_DIR / f'{table_name}.html').write_text(html_content)


def _generate_suspicious_stats_html(suspicious_df):
    """Generate dedicated suspicious stats page."""
    
    if suspicious_df is None or len(suspicious_df) == 0:
        suspicious_html = "<p class='success'>✓ No suspicious stats detected. All data looks good!</p>"
        games_affected = 0
        by_game_html = ""
    else:
        games_affected = suspicious_df['game_id'].nunique()
        
        # Group by game
        by_game_html = ""
        for game_id in suspicious_df['game_id'].unique():
            game_data = suspicious_df[suspicious_df['game_id'] == game_id]
            rows = []
            for _, row in game_data.iterrows():
                # Handle different schema versions
                severity = row.get('severity', 'INFO')
                severity_class = 'severity-warning' if severity == 'WARNING' else 'severity-info'
                rows.append(f"""
                    <tr class="{severity_class}">
                        <td>{html.escape(str(row.get('player_name', row.get('player_id', 'N/A'))))}</td>
                        <td>{html.escape(str(row.get('category', row.get('flags', ''))))}</td>
                        <td>{html.escape(str(row.get('stat', '')))}</td>
                        <td>{row.get('value', row.get('goals', ''))}</td>
                        <td>{html.escape(str(row.get('note', '')))}</td>
                    </tr>
                """)
            
            by_game_html += f"""
                <div class="game-section">
                    <h3>Game {game_id}</h3>
                    <table>
                        <tr><th>Player</th><th>Category</th><th>Stat</th><th>Value</th><th>Note</th></tr>
                        {''.join(rows)}
                    </table>
                </div>
            """
        
        suspicious_html = f"""
            <div class="alert alert-danger">
                <h2>⚠️ {len(suspicious_df)} Suspicious Statistics Detected</h2>
                <p>{games_affected} games affected - requires review</p>
            </div>
        """
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Suspicious Stats - BenchSight</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #721c24; }}
        .back-link {{ color: #4a4e69; text-decoration: none; }}
        .alert {{ padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .alert-danger {{ background: #f8d7da; color: #721c24; border: 3px solid #f5c6cb; }}
        .success {{ background: #d4edda; color: #155724; padding: 20px; border-radius: 8px; }}
        .game-section {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h3 {{ color: #4a4e69; margin-top: 0; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background: #4a4e69; color: white; }}
        .severity-warning {{ background: #fff3cd; }}
        .severity-info {{ background: #d1ecf1; }}
        footer {{ margin-top: 40px; padding: 20px; text-align: center; color: #888; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <p><a href="index.html" class="back-link">← Back to Index</a></p>
        <h1>🚨 Suspicious Statistics Report</h1>
        <p><strong>Last Checked:</strong> {VERSION_DATE} | <strong>Version:</strong> {VERSION}</p>
        
        {suspicious_html}
        
        {by_game_html}
        
        <footer>
            BenchSight v{VERSION} | Generated {VERSION_DATE}
        </footer>
    </div>
</body>
</html>"""
    
    (HTML_DIR / 'suspicious_stats.html').write_text(html_content)


def run_all_enhancements():
    """Run all v11 enhancements."""
    logger.info("=" * 60)
    logger.info(f"RUNNING V{VERSION} ENHANCEMENTS")
    logger.info("=" * 60)
    
    # 1. Create dim_shift_duration
    create_dim_shift_duration()
    
    # 2. Add shift_duration_id FKs
    add_shift_duration_fks()
    
    # 3. Add event_index to fact_event_players
    add_event_index_to_tracking()
    
    # 4. Validate dimension tables
    issues = validate_dimension_tables()
    if issues:
        logger.info(f"Dimension table notes (BLB data uses actual IDs, not prefixed): {issues}")
    
    # 5. Propagate TOI to event-derived tables
    propagate_toi_to_derived_tables()
    
    # 6. Clean QA suspicious stats
    clean_qa_suspicious_stats()
    
    # 7. Update game status with suspicious flag
    update_game_status_with_suspicious_flag()
    
    # 8. Create version stamp
    create_version_stamp()
    
    # 9. Generate HTML documentation
    generate_html_documentation()
    
    logger.info("\n" + "=" * 60)
    logger.info(f"V{VERSION} ENHANCEMENTS COMPLETE")
    logger.info("=" * 60)


def propagate_toi_to_derived_tables():
    """Propagate TOI and time columns from fact_events to derived tables."""
    logger.info("Propagating TOI to event-derived tables...")
    
    # Load fact_events with TOI columns
    events_path = OUTPUT_DIR / 'fact_events.csv'
    if not events_path.exists():
        logger.warning("fact_events.csv not found, skipping TOI propagation")
        return
    
    events = pd.read_csv(events_path, low_memory=False)
    
    # Columns to propagate
    toi_cols = [
        'time_to_next_event', 'time_from_last_event',
        'time_to_next_goal_for', 'time_to_next_goal_against',
        'time_from_last_goal_for', 'time_from_last_goal_against',
        'time_to_next_stoppage', 'time_from_last_stoppage',
        'event_player_1_toi', 'event_player_2_toi', 'event_player_3_toi',
        'event_player_4_toi', 'event_player_5_toi', 'event_player_6_toi',
        'opp_player_1_toi', 'opp_player_2_toi', 'opp_player_3_toi',
        'opp_player_4_toi', 'opp_player_5_toi', 'opp_player_6_toi',
        'team_on_ice_toi_avg', 'team_on_ice_toi_min', 'team_on_ice_toi_max',
        'opp_on_ice_toi_avg', 'opp_on_ice_toi_min', 'opp_on_ice_toi_max',
    ]
    
    # Filter to columns that exist
    available_cols = [c for c in toi_cols if c in events.columns]
    if not available_cols:
        logger.warning("No TOI columns found in fact_events")
        return
    
    # Create lookup by event_id
    toi_lookup = events[['event_id'] + available_cols].drop_duplicates(subset=['event_id'])
    
    # Tables to enhance
    derived_tables = [
        'fact_scoring_chances',
        'fact_scoring_chances_detailed',
        'fact_zone_entries',
        'fact_zone_exits',
        'fact_faceoffs',
        'fact_rushes',
        'fact_rush_events',
        'fact_saves',
        'fact_breakouts',
    ]
    
    for table_name in derived_tables:
        table_path = OUTPUT_DIR / f'{table_name}.csv'
        if not table_path.exists():
            continue
        
        try:
            df = pd.read_csv(table_path, low_memory=False)
            
            if len(df) == 0 or 'event_id' not in df.columns:
                continue
            
            # Remove existing TOI columns to avoid duplicates
            for col in available_cols:
                if col in df.columns:
                    df = df.drop(columns=[col])
            
            # Merge TOI columns
            original_len = len(df)
            df = df.merge(toi_lookup, on='event_id', how='left')
            
            if len(df) != original_len:
                logger.warning(f"  Row count changed for {table_name}: {original_len} -> {len(df)}")
            
            save_output_table(df, table_path.stem, table_path.parent)
            logger.info(f"  ✓ {table_name}: Added {len(available_cols)} TOI columns")
            
        except Exception as e:
            logger.error(f"  Error enhancing {table_name}: {e}")


if __name__ == '__main__':
    run_all_enhancements()
