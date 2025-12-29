"""
BenchSight Stats Calculator
Calculates all player and goalie statistics from tracking data.

Usage:
    python3 src/calculate_stats.py                    # Calculate all games
    python3 src/calculate_stats.py --game 19045       # Single game
    python3 src/calculate_stats.py --upload           # Calculate and upload to Supabase
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# Config
DATA_DIR = "data/output"
OUTPUT_FILE_PLAYER = "fact_player_game_stats.csv"
OUTPUT_FILE_GOALIE = "fact_goalie_game_stats.csv"

# Supabase
SUPABASE_URL = "https://uuaowslhpgyiudmbvqze.supabase.co"
SUPABASE_KEY = "sb_publishable_t1lIOebbbCjAu_YBKc8tLg_B_zH_l73"


def load_data():
    """Load all required data files."""
    data = {}
    
    files = {
        'events': 'fact_events_tracking.csv',
        'events_long': 'fact_events_long.csv',
        'shifts': 'fact_shifts_tracking.csv',
        'shift_players': 'fact_shift_players_tracking.csv',
        'linked_events': 'fact_linked_events_tracking.csv',
        'sequences': 'fact_sequences_tracking.csv',
        'roster': 'fact_gameroster.csv',
        'players': 'dim_player.csv',
        'schedule': 'dim_schedule.csv',
        'box_score': 'fact_box_score_tracking.csv',
        'coordinates': 'fact_event_coordinates.csv'
    }
    
    for key, filename in files.items():
        path = os.path.join(DATA_DIR, filename)
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, low_memory=False)
                df.columns = [c.lower().strip() for c in df.columns]
                data[key] = df
                print(f"  Loaded {filename}: {len(df)} rows")
            except Exception as e:
                print(f"  Warning: Could not load {filename}: {e}")
                data[key] = pd.DataFrame()
        else:
            print(f"  Missing: {filename}")
            data[key] = pd.DataFrame()
    
    return data


def calculate_basic_stats(events_df, player_id, game_id):
    """Calculate basic box score stats."""
    stats = {}
    
    # Filter to player and game
    pe = events_df[
        (events_df['game_id'] == game_id) & 
        (events_df['event_player_1_id'] == player_id)
    ]
    
    # Goals
    goals = pe[
        (pe['event_type'].str.lower() == 'shot') & 
        (pe['event_detail_1'].str.lower().str.contains('goal', na=False))
    ]
    stats['g'] = len(goals)
    
    # Shots on goal
    shots = pe[pe['event_type'].str.lower() == 'shot']
    sog = shots[
        shots['event_detail_1'].str.lower().str.contains('goal|onnet|save', na=False, regex=True)
    ]
    stats['sog'] = len(sog)
    
    # Shooting percentage
    stats['sh_pct'] = (stats['g'] / stats['sog'] * 100) if stats['sog'] > 0 else None
    
    # Assists (check event_player_2 and event_player_3)
    game_events = events_df[events_df['game_id'] == game_id]
    a1 = game_events[
        (game_events['event_player_2_id'] == player_id) &
        (game_events['event_detail_1'].str.lower().str.contains('goal', na=False))
    ]
    a2 = game_events[
        (game_events['event_player_3_id'] == player_id) &
        (game_events['event_detail_1'].str.lower().str.contains('goal', na=False))
    ]
    stats['a1'] = len(a1)
    stats['a2'] = len(a2)
    stats['a'] = stats['a1'] + stats['a2']
    stats['pts'] = stats['g'] + stats['a']
    
    # Hits
    hits = pe[pe['event_type'].str.lower() == 'hit']
    stats['hits'] = len(hits)
    
    # Penalties
    penalties = pe[pe['event_type'].str.lower() == 'penalty']
    stats['pen_taken'] = len(penalties)
    stats['pim'] = penalties['penalty_minutes'].sum() if 'penalty_minutes' in penalties.columns and len(penalties) > 0 else 0
    
    return stats


def calculate_micro_offense(events_df, player_id, game_id):
    """Calculate micro-offense stats."""
    stats = {}
    
    pe = events_df[
        (events_df['game_id'] == game_id) & 
        (events_df['event_player_1_id'] == player_id)
    ]
    
    # Passes
    passes = pe[pe['event_type'].str.lower() == 'pass']
    stats['pass_att'] = len(passes)
    stats['pass_comp'] = len(passes[passes['event_successful'] == 1]) if 'event_successful' in passes.columns else 0
    stats['pass_pct'] = (stats['pass_comp'] / stats['pass_att'] * 100) if stats['pass_att'] > 0 else None
    
    # Dekes
    dekes = pe[pe['event_type'].str.lower().str.contains('deke', na=False)]
    stats['deke'] = len(dekes)
    stats['deke_success'] = len(dekes[dekes['event_successful'] == 1]) if 'event_successful' in dekes.columns else 0
    
    # Check play_detail columns for various events
    def count_play_detail(detail_value):
        count = 0
        for col in ['play_detail_1', 'play_detail_2', 'event_detail_1', 'event_detail_2']:
            if col in pe.columns:
                count += pe[pe[col].str.lower().str.contains(detail_value.lower(), na=False)].shape[0]
        return count
    
    stats['screen'] = count_play_detail('screen')
    stats['tip'] = count_play_detail('tip')
    stats['one_timer'] = count_play_detail('onetimer')
    stats['board_battle_win'] = count_play_detail('boardbattlewin')
    stats['board_battle_loss'] = count_play_detail('boardbattleloss')
    stats['puck_recovery'] = count_play_detail('puckrecovery')
    stats['drive'] = count_play_detail('drive')
    stats['dump_chase'] = count_play_detail('dumpandchase')
    stats['second_touch'] = count_play_detail('secondtouch')
    stats['net_presence'] = count_play_detail('netpresence')
    stats['give_and_go'] = count_play_detail('giveandgo')
    stats['beat_defender'] = count_play_detail('beatdefender')
    stats['protect_puck'] = count_play_detail('puckprotection')
    
    return stats


def calculate_micro_defense(events_df, player_id, game_id):
    """Calculate micro-defense stats."""
    stats = {}
    
    pe = events_df[
        (events_df['game_id'] == game_id) & 
        (events_df['event_player_1_id'] == player_id)
    ]
    
    # Takeaways
    takeaways = pe[pe['event_type'].str.lower().str.contains('takeaway', na=False)]
    stats['takeaway'] = len(takeaways)
    
    # Giveaways
    giveaways = pe[pe['event_type'].str.lower().str.contains('giveaway|turnover', na=False, regex=True)]
    stats['giveaway'] = len(giveaways)
    stats['turnover_diff'] = stats['takeaway'] - stats['giveaway']
    
    # Check play_detail columns
    def count_play_detail(detail_value):
        count = 0
        for col in ['play_detail_1', 'play_detail_2', 'event_detail_1', 'event_detail_2']:
            if col in pe.columns:
                count += pe[pe[col].str.lower().str.contains(detail_value.lower(), na=False)].shape[0]
        return count
    
    stats['stick_check'] = count_play_detail('stickcheck')
    stats['poke_check'] = count_play_detail('pokecheck')
    stats['backcheck'] = count_play_detail('backcheck')
    stats['shot_block_play'] = count_play_detail('blockedshot')
    stats['in_passing_lane'] = count_play_detail('inpassinglane') + count_play_detail('inshotlane')
    stats['pass_intercept'] = count_play_detail('passintercept')
    stats['forecheck_pressure'] = count_play_detail('forecheckpressure')
    stats['forecheck_win'] = count_play_detail('forecheckwin')
    stats['gap_close'] = count_play_detail('gapclose')
    stats['box_out'] = count_play_detail('boxout')
    stats['clear_success'] = count_play_detail('clear')
    stats['coverage_blown'] = count_play_detail('blowncoverage')
    stats['angling'] = count_play_detail('angling')
    stats['pressure'] = count_play_detail('pressure')
    
    # Battles
    stats['battle_win'] = stats.get('board_battle_win', 0) + count_play_detail('loosepuckwin')
    stats['battle_loss'] = stats.get('board_battle_loss', 0) + count_play_detail('loosepuckloss')
    total_battles = stats['battle_win'] + stats['battle_loss']
    stats['battle_pct'] = (stats['battle_win'] / total_battles * 100) if total_battles > 0 else None
    
    return stats


def calculate_transition_stats(events_df, player_id, game_id):
    """Calculate transition and zone stats."""
    stats = {}
    
    pe = events_df[
        (events_df['game_id'] == game_id) & 
        (events_df['event_player_1_id'] == player_id)
    ]
    
    # Zone entries
    zone_events = pe[pe['event_type'].str.lower() == 'zone']
    entries = zone_events[zone_events['event_detail_1'].str.lower().str.contains('entry', na=False)]
    stats['zone_entry'] = len(entries)
    
    if 'event_detail_2' in entries.columns:
        ctrl = entries[entries['event_detail_2'].str.lower().str.contains('carry|pass', na=False, regex=True)]
        stats['zone_entry_ctrl'] = len(ctrl)
        dump = entries[entries['event_detail_2'].str.lower().str.contains('dump', na=False)]
        stats['zone_entry_dump'] = len(dump)
    else:
        stats['zone_entry_ctrl'] = 0
        stats['zone_entry_dump'] = 0
    
    stats['zone_entry_pct'] = (stats['zone_entry_ctrl'] / stats['zone_entry'] * 100) if stats['zone_entry'] > 0 else None
    
    # Zone exits
    exits = zone_events[zone_events['event_detail_1'].str.lower().str.contains('exit', na=False)]
    stats['zone_exit'] = len(exits)
    
    if 'event_detail_2' in exits.columns:
        ctrl_exit = exits[exits['event_detail_2'].str.lower().str.contains('carry|pass', na=False, regex=True)]
        stats['zone_exit_ctrl'] = len(ctrl_exit)
    else:
        stats['zone_exit_ctrl'] = 0
    
    # Check play details for denials, breakouts
    def count_play_detail(detail_value):
        count = 0
        for col in ['play_detail_1', 'play_detail_2']:
            if col in pe.columns:
                count += pe[pe[col].str.lower().str.contains(detail_value.lower(), na=False)].shape[0]
        return count
    
    stats['zone_entry_denial'] = count_play_detail('entrydenial')
    stats['zone_exit_denial'] = count_play_detail('exitdenial')
    stats['breakout'] = count_play_detail('breakout')
    
    return stats


def calculate_faceoff_stats(events_df, player_id, game_id):
    """Calculate faceoff stats."""
    stats = {}
    
    pe = events_df[
        (events_df['game_id'] == game_id) & 
        (events_df['event_player_1_id'] == player_id) &
        (events_df['event_type'].str.lower() == 'faceoff')
    ]
    
    stats['fow'] = len(pe[pe['event_successful'] == 1]) if 'event_successful' in pe.columns else 0
    stats['fol'] = len(pe[pe['event_successful'] == 0]) if 'event_successful' in pe.columns else 0
    total_fo = stats['fow'] + stats['fol']
    stats['fo_pct'] = (stats['fow'] / total_fo * 100) if total_fo > 0 else None
    
    # Zone faceoffs
    if 'zone' in pe.columns:
        oz_fo = pe[pe['zone'].str.upper() == 'OZ']
        dz_fo = pe[pe['zone'].str.upper() == 'DZ']
        nz_fo = pe[pe['zone'].str.upper() == 'NZ']
        stats['oz_fow'] = len(oz_fo[oz_fo['event_successful'] == 1]) if 'event_successful' in oz_fo.columns else 0
        stats['dz_fow'] = len(dz_fo[dz_fo['event_successful'] == 1]) if 'event_successful' in dz_fo.columns else 0
        stats['nz_fow'] = len(nz_fo[nz_fo['event_successful'] == 1]) if 'event_successful' in nz_fo.columns else 0
    else:
        stats['oz_fow'] = 0
        stats['dz_fow'] = 0
        stats['nz_fow'] = 0
    
    return stats


def calculate_toi_stats(shifts_df, shift_players_df, player_id, game_id):
    """Calculate time on ice stats."""
    stats = {}
    
    # Get player shifts
    if len(shift_players_df) > 0:
        player_shifts = shift_players_df[
            (shift_players_df['game_id'] == game_id) &
            (shift_players_df['player_id'] == player_id)
        ]
    else:
        player_shifts = pd.DataFrame()
    
    if len(player_shifts) > 0 and 'shift_duration_seconds' in player_shifts.columns:
        stats['toi'] = int(player_shifts['shift_duration_seconds'].sum())
        stats['shifts'] = len(player_shifts)
    elif len(shifts_df) > 0:
        # Try to calculate from shifts table
        game_shifts = shifts_df[shifts_df['game_id'] == game_id]
        # This is trickier - need to check player columns
        stats['toi'] = 0
        stats['shifts'] = 0
    else:
        stats['toi'] = 0
        stats['shifts'] = 0
    
    stats['toi_min'] = round(stats['toi'] / 60, 1) if stats['toi'] > 0 else 0
    stats['avg_shift'] = round(stats['toi'] / stats['shifts'], 1) if stats['shifts'] > 0 else None
    
    # Situation TOI (if available)
    if len(player_shifts) > 0 and 'strength' in player_shifts.columns:
        ev_shifts = player_shifts[player_shifts['strength'].str.contains('5v5|4v4|3v3', na=False, regex=True)]
        stats['toi_ev'] = int(ev_shifts['shift_duration_seconds'].sum()) if 'shift_duration_seconds' in ev_shifts.columns else 0
    else:
        stats['toi_ev'] = 0
    
    stats['toi_pp'] = 0
    stats['toi_pk'] = 0
    
    # Long shifts (beer league)
    if len(player_shifts) > 0 and 'shift_duration_seconds' in player_shifts.columns:
        long_shifts = player_shifts[player_shifts['shift_duration_seconds'] > 90]
        stats['shift_too_long'] = len(long_shifts)
    else:
        stats['shift_too_long'] = 0
    
    return stats


def calculate_rating_aware_stats(events_df, roster_df, players_df, player_id, game_id):
    """Calculate rating-aware stats unique to BLB."""
    stats = {}
    
    # Get player's skill rating
    if len(players_df) > 0 and 'skill_rating' in players_df.columns:
        player_row = players_df[players_df['player_id'] == player_id]
        player_rating = player_row['skill_rating'].values[0] if len(player_row) > 0 else 4
    else:
        player_rating = 4
    
    # Get game roster for opponent ratings
    if len(roster_df) > 0:
        game_roster = roster_df[roster_df['game_id'] == game_id]
        player_info = game_roster[game_roster['player_id'] == player_id]
        
        if len(player_info) > 0:
            player_team = player_info['team_id'].values[0] if 'team_id' in player_info.columns else None
            
            if player_team:
                opponents = game_roster[game_roster['team_id'] != player_team]
                if 'skill_rating' in opponents.columns:
                    stats['avg_opp_skill_faced'] = round(opponents['skill_rating'].mean(), 2)
                    stats['qoc_rating'] = stats['avg_opp_skill_faced']
                    stats['skill_vs_opp'] = round(player_rating - stats['qoc_rating'], 2)
                else:
                    stats['avg_opp_skill_faced'] = None
                    stats['qoc_rating'] = None
                    stats['skill_vs_opp'] = None
                
                teammates = game_roster[(game_roster['team_id'] == player_team) & (game_roster['player_id'] != player_id)]
                if 'skill_rating' in teammates.columns:
                    stats['qot_rating'] = round(teammates['skill_rating'].mean(), 2)
                else:
                    stats['qot_rating'] = None
    
    # Default values if not calculated
    stats.setdefault('avg_opp_skill_faced', None)
    stats.setdefault('qoc_rating', None)
    stats.setdefault('qot_rating', None)
    stats.setdefault('skill_vs_opp', None)
    stats['giveaway_vs_elite'] = 0  # Would need on-ice opponent tracking
    
    return stats


def calculate_rate_stats(stats):
    """Calculate per-60 rate stats."""
    toi = stats.get('toi', 0)
    
    if toi > 0:
        multiplier = 3600 / toi  # Per 60 minutes
        stats['g_60'] = round(stats.get('g', 0) * multiplier, 2)
        stats['a_60'] = round(stats.get('a', 0) * multiplier, 2)
        stats['pts_60'] = round(stats.get('pts', 0) * multiplier, 2)
        stats['sog_60'] = round(stats.get('sog', 0) * multiplier, 2)
        stats['cf_60_rate'] = round(stats.get('cf', 0) * multiplier, 2) if stats.get('cf') else None
    else:
        stats['g_60'] = None
        stats['a_60'] = None
        stats['pts_60'] = None
        stats['sog_60'] = None
        stats['cf_60_rate'] = None
    
    return stats


def calculate_composite_ratings(stats):
    """Calculate composite rating scores."""
    
    # Offensive rating (weighted combination)
    o_factors = [
        stats.get('g', 0) * 3,
        stats.get('a', 0) * 2,
        stats.get('sog', 0) * 0.5,
        stats.get('pass_danger', 0) * 1,
        stats.get('zone_entry_ctrl', 0) * 0.5,
        stats.get('scoring_chance_for', 0) * 1,
    ]
    stats['offensive_rating'] = round(sum(o_factors), 1)
    
    # Defensive rating
    d_factors = [
        stats.get('takeaway', 0) * 2,
        stats.get('shot_block_play', 0) * 1,
        stats.get('stick_check', 0) * 0.5,
        stats.get('backcheck', 0) * 1,
        stats.get('zone_exit_ctrl', 0) * 0.5,
        -stats.get('giveaway', 0) * 1,
    ]
    stats['defensive_rating'] = round(sum(d_factors), 1)
    
    # Two-way rating
    stats['two_way_rating'] = round((stats['offensive_rating'] + stats['defensive_rating']) / 2, 1)
    
    # Hustle rating
    h_factors = [
        stats.get('backcheck', 0) * 2,
        stats.get('forecheck_pressure', 0) * 1,
        stats.get('battle_win', 0) * 1,
        stats.get('pressure', 0) * 1,
        stats.get('puck_recovery', 0) * 0.5,
    ]
    stats['hustle_rating'] = round(sum(h_factors), 1)
    
    # Impact score
    impact_factors = [
        stats.get('pts', 0) * 5,
        stats.get('plus_minus', 0) * 2,
        stats.get('takeaway', 0) - stats.get('giveaway', 0),
    ]
    stats['impact_score'] = round(sum(impact_factors), 1)
    
    return stats


def calculate_player_game_stats(data, player_id, game_id):
    """Calculate all stats for a player in a game."""
    stats = {
        'player_game_key': f"{player_id}_{game_id}",
        'player_id': player_id,
        'game_id': game_id,
        '_export_timestamp': datetime.now().isoformat(),
        'is_tracked': True
    }
    
    # Get player info
    if len(data['roster']) > 0:
        player_roster = data['roster'][
            (data['roster']['game_id'] == game_id) & 
            (data['roster']['player_id'] == player_id)
        ]
        if len(player_roster) > 0:
            stats['team_id'] = player_roster['team_id'].values[0] if 'team_id' in player_roster.columns else None
            stats['position'] = player_roster['position'].values[0] if 'position' in player_roster.columns else None
    
    # Calculate all stat categories
    events = data.get('events', pd.DataFrame())
    if len(events) == 0:
        events = data.get('events_long', pd.DataFrame())
    
    if len(events) > 0:
        stats.update(calculate_basic_stats(events, player_id, game_id))
        stats.update(calculate_micro_offense(events, player_id, game_id))
        stats.update(calculate_micro_defense(events, player_id, game_id))
        stats.update(calculate_transition_stats(events, player_id, game_id))
        stats.update(calculate_faceoff_stats(events, player_id, game_id))
    
    stats.update(calculate_toi_stats(
        data.get('shifts', pd.DataFrame()),
        data.get('shift_players', pd.DataFrame()),
        player_id, game_id
    ))
    
    stats.update(calculate_rating_aware_stats(
        events,
        data.get('roster', pd.DataFrame()),
        data.get('players', pd.DataFrame()),
        player_id, game_id
    ))
    
    stats = calculate_rate_stats(stats)
    stats = calculate_composite_ratings(stats)
    
    # Set defaults for XY-required stats (NULL until we have coordinates)
    xy_stats = ['hdcf', 'mdcf', 'ldcf', 'hdca', 'mdca', 'ldca', 
                'xgf', 'xga', 'xgf_pct', 'xg_diff', 'g_xg_diff',
                'slot_pass', 'royal_road_pass']
    for stat in xy_stats:
        stats.setdefault(stat, None)
    
    # Set defaults for tracking stats (NULL until we have tracking)
    tracking_stats = ['speed_max', 'speed_bursts_20', 'speed_bursts_22', 
                      'dist_skated', 'accel_max']
    for stat in tracking_stats:
        stats.setdefault(stat, None)
    
    return stats


def main():
    print("=" * 60)
    print("BENCHSIGHT STATS CALCULATOR")
    print("=" * 60)
    
    # Parse args
    single_game = None
    upload = '--upload' in sys.argv
    
    if '--game' in sys.argv:
        idx = sys.argv.index('--game')
        if idx + 1 < len(sys.argv):
            single_game = int(sys.argv[idx + 1])
    
    # Load data
    print("\nLoading data...")
    data = load_data()
    
    # Get list of tracked games
    if len(data['events']) > 0:
        tracked_games = data['events']['game_id'].unique()
    elif len(data['events_long']) > 0:
        tracked_games = data['events_long']['game_id'].unique()
    else:
        print("No events data found!")
        return
    
    if single_game:
        tracked_games = [single_game] if single_game in tracked_games else []
    
    print(f"\nProcessing {len(tracked_games)} games...")
    
    # Calculate stats for each player in each game
    all_player_stats = []
    
    for game_id in tracked_games:
        print(f"\n  Game {game_id}...")
        
        # Get players in this game
        if len(data['roster']) > 0:
            game_roster = data['roster'][data['roster']['game_id'] == game_id]
            player_ids = game_roster['player_id'].unique()
        else:
            # Try to get from events
            events = data['events'] if len(data['events']) > 0 else data['events_long']
            game_events = events[events['game_id'] == game_id]
            player_ids = game_events['event_player_1_id'].dropna().unique()
        
        for player_id in player_ids:
            if pd.isna(player_id):
                continue
            try:
                stats = calculate_player_game_stats(data, int(player_id), game_id)
                all_player_stats.append(stats)
            except Exception as e:
                print(f"    Error for player {player_id}: {e}")
    
    # Create DataFrame
    df = pd.DataFrame(all_player_stats)
    
    # Save to CSV
    output_path = os.path.join(DATA_DIR, OUTPUT_FILE_PLAYER)
    df.to_csv(output_path, index=False)
    print(f"\nSaved {len(df)} player-game records to {output_path}")
    
    # Upload to Supabase if requested
    if upload:
        try:
            from supabase import create_client
            print("\nUploading to Supabase...")
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            
            # Clean data for upload
            records = df.replace({np.nan: None}).to_dict(orient='records')
            
            # Batch upload
            batch_size = 100
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                supabase.table('fact_player_game_stats').upsert(batch).execute()
            
            print(f"Uploaded {len(records)} records to Supabase")
        except Exception as e:
            print(f"Upload error: {e}")
    
    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
