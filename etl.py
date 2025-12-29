#!/usr/bin/env python3
"""
BENCHSIGHT v5.0.0 - PRODUCTION ETL
==================================

Requirements:
1. Drop ALL columns ending in _ (formula/helper columns)
2. Exclude games 18965, 18993, 19032 from event/shift tracking
3. Ensure player_id present in ALL tables with player data
4. Handle duplicate jersey numbers by using (game_id, team, player_number)
5. Bulletproof keys and integrity
6. Clean folder structure

Author: Senior Dev
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION
# ============================================================

BLB_PATH = Path("data/BLB_Tables.xlsx")
GAMES_DIR = Path("data/raw/games")
OUTPUT_DIR = Path("data/output")
LOG_FILE = Path("logs/etl_v5.log")

# Games to include in tracking data (complete games only)
VALID_TRACKING_GAMES = ['18969', '18977', '18981', '18987', '18991']

# Games to EXCLUDE from tracking (incomplete)
EXCLUDED_GAMES = ['18965', '18993', '19032']

# ============================================================
# LOGGING
# ============================================================

class ETLLogger:
    def __init__(self):
        self.logs = []
        self.warnings = []
        self.errors = []
        self.issues = []
        
    def info(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] INFO: {msg}"
        print(entry)
        self.logs.append(entry)
    
    def warn(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] WARN: {msg}"
        print(entry)
        self.logs.append(entry)
        self.warnings.append(msg)
    
    def error(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] ERROR: {msg}"
        print(entry)
        self.logs.append(entry)
        self.errors.append(msg)
    
    def issue(self, msg):
        """Log potential data issue for user review"""
        self.issues.append(msg)
        self.warn(f"ISSUE: {msg}")
    
    def section(self, title):
        print(f"\n{'='*60}")
        print(title)
        print('='*60)
    
    def save(self, path):
        with open(path, 'w') as f:
            f.write('\n'.join(self.logs))
            if self.issues:
                f.write('\n\n=== ISSUES FOR USER REVIEW ===\n')
                for issue in self.issues:
                    f.write(f"- {issue}\n")

log = ETLLogger()

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def drop_underscore_columns(df):
    """Drop ALL columns ending in _ (formula/helper columns)"""
    underscore_cols = [c for c in df.columns if c.endswith('_')]
    if underscore_cols:
        df = df.drop(columns=underscore_cols)
    return df, underscore_cols

def drop_index_and_unnamed(df):
    """Drop index and Unnamed columns"""
    drop_cols = []
    if 'index' in df.columns:
        drop_cols.append('index')
    drop_cols.extend([c for c in df.columns if 'Unnamed' in str(c)])
    return df.drop(columns=drop_cols, errors='ignore')

def clean_numeric_index(val):
    """Convert '1000.0' to '1000'"""
    if pd.isna(val) or val == '' or str(val).lower() in ['nan', 'x', 'none']:
        return None
    try:
        return str(int(float(val)))
    except:
        return None

def validate_key(df, key_col, table_name):
    """Validate a key column has no nulls and no duplicates"""
    issues = []
    
    if key_col not in df.columns:
        issues.append(f"{table_name}: Missing key column '{key_col}'")
        return issues
    
    null_count = df[key_col].isna().sum()
    if null_count > 0:
        issues.append(f"{table_name}.{key_col}: {null_count} NULL values")
    
    dup_count = df.duplicated(subset=[key_col]).sum()
    if dup_count > 0:
        issues.append(f"{table_name}.{key_col}: {dup_count} duplicates")
    
    return issues

def save_table(df, name):
    """Save table and return stats"""
    path = OUTPUT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    return len(df), len(df.columns)

# ============================================================
# PHASE 1: LOAD BLB TABLES
# ============================================================

def load_blb_tables():
    log.section("PHASE 1: LOAD BLB_TABLES.XLSX")
    
    xl = pd.ExcelFile(BLB_PATH)
    
    # Sheet to output name mapping
    sheet_map = {
        'dim_player': 'dim_player',
        'dim_team': 'dim_team',
        'dim_league': 'dim_league',
        'dim_season': 'dim_season',
        'dim_schedule': 'dim_schedule',
        'dim_playerurlref': 'dim_playerurlref',
        'dim_rinkboxcoord': 'dim_rinkboxcoord',
        'dim_rinkcoordzones': 'dim_rinkcoordzones',
        'dim_randomnames': 'dim_randomnames',
        'fact_gameroster': 'fact_gameroster',
        'fact_leadership': 'fact_leadership',
        'fact_registration': 'fact_registration',
        'fact_draft': 'fact_draft',
        'Fact_PlayerGames': 'fact_playergames',
    }
    
    # Primary keys for each table
    primary_keys = {
        'dim_player': 'player_id',
        'dim_team': 'team_id',
        'dim_league': 'league_id',
        'dim_season': 'season_id',
        'dim_schedule': 'game_id',
        'fact_gameroster': 'player_game_id',
        'fact_leadership': None,  # Composite key
        'fact_registration': 'player_season_registration_id',
        'fact_draft': 'player_draft_id',
        'fact_playergames': None,  # Will create
    }
    
    loaded = {}
    
    for sheet, output in sheet_map.items():
        if sheet not in xl.sheet_names:
            log.warn(f"Sheet '{sheet}' not found")
            continue
        
        log.info(f"Loading {sheet}...")
        df = pd.read_excel(BLB_PATH, sheet_name=sheet, dtype=str)
        
        # Clean
        df = drop_index_and_unnamed(df)
        df, dropped = drop_underscore_columns(df)
        if dropped:
            log.info(f"  Dropped {len(dropped)} underscore columns")
        
        # Deduplicate based on primary key if exists
        pk = primary_keys.get(output)
        if pk and pk in df.columns:
            before = len(df)
            df = df.drop_duplicates(subset=[pk])
            if len(df) < before:
                log.info(f"  Deduped on {pk}: {before} -> {len(df)}")
            
            # Validate key
            issues = validate_key(df, pk, output)
            for issue in issues:
                log.error(issue)
        
        # Special handling for fact_playergames - create proper key
        if output == 'fact_playergames':
            df['player_game_id'] = df.apply(
                lambda r: f"PG_{r.get('ID', '')}_{r.get('Player', '')[:20]}".replace(' ', '_'),
                axis=1
            )
            before = len(df)
            df = df.drop_duplicates(subset=['player_game_id'])
            log.info(f"  Created player_game_id, deduped: {before} -> {len(df)}")
        
        loaded[output] = df
        rows, cols = save_table(df, output)
        log.info(f"  Saved {output}: {rows:,} rows, {cols} cols")
    
    return loaded

# ============================================================
# PHASE 2: BUILD PLAYER LOOKUP
# ============================================================

def build_player_lookup(gameroster_df):
    """Build lookup for (game_id, team_name, player_number) -> player_id
    
    This handles duplicate jersey numbers across teams in same game.
    """
    log.section("PHASE 2: BUILD PLAYER LOOKUP")
    
    lookup = {}
    conflicts = []
    
    for _, row in gameroster_df.iterrows():
        game_id = str(row.get('game_id', ''))
        team_name = str(row.get('team_name', '')).strip()
        player_num = str(row.get('player_game_number', '')).strip()
        player_id = row.get('player_id')
        
        if game_id and player_num and pd.notna(player_id):
            # Key includes team to handle duplicate numbers
            key = (game_id, team_name, player_num)
            
            if key in lookup and lookup[key] != player_id:
                conflicts.append(f"Conflict: {key} -> {lookup[key]} vs {player_id}")
            
            lookup[key] = player_id
            
            # Also create key without team for fallback
            simple_key = (game_id, player_num)
            if simple_key not in lookup:
                lookup[simple_key] = player_id
    
    log.info(f"Built lookup with {len(lookup)} mappings")
    
    if conflicts:
        log.warn(f"Found {len(conflicts)} conflicts (duplicate numbers on different teams)")
        for c in conflicts[:5]:
            log.warn(f"  {c}")
    
    return lookup

# ============================================================
# PHASE 3: LOAD TRACKING DATA
# ============================================================

def load_tracking_data(player_lookup):
    log.section("PHASE 3: LOAD TRACKING DATA")
    log.info(f"Valid games: {VALID_TRACKING_GAMES}")
    log.info(f"Excluded games: {EXCLUDED_GAMES}")
    
    all_events = []
    all_shifts = []
    
    for game_id in VALID_TRACKING_GAMES:
        game_dir = GAMES_DIR / game_id
        if not game_dir.exists():
            log.error(f"Game directory not found: {game_dir}")
            continue
        
        # Find tracking file
        tracking_files = list(game_dir.glob("*_tracking.xlsx"))
        tracking_files = [f for f in tracking_files if 'bkup' not in str(f).lower()]
        
        if not tracking_files:
            log.error(f"No tracking file for game {game_id}")
            continue
        
        xlsx_path = tracking_files[0]
        log.info(f"\nLoading game {game_id} from {xlsx_path.name}...")
        
        try:
            xl = pd.ExcelFile(xlsx_path)
            
            # Load events
            if 'events' in xl.sheet_names:
                df = pd.read_excel(xlsx_path, sheet_name='events', dtype=str)
                df['game_id'] = game_id
                
                # Drop underscore columns
                df, dropped = drop_underscore_columns(df)
                log.info(f"  events: {len(df)} raw rows, dropped {len(dropped)} underscore cols")
                
                # Filter valid rows (has tracking_event_index)
                if 'tracking_event_index' in df.columns:
                    df = df[df['tracking_event_index'].apply(
                        lambda x: pd.notna(x) and str(x).replace('.', '').replace('-', '').isdigit()
                    )]
                    log.info(f"  events: {len(df)} valid rows (by tracking_event_index)")
                
                all_events.append(df)
            
            # Load shifts
            if 'shifts' in xl.sheet_names:
                df = pd.read_excel(xlsx_path, sheet_name='shifts', dtype=str)
                df['game_id'] = game_id
                
                df, dropped = drop_underscore_columns(df)
                log.info(f"  shifts: {len(df)} raw rows, dropped {len(dropped)} underscore cols")
                
                # Filter valid rows
                if 'shift_index' in df.columns:
                    df = df[df['shift_index'].apply(
                        lambda x: pd.notna(x) and str(x).replace('.', '').isdigit()
                    )]
                    log.info(f"  shifts: {len(df)} valid rows (by shift_index)")
                
                all_shifts.append(df)
                
        except Exception as e:
            log.error(f"Error loading game {game_id}: {e}")
    
    results = {}
    
    # Process events
    if all_events:
        df = pd.concat(all_events, ignore_index=True)
        df = drop_index_and_unnamed(df)
        
        # Generate event_id
        df['event_index'] = df['tracking_event_index'].apply(clean_numeric_index)
        df['event_id'] = df.apply(
            lambda r: f"E_{r['game_id']}_{r['event_index']}" 
                      if r['game_id'] and r['event_index'] else None,
            axis=1
        )
        df = df[df['event_id'].notna()]
        
        # Link player_id
        df = link_player_ids(df, player_lookup, 'player_game_number', 'team_venue')
        
        # Reorder columns
        priority_cols = ['event_id', 'game_id', 'event_index', 'player_id', 'player_game_number']
        other_cols = [c for c in df.columns if c not in priority_cols]
        df = df[priority_cols + other_cols]
        
        results['fact_events_tracking'] = df
        save_table(df, 'fact_events_tracking')
        log.info(f"\nCombined events: {len(df):,} rows, {df['game_id'].nunique()} games")
        log.info(f"  player_id linked: {df['player_id'].notna().sum()}/{len(df)}")
    
    # Process shifts
    if all_shifts:
        df = pd.concat(all_shifts, ignore_index=True)
        df = drop_index_and_unnamed(df)
        
        # Generate shift_id
        df['shift_index'] = df['shift_index'].apply(clean_numeric_index)
        df['shift_id'] = df.apply(
            lambda r: f"S_{r['game_id']}_{r['shift_index']}" 
                      if r['game_id'] and r['shift_index'] else None,
            axis=1
        )
        df = df[df['shift_id'].notna()]
        
        # Reorder columns
        priority_cols = ['shift_id', 'game_id', 'shift_index']
        other_cols = [c for c in df.columns if c not in priority_cols]
        df = df[priority_cols + other_cols]
        
        results['fact_shifts_tracking'] = df
        save_table(df, 'fact_shifts_tracking')
        log.info(f"Combined shifts: {len(df):,} rows, {df['game_id'].nunique()} games")
    
    return results

def link_player_ids(df, lookup, player_col, team_col):
    """Link player_id using lookup, handling team for duplicates"""
    
    def get_player_id(row):
        game_id = str(row.get('game_id', ''))
        player_num = str(row.get(player_col, '')).strip()
        
        if not game_id or not player_num:
            return None
        
        # Try with team first (more accurate)
        team = str(row.get(team_col, '')).strip()
        if team:
            # Map venue to team name if needed
            if team.lower() in ['home', 'h']:
                team = str(row.get('home_team', '')).strip()
            elif team.lower() in ['away', 'a']:
                team = str(row.get('away_team', '')).strip()
            
            key = (game_id, team, player_num)
            if key in lookup:
                return lookup[key]
        
        # Fallback to simple lookup
        simple_key = (game_id, player_num)
        return lookup.get(simple_key)
    
    df['player_id'] = df.apply(get_player_id, axis=1)
    return df

# ============================================================
# PHASE 4: CREATE DERIVED TABLES
# ============================================================

def create_derived_tables(tracking_data, player_lookup):
    log.section("PHASE 4: CREATE DERIVED TABLES")
    
    # 1. fact_events - one row per event
    if 'fact_events_tracking' in tracking_data:
        log.info("Creating fact_events...")
        tracking = tracking_data['fact_events_tracking']
        
        events = tracking.groupby('event_id', as_index=False).first()
        
        # Select meaningful columns
        keep_cols = ['event_id', 'game_id', 'event_index', 'period', 'Type',
                     'event_detail', 'event_detail_2', 'event_successful',
                     'event_team_zone', 'shift_index', 'linked_event_index',
                     'home_team', 'away_team', 'duration']
        events = events[[c for c in keep_cols if c in events.columns]]
        
        # Rename for cleaner schema
        rename = {'Type': 'event_type', 'event_detail': 'detail_1',
                  'event_detail_2': 'detail_2', 'event_successful': 'success'}
        events = events.rename(columns={k:v for k,v in rename.items() if k in events.columns})
        
        save_table(events, 'fact_events')
        log.info(f"  fact_events: {len(events):,} rows")
    
    # 2. fact_events_long - one row per player per event
    if 'fact_events_tracking' in tracking_data:
        log.info("Creating fact_events_long...")
        tracking = tracking_data['fact_events_tracking']
        
        # Build long format
        rows = []
        for _, r in tracking.iterrows():
            player_num = r.get('player_game_number')
            event_id = r.get('event_id')
            if pd.notna(player_num) and pd.notna(event_id):
                rows.append({
                    'event_player_id': f"{event_id}_{player_num}",
                    'event_id': event_id,
                    'game_id': r['game_id'],
                    'event_index': r['event_index'],
                    'player_game_number': player_num,
                    'player_id': r.get('player_id'),
                    'player_role': r.get('player_role') or r.get('role_abrev'),
                    'player_team': r.get('player_team') or r.get('team_venue'),
                    'event_type': r.get('Type'),
                    'period': r.get('period'),
                })
        
        events_long = pd.DataFrame(rows)
        events_long = events_long.drop_duplicates(subset=['event_player_id'])
        
        save_table(events_long, 'fact_events_long')
        log.info(f"  fact_events_long: {len(events_long):,} rows")
        log.info(f"  player_id linked: {events_long['player_id'].notna().sum()}/{len(events_long)}")
    
    # 3. fact_shifts - one row per shift
    if 'fact_shifts_tracking' in tracking_data:
        log.info("Creating fact_shifts...")
        shifts_tracking = tracking_data['fact_shifts_tracking']
        
        shifts = shifts_tracking.drop_duplicates(subset=['shift_id'])
        
        keep_cols = ['shift_id', 'game_id', 'shift_index', 'Period',
                     'shift_start_type', 'shift_stop_type',
                     'shift_start_min', 'shift_start_sec', 'shift_end_min', 'shift_end_sec',
                     'home_team', 'away_team',
                     'home_forward_1', 'home_forward_2', 'home_forward_3',
                     'home_defense_1', 'home_defense_2', 'home_goalie',
                     'away_forward_1', 'away_forward_2', 'away_forward_3',
                     'away_defense_1', 'away_defense_2', 'away_goalie']
        shifts = shifts[[c for c in keep_cols if c in shifts.columns]]
        
        if 'Period' in shifts.columns:
            shifts = shifts.rename(columns={'Period': 'period'})
        
        save_table(shifts, 'fact_shifts')
        log.info(f"  fact_shifts: {len(shifts):,} rows")
    
    # 4. fact_shift_players - one row per player per shift
    if 'fact_shifts_tracking' in tracking_data:
        log.info("Creating fact_shift_players...")
        shifts_tracking = tracking_data['fact_shifts_tracking']
        
        positions = [
            ('home_forward_1', 'home', 'F1'), ('home_forward_2', 'home', 'F2'),
            ('home_forward_3', 'home', 'F3'), ('home_defense_1', 'home', 'D1'),
            ('home_defense_2', 'home', 'D2'), ('home_goalie', 'home', 'G'),
            ('away_forward_1', 'away', 'F1'), ('away_forward_2', 'away', 'F2'),
            ('away_forward_3', 'away', 'F3'), ('away_defense_1', 'away', 'D1'),
            ('away_defense_2', 'away', 'D2'), ('away_goalie', 'away', 'G'),
        ]
        
        rows = []
        for _, shift in shifts_tracking.iterrows():
            for col, venue, pos in positions:
                if col in shift and pd.notna(shift[col]) and str(shift[col]).strip():
                    player_num = str(shift[col]).strip()
                    game_id = shift['game_id']
                    
                    # Get team name for player lookup
                    team_name = shift.get(f'{venue}_team', '')
                    
                    # Look up player_id
                    player_id = None
                    if team_name:
                        key = (game_id, str(team_name).strip(), player_num)
                        player_id = player_lookup.get(key)
                    if not player_id:
                        key = (game_id, player_num)
                        player_id = player_lookup.get(key)
                    
                    rows.append({
                        'shift_player_id': f"{shift['shift_id']}_{venue}_{pos}",
                        'shift_id': shift['shift_id'],
                        'game_id': game_id,
                        'shift_index': shift['shift_index'],
                        'player_game_number': player_num,
                        'player_id': player_id,
                        'venue': venue,
                        'position': pos,
                        'period': shift.get('Period') or shift.get('period'),
                    })
        
        shift_players = pd.DataFrame(rows)
        shift_players = shift_players.drop_duplicates(subset=['shift_player_id'])
        
        save_table(shift_players, 'fact_shift_players')
        log.info(f"  fact_shift_players: {len(shift_players):,} rows")
        log.info(f"  player_id linked: {shift_players['player_id'].notna().sum()}/{len(shift_players)}")

# ============================================================
# PHASE 5: CREATE REFERENCE TABLES
# ============================================================

def create_reference_tables():
    log.section("PHASE 5: CREATE REFERENCE TABLES")
    
    # dim_player_role - 14 roles
    roles = []
    for i in range(1, 7):
        roles.append({
            'role_id': i, 
            'role_code': f'event_player_{i}',
            'role_name': f'Event Player {i}',
            'role_type': 'event_team',
            'sort_order': i
        })
    roles.append({
        'role_id': 7, 
        'role_code': 'event_goalie',
        'role_name': 'Event Team Goalie',
        'role_type': 'event_team',
        'sort_order': 7
    })
    for i in range(1, 7):
        roles.append({
            'role_id': 7 + i,
            'role_code': f'opp_player_{i}',
            'role_name': f'Opponent Player {i}',
            'role_type': 'opp_team',
            'sort_order': 7 + i
        })
    roles.append({
        'role_id': 14,
        'role_code': 'opp_goalie',
        'role_name': 'Opponent Goalie',
        'role_type': 'opp_team',
        'sort_order': 14
    })
    save_table(pd.DataFrame(roles), 'dim_player_role')
    log.info("dim_player_role: 14 rows")
    
    # dim_position
    positions = [
        {'position_id': 1, 'position_code': 'C', 'position_name': 'Center', 'position_type': 'forward'},
        {'position_id': 2, 'position_code': 'LW', 'position_name': 'Left Wing', 'position_type': 'forward'},
        {'position_id': 3, 'position_code': 'RW', 'position_name': 'Right Wing', 'position_type': 'forward'},
        {'position_id': 4, 'position_code': 'F', 'position_name': 'Forward', 'position_type': 'forward'},
        {'position_id': 5, 'position_code': 'D', 'position_name': 'Defense', 'position_type': 'defense'},
        {'position_id': 6, 'position_code': 'G', 'position_name': 'Goalie', 'position_type': 'goalie'},
    ]
    save_table(pd.DataFrame(positions), 'dim_position')
    log.info("dim_position: 6 rows")
    
    # dim_zone
    zones = [
        {'zone_id': 1, 'zone_code': 'O', 'zone_name': 'Offensive Zone', 'zone_abbrev': 'OZ'},
        {'zone_id': 2, 'zone_code': 'D', 'zone_name': 'Defensive Zone', 'zone_abbrev': 'DZ'},
        {'zone_id': 3, 'zone_code': 'N', 'zone_name': 'Neutral Zone', 'zone_abbrev': 'NZ'},
    ]
    save_table(pd.DataFrame(zones), 'dim_zone')
    log.info("dim_zone: 3 rows")
    
    # dim_period
    periods = [
        {'period_id': 1, 'period_number': 1, 'period_name': '1st Period', 'period_type': 'regulation', 'period_minutes': 20},
        {'period_id': 2, 'period_number': 2, 'period_name': '2nd Period', 'period_type': 'regulation', 'period_minutes': 20},
        {'period_id': 3, 'period_number': 3, 'period_name': '3rd Period', 'period_type': 'regulation', 'period_minutes': 20},
        {'period_id': 4, 'period_number': 4, 'period_name': 'Overtime', 'period_type': 'overtime', 'period_minutes': 5},
        {'period_id': 5, 'period_number': 5, 'period_name': 'Shootout', 'period_type': 'shootout', 'period_minutes': 0},
    ]
    save_table(pd.DataFrame(periods), 'dim_period')
    log.info("dim_period: 5 rows")
    
    # dim_venue
    venues = [
        {'venue_id': 1, 'venue_code': 'home', 'venue_name': 'Home', 'venue_abbrev': 'H'},
        {'venue_id': 2, 'venue_code': 'away', 'venue_name': 'Away', 'venue_abbrev': 'A'},
    ]
    save_table(pd.DataFrame(venues), 'dim_venue')
    log.info("dim_venue: 2 rows")

# ============================================================
# PHASE 6: COMPREHENSIVE VALIDATION
# ============================================================

def validate_all():
    log.section("PHASE 6: COMPREHENSIVE VALIDATION")
    
    all_issues = []
    
    # 1. Check all expected tables exist
    log.info("\n[1] Table existence check:")
    expected_tables = [
        'dim_player', 'dim_team', 'dim_league', 'dim_season', 'dim_schedule',
        'dim_player_role', 'dim_position', 'dim_zone', 'dim_period', 'dim_venue',
        'fact_gameroster', 'fact_events', 'fact_events_long', 'fact_events_tracking',
        'fact_shifts', 'fact_shift_players', 'fact_shifts_tracking',
        'fact_playergames', 'fact_draft', 'fact_registration', 'fact_leadership',
    ]
    
    for table in expected_tables:
        path = OUTPUT_DIR / f"{table}.csv"
        if path.exists():
            df = pd.read_csv(path, dtype=str)
            log.info(f"  ✓ {table}: {len(df):,} rows")
        else:
            log.error(f"  ✗ {table}: MISSING")
            all_issues.append(f"Missing table: {table}")
    
    # 2. Check game coverage in tracking tables
    log.info("\n[2] Game coverage (tracking tables):")
    for table in ['fact_events', 'fact_shifts', 'fact_events_long', 'fact_shift_players']:
        path = OUTPUT_DIR / f"{table}.csv"
        if path.exists():
            df = pd.read_csv(path, dtype=str)
            games = sorted(df['game_id'].unique().tolist())
            missing = set(VALID_TRACKING_GAMES) - set(games)
            extra = set(games) - set(VALID_TRACKING_GAMES)
            
            if missing:
                log.error(f"  ✗ {table}: missing games {missing}")
                all_issues.append(f"{table}: missing games {missing}")
            elif extra:
                log.warn(f"  ⚠ {table}: unexpected games {extra}")
            else:
                log.info(f"  ✓ {table}: all 5 games present")
    
    # 3. Primary key integrity
    log.info("\n[3] Primary key integrity:")
    key_checks = [
        ('dim_player', 'player_id'),
        ('dim_team', 'team_id'),
        ('dim_league', 'league_id'),
        ('dim_season', 'season_id'),
        ('dim_schedule', 'game_id'),
        ('fact_gameroster', 'player_game_id'),
        ('fact_events', 'event_id'),
        ('fact_shifts', 'shift_id'),
        ('fact_events_long', 'event_player_id'),
        ('fact_shift_players', 'shift_player_id'),
        ('fact_playergames', 'player_game_id'),
    ]
    
    for table, pk in key_checks:
        path = OUTPUT_DIR / f"{table}.csv"
        if path.exists():
            df = pd.read_csv(path, dtype=str)
            if pk in df.columns:
                nulls = df[pk].isna().sum()
                dups = df.duplicated(subset=[pk]).sum()
                sample = df[pk].dropna().iloc[0] if len(df) > 0 else ""
                
                if nulls > 0 or dups > 0:
                    log.error(f"  ✗ {table}.{pk}: {nulls} NULL, {dups} dups")
                    all_issues.append(f"{table}.{pk}: {nulls} NULL, {dups} dups")
                else:
                    log.info(f"  ✓ {table}.{pk}: {sample[:40]}")
            else:
                log.error(f"  ✗ {table}: missing column {pk}")
                all_issues.append(f"{table}: missing column {pk}")
    
    # 4. Player ID linkage
    log.info("\n[4] Player ID linkage:")
    player_tables = ['fact_events_long', 'fact_shift_players', 'fact_gameroster']
    
    for table in player_tables:
        path = OUTPUT_DIR / f"{table}.csv"
        if path.exists():
            df = pd.read_csv(path, dtype=str)
            if 'player_id' in df.columns:
                linked = df['player_id'].notna().sum()
                total = len(df)
                pct = linked / total * 100 if total > 0 else 0
                
                if pct < 90:
                    log.warn(f"  ⚠ {table}: {linked:,}/{total:,} ({pct:.1f}%) - LOW")
                    log.issue(f"{table} has only {pct:.1f}% player_id linkage")
                else:
                    log.info(f"  ✓ {table}: {linked:,}/{total:,} ({pct:.1f}%)")
            else:
                log.error(f"  ✗ {table}: missing player_id column")
                all_issues.append(f"{table}: missing player_id column")
    
    # 5. No underscore columns
    log.info("\n[5] No underscore columns check:")
    for csv in OUTPUT_DIR.glob("*.csv"):
        df = pd.read_csv(csv, dtype=str, nrows=0)
        underscore_cols = [c for c in df.columns if c.endswith('_')]
        if underscore_cols:
            log.error(f"  ✗ {csv.stem}: has underscore cols {underscore_cols[:3]}")
            all_issues.append(f"{csv.stem}: has underscore columns")
        else:
            log.info(f"  ✓ {csv.stem}: clean")
    
    # 6. Referential integrity
    log.info("\n[6] Referential integrity:")
    
    # Check game_id in events exists in schedule
    schedule = pd.read_csv(OUTPUT_DIR / "dim_schedule.csv", dtype=str)
    schedule_games = set(schedule['game_id'].unique())
    
    events = pd.read_csv(OUTPUT_DIR / "fact_events.csv", dtype=str)
    event_games = set(events['game_id'].unique())
    
    missing_in_schedule = event_games - schedule_games
    if missing_in_schedule:
        log.error(f"  ✗ Events have games not in schedule: {missing_in_schedule}")
        all_issues.append(f"Games in events but not schedule: {missing_in_schedule}")
    else:
        log.info(f"  ✓ All event games exist in schedule")
    
    # Summary
    log.section("VALIDATION SUMMARY")
    
    total_rows = sum(len(pd.read_csv(f, dtype=str)) for f in OUTPUT_DIR.glob("*.csv"))
    table_count = len(list(OUTPUT_DIR.glob("*.csv")))
    
    log.info(f"Tables: {table_count}")
    log.info(f"Total rows: {total_rows:,}")
    log.info(f"Warnings: {len(log.warnings)}")
    log.info(f"Errors: {len(log.errors)}")
    log.info(f"Issues for review: {len(log.issues)}")
    
    if all_issues:
        log.error(f"\nCRITICAL ISSUES ({len(all_issues)}):")
        for issue in all_issues:
            log.error(f"  - {issue}")
        return False
    
    log.info("\n✓ ALL VALIDATIONS PASSED")
    return True

# ============================================================
# MAIN
# ============================================================

def main():
    print("="*60)
    print("BENCHSIGHT v5.0.0 - PRODUCTION ETL")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*60)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(exist_ok=True)
    
    # Phase 1: Load BLB tables
    loaded = load_blb_tables()
    
    # Phase 2: Build player lookup
    player_lookup = build_player_lookup(loaded['fact_gameroster'])
    
    # Phase 3: Load tracking data
    tracking_data = load_tracking_data(player_lookup)
    
    # Phase 4: Create derived tables
    create_derived_tables(tracking_data, player_lookup)
    
    # Phase 5: Create reference tables
    create_reference_tables()
    
    # Phase 6: Validate
    valid = validate_all()
    
    # Save log
    log.save(LOG_FILE)
    
    print("\n" + "="*60)
    if valid:
        print("✓ ETL COMPLETE - ALL VALIDATIONS PASSED")
    else:
        print("✗ ETL COMPLETE - WITH ISSUES (see log)")
    print("="*60)
    
    # Print issues for user
    if log.issues:
        print("\n=== ISSUES FOR USER REVIEW ===")
        for issue in log.issues:
            print(f"  ⚠ {issue}")
    
    return 0 if valid else 1

if __name__ == "__main__":
    exit(main())
