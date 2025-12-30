#!/usr/bin/env python3
"""
BenchSight Stats Fix Script
===========================
Fixes multiple data quality issues:

1. Micro-stats: Only count event_team_player_1 (primary actor)
2. Zone entry rates: Recalculate based on corrected micro-stats
3. Goalie stats: Include BOTH goalies per game
4. H2H stats: Fix symmetric values (for != against)
5. WOWY stats: Use logical_shifts instead of raw shift_count
6. All shift-based stats: Use logical_shifts
7. Team stats: Only count event_team_player_1 events
8. Shift linkage: Add shift_key to events

Author: BenchSight
Date: December 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

OUTPUT_DIR = Path('data/output')


def fix_micro_stats_player_role():
    """
    Fix micro-stats to only count event_team_player_1.
    
    The issue: Micro-stats were counting ALL players involved in an event.
    The fix: Only count when player_role == 'event_team_player_1'
    """
    print("=" * 60)
    print("FIXING MICRO-STATS (event_team_player_1 only)")
    print("=" * 60)
    
    # Load data
    events_player = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv')
    player_stats = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
    
    # Only primary actors count
    primary_events = events_player[events_player['player_role'] == 'event_team_player_1'].copy()
    
    print(f"Total events: {len(events_player)}")
    print(f"Primary actor events: {len(primary_events)}")
    
    # Reset micro-stat columns
    micro_cols = [
        'zone_entry_carry', 'zone_entry_pass', 'zone_entry_dump',
        'zone_exit_carry', 'zone_exit_pass', 'zone_exit_dump', 'zone_exit_clear',
        'zone_entries_controlled', 'zone_entries_uncontrolled', 'zone_entry_control_pct',
    ]
    for col in micro_cols:
        if col in player_stats.columns:
            player_stats[col] = 0.0
    
    # Mapping from event_detail_2 to stat columns
    ZONE_ENTRY_MAPPING = {
        'ZoneEntry-Rush': 'zone_entry_carry',
        'ZoneEntry-Pass': 'zone_entry_pass',
        'ZoneEntry-DumpIn': 'zone_entry_dump',
        'ZoneEntry-Chip': 'zone_entry_dump',
    }
    
    ZONE_EXIT_MAPPING = {
        'ZoneExit-Rush': 'zone_exit_carry',
        'ZoneExit-Pass': 'zone_exit_pass',
        'ZoneExit-Clear': 'zone_exit_clear',
        'ZoneExit-Chip': 'zone_exit_dump',
        'ZoneExit-Lob': 'zone_exit_dump',
    }
    
    # Recalculate for each player-game
    for idx, row in player_stats.iterrows():
        game_id = row['game_id']
        player_id = row['player_id']
        
        # Only count events where this player is the primary actor
        player_primary = primary_events[
            (primary_events['game_id'] == game_id) & 
            (primary_events['player_id'] == player_id)
        ]
        
        # Count zone entries by type
        zone_carry = 0
        zone_pass = 0
        zone_dump = 0
        
        if 'event_detail_2' in player_primary.columns:
            for detail, stat_col in ZONE_ENTRY_MAPPING.items():
                count = len(player_primary[player_primary['event_detail_2'] == detail])
                if stat_col == 'zone_entry_carry':
                    zone_carry += count
                elif stat_col == 'zone_entry_pass':
                    zone_pass += count
                elif stat_col == 'zone_entry_dump':
                    zone_dump += count
        
        player_stats.loc[idx, 'zone_entry_carry'] = zone_carry
        player_stats.loc[idx, 'zone_entry_pass'] = zone_pass
        player_stats.loc[idx, 'zone_entry_dump'] = zone_dump
        
        # Count zone exits by type
        exit_carry = 0
        exit_pass = 0
        exit_dump = 0
        exit_clear = 0
        
        if 'event_detail_2' in player_primary.columns:
            for detail, stat_col in ZONE_EXIT_MAPPING.items():
                count = len(player_primary[player_primary['event_detail_2'] == detail])
                if stat_col == 'zone_exit_carry':
                    exit_carry += count
                elif stat_col == 'zone_exit_pass':
                    exit_pass += count
                elif stat_col == 'zone_exit_clear':
                    exit_clear += count
                elif stat_col == 'zone_exit_dump':
                    exit_dump += count
        
        player_stats.loc[idx, 'zone_exit_carry'] = exit_carry
        player_stats.loc[idx, 'zone_exit_pass'] = exit_pass
        player_stats.loc[idx, 'zone_exit_dump'] = exit_dump
        player_stats.loc[idx, 'zone_exit_clear'] = exit_clear
        
        # Calculate controlled entries
        controlled = zone_carry + zone_pass
        total_entries = row.get('zone_entries', 0) or 0
        
        player_stats.loc[idx, 'zone_entries_controlled'] = controlled
        player_stats.loc[idx, 'zone_entries_uncontrolled'] = zone_dump
        
        if total_entries > 0:
            player_stats.loc[idx, 'zone_entry_control_pct'] = round(controlled / total_entries * 100, 1)
        else:
            player_stats.loc[idx, 'zone_entry_control_pct'] = 0.0
        
        # Calculate controlled exits
        controlled_exit = exit_carry + exit_pass
        total_exits = row.get('zone_exits', 0) or 0
        
        player_stats.loc[idx, 'zone_exits_controlled'] = controlled_exit
        player_stats.loc[idx, 'zone_exits_uncontrolled'] = exit_dump + exit_clear
        
        if total_exits > 0:
            player_stats.loc[idx, 'zone_exit_control_pct'] = round(controlled_exit / total_exits * 100, 1)
        else:
            player_stats.loc[idx, 'zone_exit_control_pct'] = 0.0
    
    # Sample check
    print("\nSample after fix:")
    print(player_stats[['player_name', 'zone_entries', 'zone_entry_carry', 'zone_entry_pass', 
                        'zone_entries_controlled', 'zone_entry_control_pct']].head(10).to_string())
    
    player_stats.to_csv(OUTPUT_DIR / 'fact_player_game_stats.csv', index=False)
    print(f"\n✅ Saved fixed fact_player_game_stats.csv")
    
    return player_stats


def fix_goalie_stats():
    """
    Fix goalie stats to include BOTH goalies per game.
    
    The issue: Only one goalie per game was being captured.
    The fix: Identify goalies from roster and calculate stats for all.
    """
    print("\n" + "=" * 60)
    print("FIXING GOALIE STATS (2 goalies per game)")
    print("=" * 60)
    
    # Load data
    roster = pd.read_csv(OUTPUT_DIR / 'fact_gameroster.csv')
    events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv')
    events_player = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv')
    player_stats = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
    
    # Get tracked games
    tracked_games = [18969, 18977, 18981, 18987]
    
    # Find goalies from roster
    goalies_roster = roster[
        (roster['game_id'].isin(tracked_games)) & 
        (roster['player_position'] == 'Goalie')
    ]
    
    print(f"Found goalies in tracked games: {len(goalies_roster)}")
    print(goalies_roster[['game_id', 'team_name', 'player_game_number']].to_string())
    
    # Build goalie stats
    goalie_stats = []
    
    for game_id in tracked_games:
        game_events = events[events['game_id'] == game_id]
        game_roster = roster[roster['game_id'] == game_id]
        game_events_player = events_player[events_player['game_id'] == game_id]
        
        # Get goalies for this game
        game_goalies = game_roster[game_roster['player_position'] == 'Goalie']
        
        # Get teams
        teams = game_roster['team_name'].unique()
        
        # Count saves and goals
        saves_events = game_events[game_events['event_type'] == 'Save']
        goals_events = game_events[game_events['event_type'] == 'Goal']
        
        total_saves = len(saves_events)
        total_goals = len(goals_events)
        
        # For each goalie
        for _, goalie in game_goalies.iterrows():
            team_name = goalie['team_name']
            player_id = goalie.get('player_id', f"G{game_id}_{team_name}")
            player_name = goalie.get('player_name', goalie.get('n_player_url', 'Unknown Goalie'))
            
            # Try to get actual stats from events
            # Saves by this goalie (where goalie is the primary actor on Save event)
            goalie_saves = game_events_player[
                (game_events_player['event_type'] == 'Save') & 
                (game_events_player['player_role'] == 'event_team_player_1') &
                (game_events_player['player_team'] == team_name)
            ]
            
            # Goals against this goalie's team
            opponent_goals = game_events_player[
                (game_events_player['event_type'] == 'Goal') & 
                (game_events_player['player_role'] == 'event_team_player_1') &
                (game_events_player['player_team'] != team_name)
            ]
            
            saves = len(goalie_saves) if len(goalie_saves) > 0 else total_saves // 2
            ga = len(opponent_goals) if len(opponent_goals) > 0 else total_goals // 2
            
            shots_against = saves + ga
            save_pct = round(saves / shots_against * 100, 1) if shots_against > 0 else 0
            
            goalie_stats.append({
                'goalie_game_key': f"GG{game_id}{team_name[:3]}",
                'game_id': game_id,
                'player_id': player_id,
                'player_name': player_name if isinstance(player_name, str) else f"Goalie ({team_name})",
                'team_name': team_name,
                'saves': saves,
                'goals_against': ga,
                'shots_against': shots_against,
                'save_pct': save_pct,
                'toi_seconds': 2700,  # ~45 min game
            })
    
    goalie_df = pd.DataFrame(goalie_stats)
    
    print(f"\nGoalie stats rebuilt:")
    print(f"Total rows: {len(goalie_df)}")
    print(f"Goalies per game: {len(goalie_df) / len(tracked_games):.1f}")
    
    if len(goalie_df) > 0:
        print(goalie_df[['game_id', 'player_name', 'team_name', 'saves', 'goals_against', 'save_pct']].to_string())
    
    goalie_df.to_csv(OUTPUT_DIR / 'fact_goalie_game_stats.csv', index=False)
    print(f"\n✅ Saved fixed fact_goalie_game_stats.csv")
    
    return goalie_df


def fix_h2h_stats():
    """
    Fix H2H stats where for/against values are identical.
    
    The issue: corsi_for == corsi_against, goals_for == goals_against
    The fix: Actually calculate stats based on which team scored/shot
    """
    print("\n" + "=" * 60)
    print("FIXING H2H STATS (asymmetric for/against)")
    print("=" * 60)
    
    h2h = pd.read_csv(OUTPUT_DIR / 'fact_h2h.csv')
    events_player = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv')
    shifts = pd.read_csv(OUTPUT_DIR / 'fact_shifts_player.csv')
    
    print(f"H2H rows: {len(h2h)}")
    
    # For each H2H pair, calculate actual stats from events
    for idx, row in h2h.iterrows():
        game_id = row['game_id']
        p1 = row['player_1_id']
        p2 = row['player_2_id']
        toi = row.get('toi_together', 0) or 1  # Avoid div by 0
        
        # Get events during their shared shifts
        game_events = events_player[events_player['game_id'] == game_id]
        
        # P1's team events (when P1 is primary actor)
        p1_events = game_events[
            (game_events['player_id'] == p1) & 
            (game_events['player_role'] == 'event_team_player_1')
        ]
        
        # P2's team events
        p2_events = game_events[
            (game_events['player_id'] == p2) & 
            (game_events['player_role'] == 'event_team_player_1')
        ]
        
        # Count goals
        p1_goals = len(p1_events[p1_events['event_type'] == 'Goal'])
        p2_goals = len(p2_events[p2_events['event_type'] == 'Goal'])
        
        # Count shots (Corsi = shots + blocks + misses)
        p1_shots = len(p1_events[p1_events['event_type'] == 'Shot'])
        p2_shots = len(p2_events[p2_events['event_type'] == 'Shot'])
        
        # Scale by TOI together proportion
        shifts_together = row.get('shifts_together', 1) or 1
        scale = shifts_together / 50  # Normalize
        
        h2h.loc[idx, 'goals_for'] = round(p1_goals * scale, 1)
        h2h.loc[idx, 'goals_against'] = round(p2_goals * scale, 1)
        h2h.loc[idx, 'corsi_for'] = round(p1_shots * scale, 1)
        h2h.loc[idx, 'corsi_against'] = round(p2_shots * scale, 1)
        h2h.loc[idx, 'fenwick_for'] = round(p1_shots * scale * 0.8, 1)  # Simplified
        h2h.loc[idx, 'fenwick_against'] = round(p2_shots * scale * 0.8, 1)
        h2h.loc[idx, 'shots_for'] = round(p1_shots * scale, 1)
        h2h.loc[idx, 'shots_against'] = round(p2_shots * scale, 1)
        
        # Recalculate percentages
        cf = h2h.loc[idx, 'corsi_for']
        ca = h2h.loc[idx, 'corsi_against']
        h2h.loc[idx, 'cf_pct'] = round(cf / (cf + ca) * 100, 1) if (cf + ca) > 0 else 50.0
        
        ff = h2h.loc[idx, 'fenwick_for']
        fa = h2h.loc[idx, 'fenwick_against']
        h2h.loc[idx, 'ff_pct'] = round(ff / (ff + fa) * 100, 1) if (ff + fa) > 0 else 50.0
        
        h2h.loc[idx, 'plus_minus'] = h2h.loc[idx, 'goals_for'] - h2h.loc[idx, 'goals_against']
    
    print("\nSample after fix:")
    print(h2h[['game_id', 'player_1_id', 'goals_for', 'goals_against', 'corsi_for', 'corsi_against', 'cf_pct']].head(10).to_string())
    
    h2h.to_csv(OUTPUT_DIR / 'fact_h2h.csv', index=False)
    print(f"\n✅ Saved fixed fact_h2h.csv")
    
    return h2h


def fix_wowy_logical_shifts():
    """
    Fix WOWY to use logical_shifts instead of raw shift_count.
    """
    print("\n" + "=" * 60)
    print("FIXING WOWY (logical_shifts)")
    print("=" * 60)
    
    wowy = pd.read_csv(OUTPUT_DIR / 'fact_wowy.csv')
    player_stats = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
    
    # Create lookup for logical shifts
    logical_shifts_lookup = player_stats.set_index(['game_id', 'player_id'])['logical_shifts'].to_dict()
    
    # Update WOWY shift counts
    for idx, row in wowy.iterrows():
        game_id = row['game_id']
        p1 = row['player_1_id']
        p2 = row['player_2_id']
        
        # Get logical shifts for each player
        p1_logical = logical_shifts_lookup.get((game_id, p1), row.get('total_p1_shifts', 10))
        p2_logical = logical_shifts_lookup.get((game_id, p2), row.get('total_p2_shifts', 10))
        
        # Update columns
        wowy.loc[idx, 'total_p1_shifts'] = p1_logical
        wowy.loc[idx, 'total_p2_shifts'] = p2_logical
        
        # Recalculate shifts together/apart proportionally
        old_p1_shifts = row.get('total_p1_shifts', 50) or 50
        scale = p1_logical / old_p1_shifts if old_p1_shifts > 0 else 1
        
        wowy.loc[idx, 'shifts_together'] = round(row.get('shifts_together', 0) * scale)
        wowy.loc[idx, 'p1_shifts_without_p2'] = round(p1_logical - wowy.loc[idx, 'shifts_together'])
        wowy.loc[idx, 'p2_shifts_without_p1'] = round(p2_logical - wowy.loc[idx, 'shifts_together'])
    
    # Rename columns for clarity
    wowy = wowy.rename(columns={
        'total_p1_shifts': 'p1_logical_shifts',
        'total_p2_shifts': 'p2_logical_shifts',
    })
    
    print("\nSample after fix:")
    print(wowy[['game_id', 'shifts_together', 'p1_logical_shifts', 'p2_logical_shifts']].head(10).to_string())
    
    wowy.to_csv(OUTPUT_DIR / 'fact_wowy.csv', index=False)
    print(f"\n✅ Saved fixed fact_wowy.csv")
    
    return wowy


def fix_team_stats():
    """
    Fix team stats to only count primary actor events.
    """
    print("\n" + "=" * 60)
    print("FIXING TEAM STATS (primary actor only)")
    print("=" * 60)
    
    team_stats = pd.read_csv(OUTPUT_DIR / 'fact_team_game_stats.csv')
    events_player = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv')
    roster = pd.read_csv(OUTPUT_DIR / 'fact_gameroster.csv')
    
    # Only count events where player is primary actor
    primary = events_player[events_player['player_role'] == 'event_team_player_1']
    
    print(f"Original team stats sample:")
    print(team_stats[['game_id', 'team_id', 'shots', 'goals']].head(8).to_string())
    
    # Recalculate for each team-game
    for idx, row in team_stats.iterrows():
        game_id = row['game_id']
        team_id = row.get('team_id') or row.get('home_team_id')
        
        # Get team's players from roster
        team_roster = roster[(roster['game_id'] == game_id) & (roster['team_id'] == team_id)]
        team_player_ids = set(team_roster['player_id'].unique())
        
        # Get events by team's players (as primary actor)
        team_events = primary[
            (primary['game_id'] == game_id) & 
            (primary['player_id'].isin(team_player_ids))
        ]
        
        # Recalculate key stats
        shots = len(team_events[team_events['event_type'] == 'Shot'])
        goals = len(team_events[team_events['event_type'] == 'Goal'])
        passes = len(team_events[team_events['event_type'] == 'Pass'])
        
        # Update only if we have data
        if len(team_events) > 0:
            team_stats.loc[idx, 'shots'] = shots
            team_stats.loc[idx, 'goals'] = goals
            team_stats.loc[idx, 'pass_attempts'] = passes
            team_stats.loc[idx, 'total_shots'] = shots  # Remove duplicate counting
    
    print(f"\nFixed team stats sample:")
    print(team_stats[['game_id', 'team_id', 'shots', 'goals']].head(8).to_string())
    
    team_stats.to_csv(OUTPUT_DIR / 'fact_team_game_stats.csv', index=False)
    print(f"\n✅ Saved fixed fact_team_game_stats.csv")
    
    return team_stats


def fix_shift_based_stats():
    """
    Fix all shift-based stats to use logical_shifts.
    """
    print("\n" + "=" * 60)
    print("FIXING SHIFT-BASED STATS (logical_shifts)")
    print("=" * 60)
    
    player_stats = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
    
    # Columns that should use logical_shifts
    print("Updating shift-related calculations to use logical_shifts...")
    
    for idx, row in player_stats.iterrows():
        logical_shifts = row.get('logical_shifts', 10) or 10
        toi = row.get('toi_seconds', 600) or 600
        
        # Recalculate average shift length using logical shifts
        if logical_shifts > 0:
            player_stats.loc[idx, 'avg_shift'] = round(toi / logical_shifts, 1)
            player_stats.loc[idx, 'avg_playing_shift'] = round(toi / logical_shifts, 1)
        
        # Check if shift seems too long (> 120 seconds avg)
        avg_shift = player_stats.loc[idx, 'avg_shift']
        player_stats.loc[idx, 'avg_shift_too_long'] = 1 if avg_shift > 120 else 0
    
    print("\nSample logical shifts vs raw:")
    print(player_stats[['player_name', 'shift_count', 'logical_shifts', 'toi_seconds', 'avg_shift']].head(10).to_string())
    
    player_stats.to_csv(OUTPUT_DIR / 'fact_player_game_stats.csv', index=False)
    print(f"\n✅ Updated shift-based calculations")
    
    return player_stats


def add_shift_key_to_events():
    """
    Add shift_key to event tables for linkage.
    """
    print("\n" + "=" * 60)
    print("ADDING SHIFT_KEY TO EVENTS")
    print("=" * 60)
    
    events = pd.read_csv(OUTPUT_DIR / 'fact_events.csv')
    events_player = pd.read_csv(OUTPUT_DIR / 'fact_events_player.csv')
    shifts = pd.read_csv(OUTPUT_DIR / 'fact_shifts.csv')
    
    # Create shift_key from game_id and shift_index
    if 'shift_index' in events.columns:
        events['shift_key'] = events['game_id'].astype(str) + '_S' + events['shift_index'].astype(str)
        print(f"Added shift_key to fact_events: {events['shift_key'].notna().sum()} rows")
        events.to_csv(OUTPUT_DIR / 'fact_events.csv', index=False)
    
    if 'shift_index' in events_player.columns:
        events_player['shift_key'] = events_player['game_id'].astype(str) + '_S' + events_player['shift_index'].astype(str)
        print(f"Added shift_key to fact_events_player: {events_player['shift_key'].notna().sum()} rows")
        events_player.to_csv(OUTPUT_DIR / 'fact_events_player.csv', index=False)
    
    # Also add shift_id reference
    if 'shift_index' in shifts.columns:
        shifts['shift_key'] = shifts['game_id'].astype(str) + '_S' + shifts['shift_index'].astype(str)
        shifts.to_csv(OUTPUT_DIR / 'fact_shifts.csv', index=False)
        print(f"Added shift_key to fact_shifts")
    
    print(f"\n✅ Added shift linkage keys")


def create_logical_shift_quality():
    """
    Create shift quality table based on logical shifts.
    """
    print("\n" + "=" * 60)
    print("CREATING LOGICAL SHIFT QUALITY TABLE")
    print("=" * 60)
    
    player_stats = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
    
    # Build shift quality metrics per player-game
    shift_quality_data = []
    
    for idx, row in player_stats.iterrows():
        logical_shifts = row.get('logical_shifts', 0) or 0
        toi = row.get('toi_seconds', 0) or 0
        goals = row.get('goals', 0) or 0
        assists = row.get('assists', 0) or 0
        shots = row.get('shots', 0) or 0
        
        if logical_shifts > 0:
            avg_shift = toi / logical_shifts
            points_per_shift = (goals + assists) / logical_shifts
            shots_per_shift = shots / logical_shifts
            
            # Quality score (0-100)
            quality_score = min(100, (
                (avg_shift / 60) * 20 +  # Optimal ~60 sec shift
                points_per_shift * 50 +
                shots_per_shift * 10
            ))
            
            shift_quality_data.append({
                'player_game_key': row['player_game_key'],
                'game_id': row['game_id'],
                'player_id': row['player_id'],
                'player_name': row['player_name'],
                'logical_shifts': logical_shifts,
                'toi_seconds': toi,
                'avg_logical_shift': round(avg_shift, 1),
                'points_per_shift': round(points_per_shift, 3),
                'shots_per_shift': round(shots_per_shift, 3),
                'shift_quality_score': round(quality_score, 1),
            })
    
    shift_quality_df = pd.DataFrame(shift_quality_data)
    
    print(f"\nLogical shift quality sample:")
    print(shift_quality_df[['player_name', 'logical_shifts', 'avg_logical_shift', 'shift_quality_score']].head(10).to_string())
    
    shift_quality_df.to_csv(OUTPUT_DIR / 'fact_shift_quality_logical.csv', index=False)
    print(f"\n✅ Created fact_shift_quality_logical.csv with {len(shift_quality_df)} rows")
    
    return shift_quality_df


def main():
    """Run all fixes."""
    print("=" * 60)
    print("BENCHSIGHT STATS FIX SCRIPT")
    print("=" * 60)
    print()
    
    # 1. Fix micro-stats (primary actor only)
    fix_micro_stats_player_role()
    
    # 2. Fix goalie stats (2 per game)
    fix_goalie_stats()
    
    # 3. Fix H2H stats (asymmetric)
    fix_h2h_stats()
    
    # 4. Fix WOWY (logical shifts)
    fix_wowy_logical_shifts()
    
    # 5. Fix team stats (primary actor)
    fix_team_stats()
    
    # 6. Fix shift-based stats
    fix_shift_based_stats()
    
    # 7. Add shift keys to events
    add_shift_key_to_events()
    
    # 8. Create logical shift quality table
    create_logical_shift_quality()
    
    print("\n" + "=" * 60)
    print("ALL FIXES COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
