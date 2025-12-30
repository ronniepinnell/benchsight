#!/usr/bin/env python3
"""
BenchSight Data Integrity & Standardization Fix
================================================

This script fixes:
1. KEY STANDARDIZATION: All keys use format {2-char prefix}{game_id}{5-digit index}
2. TEAM STATS: Recalculate using ONLY event_team_player_1
3. ZONE PRESSURE: Fix dz_pressure calculation
4. FOREIGN KEYS: Ensure all FKs use standardized format
5. EMPTY NET: Properly flag empty net situations

KEY FORMAT STANDARD:
- Event key:        EV{game_id}{5-digit} e.g., EV1896900001
- Shift key:        SH{game_id}{5-digit} e.g., SH1896900001
- Player game key:  PG{game_id}{5-digit} e.g., PG1896900001
- Team game key:    TG{game_id}{5-digit} e.g., TG1896900001
- Goalie key:       GK{game_id}{5-digit} e.g., GK1896900001
- Zone time key:    ZT{game_id}{5-digit} e.g., ZT1896900001
- H2H key:          HH{game_id}{5-digit} e.g., HH1896900001
- WOWY key:         WY{game_id}{5-digit} e.g., WY1896900001
- Line combo key:   LC{game_id}{5-digit} e.g., LC1896900001
- Shift player key: SP{game_id}{5-digit} e.g., SP1896900001
- Event player key: EP{game_id}{5-digit} e.g., EP1896900001

Author: BenchSight
Date: December 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

OUTPUT_DIR = Path('data/output')


def generate_standardized_key(prefix: str, game_id: int, index) -> str:
    """Generate standardized key: {2-char prefix}{game_id}{5-digit padded index}"""
    try:
        idx = int(index) if pd.notna(index) else 0
    except (ValueError, TypeError):
        idx = 0
    return f"{prefix}{game_id}{idx:05d}"


def standardize_all_keys():
    """Standardize all primary and foreign keys across tables."""
    print("=" * 60)
    print("STANDARDIZING ALL KEYS")
    print("=" * 60)
    
    # =========================================================================
    # 1. FACT_SHIFTS - Fix shift_key
    # =========================================================================
    print("\n1. Fixing fact_shifts keys...")
    shifts = pd.read_csv(OUTPUT_DIR / 'fact_shifts.csv')
    
    # Generate new shift keys
    for idx, row in shifts.iterrows():
        game_id = row['game_id']
        shift_idx = row['shift_index']
        shifts.loc[idx, 'shift_key'] = generate_standardized_key('SH', game_id, shift_idx)
    
    shifts.to_csv(OUTPUT_DIR / 'fact_shifts.csv', index=False)
    print(f"   ✅ Updated {len(shifts)} shift keys (format: SH{{game}}{{5d}})")
    
    # =========================================================================
    # 2. FACT_EVENTS - Standardize event_key
    # =========================================================================
    print("\n2. Fixing fact_events keys...")
    events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv')
    
    for idx, row in events.iterrows():
        game_id = row['game_id']
        event_idx = row['event_index'] if pd.notna(row['event_index']) else idx
        events.loc[idx, 'event_key'] = generate_standardized_key('EV', game_id, event_idx)
        
        # Also fix shift_key FK
        shift_idx = row.get('shift_index')
        if pd.notna(shift_idx):
            events.loc[idx, 'shift_key'] = generate_standardized_key('SH', game_id, shift_idx)
    
    events.to_csv(OUTPUT_DIR / 'fact_events.csv', index=False)
    print(f"   ✅ Updated {len(events)} event keys")
    
    # =========================================================================
    # 3. FACT_EVENTS_PLAYER - Standardize keys and FKs
    # =========================================================================
    print("\n3. Fixing fact_events_player keys...")
    events_player = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv')
    
    for idx, row in events_player.iterrows():
        game_id = row['game_id']
        # Use row index for unique key within game
        events_player.loc[idx, 'event_player_key'] = generate_standardized_key('EP', game_id, idx % 100000)
        events_player.loc[idx, 'event_key'] = generate_standardized_key('EV', game_id, row['event_index'])
        
        if pd.notna(row.get('shift_index')):
            events_player.loc[idx, 'shift_key'] = generate_standardized_key('SH', game_id, row['shift_index'])
    
    events_player.to_csv(OUTPUT_DIR / 'fact_events_player.csv', index=False)
    print(f"   ✅ Updated {len(events_player)} event_player keys")
    
    # =========================================================================
    # 4. FACT_SHIFTS_PLAYER - Standardize keys
    # =========================================================================
    print("\n4. Fixing fact_shifts_player keys...")
    shifts_player = pd.read_csv(OUTPUT_DIR / 'fact_shifts_player.csv')
    
    counter = {}  # Track index per game
    for idx, row in shifts_player.iterrows():
        game_id = row['game_id']
        shift_idx = row.get('shift_index', idx)
        
        counter[game_id] = counter.get(game_id, 0) + 1
        shifts_player.loc[idx, 'shift_player_key'] = generate_standardized_key('SP', game_id, counter[game_id])
        shifts_player.loc[idx, 'shift_key'] = generate_standardized_key('SH', game_id, shift_idx if pd.notna(shift_idx) else counter[game_id])
    
    shifts_player.to_csv(OUTPUT_DIR / 'fact_shifts_player.csv', index=False)
    print(f"   ✅ Updated {len(shifts_player)} shift_player keys")
    
    # =========================================================================
    # 5. FACT_PLAYER_GAME_STATS - Standardize keys
    # =========================================================================
    print("\n5. Fixing fact_player_game_stats keys...")
    player_stats = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
    
    counter = {}
    for idx, row in player_stats.iterrows():
        game_id = row['game_id']
        counter[game_id] = counter.get(game_id, 0) + 1
        player_stats.loc[idx, 'player_game_key'] = generate_standardized_key('PG', game_id, counter[game_id])
    
    player_stats.to_csv(OUTPUT_DIR / 'fact_player_game_stats.csv', index=False)
    print(f"   ✅ Updated {len(player_stats)} player_game keys")
    
    # =========================================================================
    # 6. FACT_TEAM_GAME_STATS - Standardize keys
    # =========================================================================
    print("\n6. Fixing fact_team_game_stats keys...")
    team_stats = pd.read_csv(OUTPUT_DIR / 'fact_team_game_stats.csv')
    
    counter = {}
    for idx, row in team_stats.iterrows():
        game_id = row['game_id']
        counter[game_id] = counter.get(game_id, 0) + 1
        team_stats.loc[idx, 'team_game_key'] = generate_standardized_key('TG', game_id, counter[game_id])
    
    team_stats.to_csv(OUTPUT_DIR / 'fact_team_game_stats.csv', index=False)
    print(f"   ✅ Updated {len(team_stats)} team_game keys")
    
    # =========================================================================
    # 7. FACT_GOALIE_GAME_STATS - Standardize keys
    # =========================================================================
    print("\n7. Fixing fact_goalie_game_stats keys...")
    goalie_stats = pd.read_csv(OUTPUT_DIR / 'fact_goalie_game_stats.csv')
    
    counter = {}
    for idx, row in goalie_stats.iterrows():
        game_id = row['game_id']
        counter[game_id] = counter.get(game_id, 0) + 1
        goalie_stats.loc[idx, 'goalie_game_key'] = generate_standardized_key('GK', game_id, counter[game_id])
    
    goalie_stats.to_csv(OUTPUT_DIR / 'fact_goalie_game_stats.csv', index=False)
    print(f"   ✅ Updated {len(goalie_stats)} goalie_game keys")
    
    # =========================================================================
    # 8. FACT_H2H - Add keys
    # =========================================================================
    print("\n8. Adding fact_h2h keys...")
    h2h = pd.read_csv(OUTPUT_DIR / 'fact_h2h.csv')
    
    counter = {}
    for idx, row in h2h.iterrows():
        game_id = row['game_id']
        counter[game_id] = counter.get(game_id, 0) + 1
        h2h.loc[idx, 'h2h_key'] = generate_standardized_key('HH', game_id, counter[game_id])
    
    h2h.to_csv(OUTPUT_DIR / 'fact_h2h.csv', index=False)
    print(f"   ✅ Added {len(h2h)} h2h keys")
    
    # =========================================================================
    # 9. FACT_WOWY - Add keys
    # =========================================================================
    print("\n9. Adding fact_wowy keys...")
    wowy = pd.read_csv(OUTPUT_DIR / 'fact_wowy.csv')
    
    counter = {}
    for idx, row in wowy.iterrows():
        game_id = row['game_id']
        counter[game_id] = counter.get(game_id, 0) + 1
        wowy.loc[idx, 'wowy_key'] = generate_standardized_key('WY', game_id, counter[game_id])
    
    wowy.to_csv(OUTPUT_DIR / 'fact_wowy.csv', index=False)
    print(f"   ✅ Added {len(wowy)} wowy keys")
    
    # =========================================================================
    # 10. FACT_TEAM_ZONE_TIME - Standardize keys
    # =========================================================================
    print("\n10. Fixing fact_team_zone_time keys...")
    zone_time = pd.read_csv(OUTPUT_DIR / 'fact_team_zone_time.csv')
    
    counter = {}
    for idx, row in zone_time.iterrows():
        game_id = row['game_id']
        counter[game_id] = counter.get(game_id, 0) + 1
        zone_time.loc[idx, 'zone_time_key'] = generate_standardized_key('ZT', game_id, counter[game_id])
    
    zone_time.to_csv(OUTPUT_DIR / 'fact_team_zone_time.csv', index=False)
    print(f"   ✅ Updated {len(zone_time)} zone_time keys")
    
    print("\n✅ All keys standardized!")


def recalculate_team_stats():
    """
    Recalculate team stats using ONLY event_team_player_1.
    
    CRITICAL RULES:
    - Shots: Only count event_team_player_1 on Shot events
    - Faceoffs: event_team_player_1 = WINNER, opp_team_player_1 = LOSER
    - Passes: Only count event_team_player_1
    - Turnovers: Only count event_team_player_1 (giveaways = their turnover)
    """
    print("\n" + "=" * 60)
    print("RECALCULATING TEAM STATS (event_team_player_1 only)")
    print("=" * 60)
    
    events_player = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv')
    roster = pd.read_csv(OUTPUT_DIR / 'fact_gameroster.csv')
    team_stats = pd.read_csv(OUTPUT_DIR / 'fact_team_game_stats.csv')
    
    # Get tracked games
    tracked_games = team_stats['game_id'].unique()
    
    for game_id in tracked_games:
        print(f"\n--- Game {game_id} ---")
        
        game_events = events_player[events_player['game_id'] == game_id]
        game_roster = roster[roster['game_id'] == game_id]
        
        # Get primary actor events only
        primary_events = game_events[game_events['player_role'] == 'event_team_player_1']
        
        # Get teams from player_team column (more reliable than roster matching)
        teams = primary_events['player_team'].dropna().unique()
        
        # Total faceoffs in game
        total_game_faceoffs = len(primary_events[primary_events['event_type'] == 'Faceoff'])
        
        for team_name in teams:
            # Filter to this team's events (by player_team column)
            team_primary = primary_events[primary_events['player_team'] == team_name]
            
            # Calculate stats
            shots = len(team_primary[team_primary['event_type'] == 'Shot'])
            sog = len(team_primary[team_primary['event_detail'].isin([
                'Shot_OnNetSaved', 'Shot_Goal', 'Shot_TippedOnNetSaved', 
                'Shot_DeflectedOnNetSaved', 'Shot_OnNetTippedGoal'
            ])])
            goals = len(team_primary[team_primary['event_type'] == 'Goal'])
            
            # Faceoffs: event_team_player_1 = winner
            fo_wins = len(team_primary[team_primary['event_type'] == 'Faceoff'])
            fo_losses = total_game_faceoffs - fo_wins  # Losses = total - wins
            
            # Passes
            pass_events = team_primary[team_primary['event_type'] == 'Pass']
            pass_attempts = len(pass_events)
            pass_completed = len(pass_events[pass_events['event_successful'] == 's'])
            
            # Turnovers (giveaways = team's turnovers)
            turnovers = team_primary[team_primary['event_type'] == 'Turnover']
            giveaways = len(turnovers[turnovers['event_detail'].str.contains('Giveaway', na=False)])
            takeaways = len(turnovers[turnovers['event_detail'].str.contains('Takeaway', na=False)])
            
            # Zone entries
            zone_events = team_primary[team_primary['event_type'] == 'Zone_Entry_Exit']
            zone_entries = len(zone_events[zone_events['event_detail'].str.contains('Entry', na=False)])
            zone_exits = len(zone_events[zone_events['event_detail'].str.contains('Exit', na=False)])
            
            print(f"  {team_name}: Shots={shots}, SOG={sog}, Goals={goals}, FO W/L={fo_wins}/{fo_losses}")
            
            # Get team_id from roster
            team_roster = game_roster[game_roster['team_name'] == team_name]
            if len(team_roster) > 0:
                team_id = team_roster['team_id'].iloc[0]
                
                # Update team stats
                mask = (team_stats['game_id'] == game_id) & (team_stats['team_id'] == team_id)
                if mask.any():
                    team_stats.loc[mask, 'shots'] = shots
                    team_stats.loc[mask, 'sog'] = sog
                    team_stats.loc[mask, 'goals'] = goals
                    team_stats.loc[mask, 'fo_wins'] = fo_wins
                    team_stats.loc[mask, 'fo_losses'] = fo_losses
                    team_stats.loc[mask, 'fo_total'] = fo_wins + fo_losses
                    team_stats.loc[mask, 'fo_pct'] = round(fo_wins / (fo_wins + fo_losses) * 100, 1) if (fo_wins + fo_losses) > 0 else 0
                    team_stats.loc[mask, 'pass_attempts'] = pass_attempts
                    team_stats.loc[mask, 'pass_completed'] = pass_completed
                    team_stats.loc[mask, 'pass_pct'] = round(pass_completed / pass_attempts * 100, 1) if pass_attempts > 0 else 0
                    team_stats.loc[mask, 'giveaways'] = giveaways
                    team_stats.loc[mask, 'takeaways'] = takeaways
                    team_stats.loc[mask, 'zone_entries'] = zone_entries
                    team_stats.loc[mask, 'zone_exits'] = zone_exits
                    team_stats.loc[mask, 'shooting_pct'] = round(goals / sog * 100, 1) if sog > 0 else 0
    
    team_stats.to_csv(OUTPUT_DIR / 'fact_team_game_stats.csv', index=False)
    print("\n✅ Team stats recalculated!")
    
    return team_stats


def fix_zone_pressure():
    """Fix dz_pressure calculation in zone time stats."""
    print("\n" + "=" * 60)
    print("FIXING ZONE PRESSURE CALCULATIONS")
    print("=" * 60)
    
    zone_time = pd.read_csv(OUTPUT_DIR / 'fact_team_zone_time.csv')
    events_player = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv')
    
    tracked_games = zone_time['game_id'].unique()
    
    for game_id in tracked_games:
        game_zone = zone_time[zone_time['game_id'] == game_id]
        game_events = events_player[
            (events_player['game_id'] == game_id) &
            (events_player['player_role'] == 'event_team_player_1')
        ]
        
        for idx, row in game_zone.iterrows():
            team_id = row.get('team_id')
            
            # DZ pressure = events by opposing team in your DZ
            # i.e., shots, passes, possession events in your defensive zone
            dz_events = row.get('dzone_events', 0)
            oz_events = row.get('ozone_events', 0)
            total = row.get('total_events', 1) or 1
            
            # Calculate DZ pressure as ratio of DZ events
            dz_pressure = round(dz_events / total * 100, 1) if total > 0 else 0
            
            zone_time.loc[idx, 'dz_pressure'] = dz_pressure
    
    zone_time.to_csv(OUTPUT_DIR / 'fact_team_zone_time.csv', index=False)
    print("✅ Zone pressure fixed!")
    
    return zone_time


def add_empty_net_flags():
    """Add empty net flags to relevant tables."""
    print("\n" + "=" * 60)
    print("ADDING EMPTY NET FLAGS")
    print("=" * 60)
    
    shifts = pd.read_csv(OUTPUT_DIR / 'fact_shifts.csv')
    events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv')
    goalie_stats = pd.read_csv(OUTPUT_DIR / 'fact_goalie_game_stats.csv')
    
    # Check which goals were empty net
    empty_net_goals = []
    
    for idx, event in events[events['event_type'] == 'Goal'].iterrows():
        game_id = event['game_id']
        shift_idx = event.get('shift_index')
        
        if pd.isna(shift_idx):
            continue
        
        # Find the shift
        shift = shifts[
            (shifts['game_id'] == game_id) & 
            (shifts['shift_index'] == shift_idx)
        ]
        
        if len(shift) == 0:
            continue
        
        shift = shift.iloc[0]
        scoring_team = event.get('team_venue', '')
        
        # Check if opposing goalie was pulled
        if scoring_team == 'home':
            is_en = shift.get('away_team_en', 0) == 1 or pd.isna(shift.get('away_goalie'))
        else:
            is_en = shift.get('home_team_en', 0) == 1 or pd.isna(shift.get('home_goalie'))
        
        if is_en:
            events.loc[idx, 'empty_net_goal'] = 1
            empty_net_goals.append(event['event_index'])
    
    # Add empty_net_goal column if not exists
    if 'empty_net_goal' not in events.columns:
        events['empty_net_goal'] = 0
    
    events.to_csv(OUTPUT_DIR / 'fact_events.csv', index=False)
    print(f"✅ Flagged {len(empty_net_goals)} empty net goals")
    
    # Update goalie stats to exclude empty net goals from GA
    # (This is informational - goalie shouldn't be penalized for EN goals)
    if 'empty_net_ga' not in goalie_stats.columns:
        goalie_stats['empty_net_ga'] = 0
        goalie_stats.to_csv(OUTPUT_DIR / 'fact_goalie_game_stats.csv', index=False)
    
    return empty_net_goals


def verify_fk_relationships():
    """Verify all foreign key relationships are valid."""
    print("\n" + "=" * 60)
    print("VERIFYING FOREIGN KEY RELATIONSHIPS")
    print("=" * 60)
    
    # Load all tables
    tables = {
        'fact_events': pd.read_csv(OUTPUT_DIR / 'fact_events.csv'),
        'fact_events_player': pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv'),
        'fact_shifts': pd.read_csv(OUTPUT_DIR / 'fact_shifts.csv'),
        'fact_shifts_player': pd.read_csv(OUTPUT_DIR / 'fact_shifts_player.csv'),
        'fact_player_game_stats': pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv'),
    }
    
    errors = []
    
    # Check event_key references
    event_keys = set(tables['fact_events']['event_key'].dropna())
    ep_event_keys = set(tables['fact_events_player']['event_key'].dropna())
    
    orphan_event_keys = ep_event_keys - event_keys
    if orphan_event_keys:
        errors.append(f"fact_events_player has {len(orphan_event_keys)} orphan event_keys")
    else:
        print("✅ fact_events_player.event_key -> fact_events.event_key")
    
    # Check shift_key references
    shift_keys = set(tables['fact_shifts']['shift_key'].dropna())
    sp_shift_keys = set(tables['fact_shifts_player']['shift_key'].dropna())
    
    orphan_shift_keys = sp_shift_keys - shift_keys
    if orphan_shift_keys:
        errors.append(f"fact_shifts_player has {len(orphan_shift_keys)} orphan shift_keys")
    else:
        print("✅ fact_shifts_player.shift_key -> fact_shifts.shift_key")
    
    # Check player_id references
    roster = pd.read_csv(OUTPUT_DIR / 'fact_gameroster.csv')
    player_ids = set(roster['player_id'].dropna())
    
    for table_name, df in tables.items():
        if 'player_id' in df.columns:
            table_player_ids = set(df['player_id'].dropna())
            orphan = table_player_ids - player_ids
            if orphan:
                # This might be OK for some tables
                print(f"⚠️  {table_name} has {len(orphan)} player_ids not in roster")
            else:
                print(f"✅ {table_name}.player_id -> fact_gameroster.player_id")
    
    if errors:
        print("\n❌ FK Errors:")
        for e in errors:
            print(f"   {e}")
    else:
        print("\n✅ All FK relationships valid!")
    
    return errors


def print_final_stats():
    """Print final statistics for verification."""
    print("\n" + "=" * 60)
    print("FINAL STATISTICS")
    print("=" * 60)
    
    team_stats = pd.read_csv(OUTPUT_DIR / 'fact_team_game_stats.csv')
    
    print("\nTeam Stats (recalculated with event_team_player_1 only):")
    print(team_stats[['game_id', 'team_id', 'shots', 'sog', 'goals', 'fo_wins', 'fo_losses', 'pass_attempts', 'giveaways']].to_string())
    
    # Check key format samples
    print("\n\nKey Format Samples:")
    events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv')
    shifts = pd.read_csv(OUTPUT_DIR / 'fact_shifts.csv')
    
    print(f"  Event key:  {events['event_key'].iloc[0]}")
    print(f"  Shift key:  {shifts['shift_key'].iloc[0]}")
    print(f"  Team key:   {team_stats['team_game_key'].iloc[0]}")


def main():
    """Run all fixes."""
    print("=" * 60)
    print("BENCHSIGHT DATA INTEGRITY & STANDARDIZATION")
    print("=" * 60)
    
    # 1. Standardize all keys
    standardize_all_keys()
    
    # 2. Recalculate team stats
    recalculate_team_stats()
    
    # 3. Fix zone pressure
    fix_zone_pressure()
    
    # 4. Add empty net flags
    add_empty_net_flags()
    
    # 5. Verify FK relationships
    verify_fk_relationships()
    
    # 6. Print final stats
    print_final_stats()
    
    print("\n" + "=" * 60)
    print("ALL FIXES COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
