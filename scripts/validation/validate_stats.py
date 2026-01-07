#!/usr/bin/env python3
"""
BenchSight Stats Validation Script
Uses VALIDATION_LOG.tsv as training data to validate stat calculations.

Run this before any delivery to ensure calculations are correct.

Usage:
    python scripts/validate_stats.py
"""

import pandas as pd
from pathlib import Path
import sys

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "output"
VALIDATION_LOG = BASE_DIR / "docs" / "VALIDATION_LOG.tsv"

def load_data():
    """Load all required data files."""
    try:
        return {
            'events': pd.read_csv(DATA_DIR / "fact_events_player.csv", dtype=str),
            'shifts': pd.read_csv(DATA_DIR / "fact_shifts_player.csv"),
        }
    except FileNotFoundError as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

def count_stat(events, game_id, player_id, stat_name):
    """Calculate a stat using validated rules."""
    df = events[(events['game_id'] == str(game_id)) & (events['player_id'] == player_id)]
    
    rules = {
        # Goals & Assists
        'goals': lambda d: len(d[(d['event_type'] == 'Goal') & (d['player_role'] == 'event_team_player_1')]),
        'assists': lambda d: len(d[d['play_detail'].str.contains('Assist', na=False)]),
        
        # Shots - SOG = shots with OnNet or Goal in event_detail (not blocked/missed)
        'shots_total': lambda d: len(d[(d['event_type'] == 'Shot') & (d['player_role'] == 'event_team_player_1')]),
        'sog': lambda d: len(d[(d['event_type'] == 'Shot') & (d['player_role'] == 'event_team_player_1') & 
                               (d['event_detail'].str.contains('OnNet|Goal', na=False, regex=True))]),
        'shots_blocked': lambda d: len(d[(d['event_type'] == 'Shot') & (d['player_role'] == 'event_team_player_1') &
                                         (d['event_detail'].str.contains('Blocked', na=False)) &
                                         (~d['event_detail'].str.contains('SameTeam', na=False))]),
        'shots_missed': lambda d: len(d[(d['event_type'] == 'Shot') & (d['player_role'] == 'event_team_player_1') &
                                        (d['event_detail'].str.contains('Missed', na=False))]),
        
        # Passes
        'pass_attempts': lambda d: len(d[(d['event_type'] == 'Pass') & (d['player_role'] == 'event_team_player_1')]),
        'pass_completed': lambda d: len(d[(d['event_type'] == 'Pass') & (d['player_role'] == 'event_team_player_1') & 
                                          (d['event_detail'] == 'Pass_Completed')]),
        'pass_missed': lambda d: len(d[(d['event_type'] == 'Pass') & (d['player_role'] == 'event_team_player_1') & 
                                       (d['event_detail'] == 'Pass_Missed')]),
        'pass_deflected': lambda d: len(d[(d['event_type'] == 'Pass') & (d['player_role'] == 'event_team_player_1') & 
                                          (d['event_detail'] == 'Pass_Deflected')]),
        'pass_targets': lambda d: len(d[(d['event_type'] == 'Pass') & (d['player_role'] == 'event_team_player_2')]),
        'pass_received': lambda d: len(d[(d['event_type'] == 'Pass') & (d['player_role'] == 'event_team_player_2') & 
                                         (d['event_detail'] == 'Pass_Completed')]),
        
        # Faceoffs
        'fo_wins': lambda d: len(d[(d['event_type'] == 'Faceoff') & (d['player_role'] == 'event_team_player_1')]),
        'fo_losses': lambda d: len(d[(d['event_type'] == 'Faceoff') & (d['player_role'] == 'opp_team_player_1')]),
        'fo_total': lambda d: len(d[(d['event_type'] == 'Faceoff') & 
                                    (d['player_role'].isin(['event_team_player_1', 'opp_team_player_1']))]),
        
        # Zone entries
        'zone_entries': lambda d: len(d[(d['event_detail'].str.contains('Entry', na=False)) & 
                                        (d['player_role'] == 'event_team_player_1')]),
        'zone_entries_rush': lambda d: len(d[(d['event_detail_2'] == 'ZoneEntry-Rush') & 
                                             (d['player_role'] == 'event_team_player_1')]),
        
        # Zone exits
        'zone_exits': lambda d: len(d[(d['event_detail'].str.contains('Exit', na=False)) & 
                                      (d['player_role'] == 'event_team_player_1')]),
        
        # Turnovers
        'giveaways': lambda d: len(d[(d['event_detail'].str.contains('Giveaway', na=False)) & 
                                     (d['player_role'] == 'event_team_player_1')]),
        'takeaways': lambda d: len(d[(d['event_detail'].str.contains('Takeaway', na=False)) & 
                                     (d['player_role'] == 'event_team_player_1')]),
        
        # Possession
        'puck_retrievals': lambda d: len(d[(d['event_type'] == 'Possession') & 
                                           (d['event_detail'] == 'PuckRetrieval') & 
                                           (d['player_role'] == 'event_team_player_1')]),
        'puck_recoveries': lambda d: len(d[(d['event_type'] == 'Possession') & 
                                           (d['event_detail'] == 'PuckRecovery') & 
                                           (d['player_role'] == 'event_team_player_1')]),
        'breakaways': lambda d: len(d[(d['event_type'] == 'Possession') & 
                                      (d['event_detail'] == 'Breakaway') & 
                                      (d['player_role'] == 'event_team_player_1')]),
        
        # Loose pucks
        'loose_puck_battles': lambda d: len(d[d['event_type'].str.contains('Loose', na=False)]),
        'loose_puck_wins': lambda d: len(d[(d['event_type'].str.contains('Loose', na=False)) & 
                                           (d['player_role'] == 'event_team_player_1')]),
        'loose_puck_losses': lambda d: len(d[(d['event_type'].str.contains('Loose', na=False)) & 
                                             (d['player_role'].str.contains('opp_team_player', na=False))]),
        
        # Defensive plays
        'stick_checks': lambda d: len(d[(d['play_detail'] == 'StickCheck') | (d['play_detail_2'] == 'StickCheck')]),
        'poke_checks': lambda d: len(d[(d['play_detail'] == 'PokeCheck') | (d['play_detail_2'] == 'PokeCheck')]),
        'blocks': lambda d: len(d[(d['play_detail'] == 'BlockedShot') | (d['play_detail_2'] == 'BlockedShot')]),
        
        # Goalie stats
        'saves': lambda d: len(d[(d['event_type'] == 'Save') & (d['player_role'] == 'event_team_player_1')]),
        'goals_against': lambda d: len(d[(d['event_type'] == 'Goal') & (d['player_role'] == 'opp_team_player_1')]),
        'rebounds': lambda d: len(d[(d['event_type'] == 'Rebound') & (d['player_role'] == 'event_team_player_1')]),
    }
    
    if stat_name in rules:
        return rules[stat_name](df)
    return None

def validate_all():
    """Run validation against all entries in VALIDATION_LOG.tsv"""
    
    if not VALIDATION_LOG.exists():
        print(f"❌ VALIDATION_LOG.tsv not found at {VALIDATION_LOG}")
        return False
    
    data = load_data()
    validation = pd.read_csv(VALIDATION_LOG, sep='\t')
    
    print("=" * 80)
    print("BENCHSIGHT STATS VALIDATION")
    print("=" * 80)
    print(f"Validation file: {VALIDATION_LOG}")
    print(f"Total entries: {len(validation)}")
    print()
    
    passed = 0
    failed = 0
    skipped = 0
    known_issues = 0
    failures = []
    
    for _, row in validation.iterrows():
        game_id = row['game_id']
        player_id = row['player_id']
        stat = row['stat']
        expected = row['actual_value']
        match_col = row['match']
        
        # Skip known issues marked as FALSE
        if match_col == 'FALSE':
            known_issues += 1
            continue
        
        # Skip stats marked as SKIP
        if match_col == 'SKIP':
            skipped += 1
            continue
        
        calculated = count_stat(data['events'], game_id, player_id, stat)
        
        if calculated is None:
            skipped += 1
            continue
        
        try:
            expected_num = float(expected)
            match = abs(calculated - expected_num) < 0.01
        except:
            match = False
        
        if match:
            passed += 1
        else:
            failed += 1
            failures.append(f"  {row['player_name']} | {stat}: Expected {expected}, Got {calculated}")
    
    # Print results
    if failures:
        print("FAILURES:")
        for f in failures:
            print(f"❌ {f}")
        print()
    
    print("-" * 80)
    print(f"✅ Passed:       {passed}")
    print(f"❌ Failed:       {failed}")
    print(f"⏭️  Skipped:      {skipped} (complex stats not yet implemented)")
    print(f"⚠️  Known Issues: {known_issues} (marked FALSE in validation log)")
    print(f"📊 Total:        {passed + failed + skipped + known_issues}")
    print("-" * 80)
    
    if failed == 0:
        print("\n🎉 ALL IMPLEMENTED TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {failed} TESTS FAILED - Review calculations")
        return False

if __name__ == "__main__":
    success = validate_all()
    sys.exit(0 if success else 1)
