#!/usr/bin/env python3
"""
BenchSight Final Data Fixes
===========================

This script fixes:
1. Add team_name wherever team_id exists
2. Add player_name wherever player_id exists
3. Fix fact_events_tracking keys
4. Add goalie microstats
5. Verify and fix team game stats

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
    """Generate standardized key."""
    try:
        idx = int(index) if pd.notna(index) else 0
    except (ValueError, TypeError):
        idx = 0
    return f"{prefix}{game_id}{idx:05d}"


def get_name_lookups():
    """Create lookups for team and player names."""
    roster = pd.read_csv(OUTPUT_DIR / 'fact_gameroster.csv')
    
    # Team name lookup
    team_lookup = roster.drop_duplicates(subset=['team_id'])[['team_id', 'team_name']].set_index('team_id')['team_name'].to_dict()
    
    # Player name lookup
    player_lookup = roster.drop_duplicates(subset=['player_id'])[['player_id', 'player_full_name']].set_index('player_id')['player_full_name'].to_dict()
    
    return team_lookup, player_lookup


def add_names_to_tables():
    """Add team_name and player_name to all tables that have IDs."""
    print("=" * 60)
    print("ADDING team_name AND player_name TO ALL TABLES")
    print("=" * 60)
    
    team_lookup, player_lookup = get_name_lookups()
    
    tables_to_fix = [
        'fact_shifts_player',
        'fact_team_game_stats',
        'fact_team_zone_time',
        'fact_line_combos',
        'fact_player_game_position',
        'fact_h2h',
        'fact_wowy',
    ]
    
    for table_name in tables_to_fix:
        try:
            df = pd.read_csv(OUTPUT_DIR / f'{table_name}.csv')
            modified = False
            
            # Add team_name if team_id exists
            if 'team_id' in df.columns and 'team_name' not in df.columns:
                df['team_name'] = df['team_id'].map(team_lookup)
                modified = True
                print(f"  ✅ Added team_name to {table_name}")
            
            # Add player_name if player_id exists
            if 'player_id' in df.columns and 'player_name' not in df.columns:
                df['player_name'] = df['player_id'].map(player_lookup)
                modified = True
                print(f"  ✅ Added player_name to {table_name}")
            
            # Handle player_1_id and player_2_id for H2H/WOWY
            if 'player_1_id' in df.columns and 'player_1_name' not in df.columns:
                df['player_1_name'] = df['player_1_id'].map(player_lookup)
                modified = True
            if 'player_2_id' in df.columns and 'player_2_name' not in df.columns:
                df['player_2_name'] = df['player_2_id'].map(player_lookup)
                modified = True
            
            if modified:
                df.to_csv(OUTPUT_DIR / f'{table_name}.csv', index=False)
        
        except Exception as e:
            print(f"  ❌ Error with {table_name}: {e}")
    
    print("\n✅ Names added to all tables!")


def fix_events_tracking_keys():
    """Fix fact_events_tracking to have standardized keys."""
    print("\n" + "=" * 60)
    print("FIXING ALL TRACKING AND REMAINING KEYS")
    print("=" * 60)
    
    # 1. fact_events_tracking
    et = pd.read_csv(OUTPUT_DIR / 'fact_events_tracking.csv')
    
    for idx, row in et.iterrows():
        game_id = row['game_id']
        event_idx = row.get('event_index', idx)
        et.loc[idx, 'event_tracking_key'] = generate_standardized_key('ET', game_id, event_idx)
        et.loc[idx, 'event_key'] = generate_standardized_key('EV', game_id, event_idx)
    
    cols = ['event_tracking_key', 'event_key'] + [c for c in et.columns if c not in ['event_tracking_key', 'event_key']]
    et = et[cols]
    et.to_csv(OUTPUT_DIR / 'fact_events_tracking.csv', index=False)
    print(f"  ✅ Fixed fact_events_tracking: {len(et)} rows")
    
    # 2. fact_shifts_tracking
    try:
        st = pd.read_csv(OUTPUT_DIR / 'fact_shifts_tracking.csv')
        for idx, row in st.iterrows():
            game_id = row['game_id']
            shift_idx = row.get('shift_index', idx)
            st.loc[idx, 'shift_tracking_key'] = generate_standardized_key('ST', game_id, shift_idx)
            st.loc[idx, 'shift_key'] = generate_standardized_key('SH', game_id, shift_idx)
        
        cols = ['shift_tracking_key', 'shift_key'] + [c for c in st.columns if c not in ['shift_tracking_key', 'shift_key']]
        st = st[cols]
        st.to_csv(OUTPUT_DIR / 'fact_shifts_tracking.csv', index=False)
        print(f"  ✅ Fixed fact_shifts_tracking: {len(st)} rows")
    except Exception as e:
        print(f"  ⚠️ fact_shifts_tracking: {e}")
    
    # 3. fact_line_combos
    try:
        lc = pd.read_csv(OUTPUT_DIR / 'fact_line_combos.csv')
        counter = {}
        for idx, row in lc.iterrows():
            game_id = row['game_id']
            counter[game_id] = counter.get(game_id, 0) + 1
            lc.loc[idx, 'line_combo_key'] = generate_standardized_key('LC', game_id, counter[game_id])
        
        cols = ['line_combo_key'] + [c for c in lc.columns if c != 'line_combo_key']
        lc = lc[cols]
        lc.to_csv(OUTPUT_DIR / 'fact_line_combos.csv', index=False)
        print(f"  ✅ Fixed fact_line_combos: {len(lc)} rows")
    except Exception as e:
        print(f"  ⚠️ fact_line_combos: {e}")
    
    # 4. fact_player_game_position
    try:
        pgp = pd.read_csv(OUTPUT_DIR / 'fact_player_game_position.csv')
        counter = {}
        for idx, row in pgp.iterrows():
            game_id = row['game_id']
            counter[game_id] = counter.get(game_id, 0) + 1
            pgp.loc[idx, 'player_position_key'] = generate_standardized_key('PP', game_id, counter[game_id])
        
        cols = ['player_position_key'] + [c for c in pgp.columns if c != 'player_position_key']
        pgp = pgp[cols]
        pgp.to_csv(OUTPUT_DIR / 'fact_player_game_position.csv', index=False)
        print(f"  ✅ Fixed fact_player_game_position: {len(pgp)} rows")
    except Exception as e:
        print(f"  ⚠️ fact_player_game_position: {e}")


def create_goalie_microstats():
    """Create detailed goalie microstats from event data."""
    print("\n" + "=" * 60)
    print("CREATING GOALIE MICROSTATS")
    print("=" * 60)
    
    events_player = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv')
    roster = pd.read_csv(OUTPUT_DIR / 'fact_gameroster.csv')
    goalie_stats = pd.read_csv(OUTPUT_DIR / 'fact_goalie_game_stats.csv')
    
    # Get goalie player_ids
    goalies = roster[roster['player_position'] == 'Goalie'][['game_id', 'player_id', 'player_full_name', 'team_name']]
    
    tracked_games = goalie_stats['game_id'].unique()
    
    for game_id in tracked_games:
        game_events = events_player[events_player['game_id'] == game_id]
        game_goalies = goalies[goalies['game_id'] == game_id]
        
        for _, goalie in game_goalies.iterrows():
            player_id = goalie['player_id']
            team_name = goalie['team_name']
            
            # Goalie saves = Save events where the OPPOSING team shot
            # (i.e., Save events where player_team is the goalie's team)
            save_events = game_events[
                (game_events['event_type'] == 'Save') &
                (game_events['player_team'] == team_name)
            ]
            
            total_saves = len(save_events)
            
            # Save types
            saves_rebound = len(save_events[save_events['event_detail'].str.contains('Rebound', na=False)])
            saves_freeze = len(save_events[save_events['event_detail'].str.contains('Freeze', na=False)])
            
            # Save locations (from event_detail_2)
            saves_glove = len(save_events[save_events['event_detail_2'].str.contains('Glove', na=False)])
            saves_blocker = len(save_events[save_events['event_detail_2'].str.contains('Blocker', na=False)])
            saves_left_pad = len(save_events[save_events['event_detail_2'].str.contains('LeftPad', na=False)])
            saves_right_pad = len(save_events[save_events['event_detail_2'].str.contains('RightPad', na=False)])
            
            # Rebound control rate
            rebound_control_pct = round((saves_freeze / total_saves * 100), 1) if total_saves > 0 else 0
            
            # Update goalie stats - but keep original saves count as it may be more accurate
            mask = (goalie_stats['game_id'] == game_id) & (goalie_stats['player_id'] == player_id)
            if mask.any():
                # Only add microstats, don't overwrite original saves count
                goalie_stats.loc[mask, 'saves_rebound'] = saves_rebound
                goalie_stats.loc[mask, 'saves_freeze'] = saves_freeze
                goalie_stats.loc[mask, 'saves_glove'] = saves_glove
                goalie_stats.loc[mask, 'saves_blocker'] = saves_blocker
                goalie_stats.loc[mask, 'saves_left_pad'] = saves_left_pad
                goalie_stats.loc[mask, 'saves_right_pad'] = saves_right_pad
                goalie_stats.loc[mask, 'rebound_control_pct'] = rebound_control_pct
                goalie_stats.loc[mask, 'total_save_events'] = total_saves  # For reference
                
                original_saves = goalie_stats.loc[mask, 'saves'].iloc[0]
                print(f"  Game {game_id} - {goalie['player_full_name']}: Original={original_saves}, Events={total_saves} (Freeze: {saves_freeze}, Rebound: {saves_rebound})")
    
    goalie_stats.to_csv(OUTPUT_DIR / 'fact_goalie_game_stats.csv', index=False)
    print("\n✅ Goalie microstats added!")
    
    return goalie_stats


def verify_team_stats():
    """Verify and fix team game stats."""
    print("\n" + "=" * 60)
    print("VERIFYING TEAM GAME STATS")
    print("=" * 60)
    
    team_stats = pd.read_csv(OUTPUT_DIR / 'fact_team_game_stats.csv')
    events_player = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv')
    
    team_lookup, _ = get_name_lookups()
    
    # Add team_name if missing
    if 'team_name' not in team_stats.columns:
        team_stats['team_name'] = team_stats['team_id'].map(team_lookup)
    
    tracked_games = team_stats['game_id'].unique()
    
    print("\nVerifying stats by recounting from events (event_team_player_1 only):")
    
    for game_id in tracked_games:
        game_events = events_player[events_player['game_id'] == game_id]
        primary = game_events[game_events['player_role'] == 'event_team_player_1']
        total_faceoffs = len(primary[primary['event_type'] == 'Faceoff'])
        
        teams = primary['player_team'].dropna().unique()
        
        print(f"\n--- Game {game_id} ---")
        
        for team_name in teams:
            team_events = primary[primary['player_team'] == team_name]
            
            # Recalculate
            shots = len(team_events[team_events['event_type'] == 'Shot'])
            sog = len(team_events[team_events['event_detail'].isin([
                'Shot_OnNetSaved', 'Shot_Goal', 'Shot_TippedOnNetSaved',
                'Shot_DeflectedOnNetSaved', 'Shot_OnNetTippedGoal'
            ])])
            goals = len(team_events[team_events['event_type'] == 'Goal'])
            fo_wins = len(team_events[team_events['event_type'] == 'Faceoff'])
            fo_losses = total_faceoffs - fo_wins
            
            passes = team_events[team_events['event_type'] == 'Pass']
            pass_attempts = len(passes)
            pass_completed = len(passes[passes['event_successful'] == 's'])
            
            turnovers = team_events[team_events['event_type'] == 'Turnover']
            giveaways = len(turnovers[turnovers['event_detail'].str.contains('Giveaway', na=False)])
            takeaways = len(turnovers[turnovers['event_detail'].str.contains('Takeaway', na=False)])
            
            print(f"  {team_name}: Shots={shots}, SOG={sog}, G={goals}, FO={fo_wins}/{fo_losses}, Pass={pass_completed}/{pass_attempts}")
            
            # Update
            mask = (team_stats['game_id'] == game_id) & (team_stats['team_name'] == team_name)
            if not mask.any():
                # Try by team_id
                roster = pd.read_csv(OUTPUT_DIR / 'fact_gameroster.csv')
                team_id = roster[(roster['game_id'] == game_id) & (roster['team_name'] == team_name)]['team_id'].iloc[0] if len(roster[(roster['game_id'] == game_id) & (roster['team_name'] == team_name)]) > 0 else None
                if team_id:
                    mask = (team_stats['game_id'] == game_id) & (team_stats['team_id'] == team_id)
            
            if mask.any():
                team_stats.loc[mask, 'shots'] = shots
                team_stats.loc[mask, 'sog'] = sog
                team_stats.loc[mask, 'goals'] = goals
                team_stats.loc[mask, 'fo_wins'] = fo_wins
                team_stats.loc[mask, 'fo_losses'] = fo_losses
                team_stats.loc[mask, 'fo_total'] = total_faceoffs
                team_stats.loc[mask, 'fo_pct'] = round(fo_wins / total_faceoffs * 100, 1) if total_faceoffs > 0 else 0
                team_stats.loc[mask, 'pass_attempts'] = pass_attempts
                team_stats.loc[mask, 'pass_completed'] = pass_completed
                team_stats.loc[mask, 'pass_pct'] = round(pass_completed / pass_attempts * 100, 1) if pass_attempts > 0 else 0
                team_stats.loc[mask, 'giveaways'] = giveaways
                team_stats.loc[mask, 'takeaways'] = takeaways
                team_stats.loc[mask, 'shooting_pct'] = round(goals / sog * 100, 1) if sog > 0 else 0
    
    team_stats.to_csv(OUTPUT_DIR / 'fact_team_game_stats.csv', index=False)
    print("\n✅ Team stats verified and updated!")
    
    return team_stats


def print_summary():
    """Print summary of all fixes."""
    print("\n" + "=" * 60)
    print("FIX SUMMARY")
    print("=" * 60)
    
    # Check all tables
    tables = [
        'fact_team_game_stats', 'fact_player_game_stats', 'fact_goalie_game_stats',
        'fact_events_tracking', 'fact_shifts_tracking', 'fact_h2h', 'fact_wowy',
        'fact_team_zone_time', 'fact_line_combos', 'fact_player_game_position'
    ]
    
    print("\nTable Status:")
    for table in tables:
        try:
            df = pd.read_csv(OUTPUT_DIR / f'{table}.csv')
            has_team_name = 'team_name' in df.columns or 'team_id' not in df.columns
            has_player_name = 'player_name' in df.columns or 'player_id' not in df.columns
            key_cols = [c for c in df.columns if 'key' in c.lower()]
            
            status = "✅" if has_team_name and has_player_name and key_cols else "⚠️"
            print(f"  {status} {table}: {len(df)} rows, keys={key_cols[:2]}")
        except Exception as e:
            print(f"  ❌ {table}: {e}")


def main():
    """Run all fixes."""
    print("=" * 60)
    print("BENCHSIGHT FINAL DATA FIXES")
    print("=" * 60)
    
    # 1. Add names to all tables
    add_names_to_tables()
    
    # 2. Fix tracking keys
    fix_events_tracking_keys()
    
    # 3. Create goalie microstats
    create_goalie_microstats()
    
    # 4. Verify team stats
    verify_team_stats()
    
    # 5. Print summary
    print_summary()
    
    print("\n" + "=" * 60)
    print("ALL FIXES COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
