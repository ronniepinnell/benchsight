#!/usr/bin/env python3
"""
BenchSight Roster Loader
========================
Generates game configuration files from BLB_Tables.xlsx for the tracker.

Data Sources:
- dim_schedule: Game schedule with teams, dates, scores, video info
- fact_gameroster: Player stats per game (rosters)
- dim_player: Player master data
- dim_team: Team info and colors

Output:
- data/output/games_config.json: All games with rosters for tracker
- data/raw/games/{game_id}/roster.json: Per-game roster files

Usage:
    python src/roster_loader.py                    # Generate all configs
    python src/roster_loader.py --game 18969       # Single game
    python src/roster_loader.py --season 20252026  # Specific season
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd


# Team colors (NORAD official)
TEAM_COLORS = {
    "Ace": "#8B0000",
    "AMOS": "#228B22",
    "HollowBrook": "#4D2640",
    "Nelson": "#F3C323",
    "Orphans": "#C5B358",
    "OS Offices": "#2C8A5E",
    "Outlaws": "#02007B",
    "Platinum": "#667788",
    "Triple J": "#4EB9E5",
    "Velodrome": "#9C47E4"
}


def load_blb_tables(xlsx_path: str) -> dict:
    """Load all relevant sheets from BLB_Tables.xlsx"""
    xl = pd.ExcelFile(xlsx_path)
    
    return {
        'schedule': pd.read_excel(xl, 'dim_schedule'),
        'gameroster': pd.read_excel(xl, 'fact_gameroster'),
        'players': pd.read_excel(xl, 'dim_player'),
        'teams': pd.read_excel(xl, 'dim_team') if 'dim_team' in xl.sheet_names else None
    }


def position_to_short(position: str) -> str:
    """Convert full position to short code"""
    pos = str(position).lower()
    if 'goal' in pos or pos == 'g':
        return 'G'
    elif 'defense' in pos or pos == 'd':
        return 'D'
    else:
        return 'F'


def get_game_roster(gameroster_df: pd.DataFrame, game_id: int, team_name: str) -> list:
    """Extract roster for a specific team in a specific game"""
    mask = (gameroster_df['game_id'] == game_id) & (gameroster_df['team_name'] == team_name)
    team_roster = gameroster_df[mask].copy()
    
    roster = []
    for _, row in team_roster.iterrows():
        player = {
            'n': str(int(row['player_game_number'])) if pd.notna(row['player_game_number']) else '',
            'name': row['player_full_name'],
            'pos': position_to_short(row['player_position']),
            'skill': int(row['skill_rating']) if pd.notna(row.get('skill_rating')) else 4
        }
        roster.append(player)
    
    # Sort: Goalies first, then by position, then by number
    pos_order = {'G': 0, 'D': 1, 'F': 2}
    roster.sort(key=lambda x: (pos_order.get(x['pos'], 2), int(x['n']) if x['n'].isdigit() else 999))
    
    return roster


def build_game_config(schedule_df: pd.DataFrame, gameroster_df: pd.DataFrame, 
                      game_id: int) -> dict:
    """Build complete game configuration for tracker"""
    game = schedule_df[schedule_df['game_id'] == game_id].iloc[0]
    
    home_team = game['home_team_name']
    away_team = game['away_team_name']
    
    config = {
        'gid': str(game_id),
        'date': str(game['date'])[:10] if pd.notna(game['date']) else '',
        'time': str(game['game_time']) if pd.notna(game.get('game_time')) else '',
        'homeTeam': home_team,
        'awayTeam': away_team,
        'homeColor': TEAM_COLORS.get(home_team, '#667788'),
        'awayColor': TEAM_COLORS.get(away_team, '#9C47E4'),
        'homeRoster': get_game_roster(gameroster_df, game_id, home_team),
        'awayRoster': get_game_roster(gameroster_df, game_id, away_team),
        'video': {
            'id': str(game['video_id']) if pd.notna(game.get('video_id')) else '',
            'url': game.get('video_url', ''),
            'start': str(game['video_start_time']) if pd.notna(game.get('video_start_time')) else '',
            'end': str(game['video_end_time']) if pd.notna(game.get('video_end_time')) else '',
            'title': game.get('video_title', '')
        },
        'finalScore': {
            'home': int(game['home_total_goals']) if pd.notna(game.get('home_total_goals')) else None,
            'away': int(game['away_total_goals']) if pd.notna(game.get('away_total_goals')) else None
        },
        'periodScores': {
            'home': [
                int(game.get('home_team_period1_goals', 0) or 0),
                int(game.get('home_team_period2_goals', 0) or 0),
                int(game.get('home_team_period3_goals', 0) or 0),
                int(game.get('home_team_periodOT_goals', 0) or 0)
            ],
            'away': [
                int(game.get('away_team_period1_goals', 0) or 0),
                int(game.get('away_team_period2_goals', 0) or 0),
                int(game.get('away_team_period3_goals', 0) or 0),
                int(game.get('away_team_periodOT_goals', 0) or 0)
            ]
        },
        'gameType': game.get('game_type', 'Regular'),
        'season': game.get('season', '')
    }
    
    return config


def save_game_roster_json(config: dict, games_dir: Path) -> bool:
    """Save roster.json to game folder"""
    game_folder = games_dir / config['gid']
    
    if not game_folder.exists():
        game_folder.mkdir(parents=True)
        # Create standard subfolders
        (game_folder / 'bkups').mkdir(exist_ok=True)
        (game_folder / 'events').mkdir(exist_ok=True)
        (game_folder / 'shots').mkdir(exist_ok=True)
        (game_folder / 'xy').mkdir(exist_ok=True)
    
    # Save roster.json
    roster_file = game_folder / 'roster.json'
    roster_data = {
        'gid': config['gid'],
        'date': config['date'],
        'homeTeam': config['homeTeam'],
        'awayTeam': config['awayTeam'],
        'homeColor': config['homeColor'],
        'awayColor': config['awayColor'],
        'homeRoster': config['homeRoster'],
        'awayRoster': config['awayRoster'],
        'video': config['video'],
        'generated': datetime.now().isoformat()
    }
    
    with open(roster_file, 'w') as f:
        json.dump(roster_data, f, indent=2)
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Generate game configs from BLB_Tables.xlsx')
    parser.add_argument('--game', type=int, help='Generate config for specific game ID')
    parser.add_argument('--season', type=str, help='Generate configs for specific season (e.g., 20252026)')
    parser.add_argument('--xlsx', type=str, default='data/BLB_Tables.xlsx', help='Path to BLB_Tables.xlsx')
    parser.add_argument('--output', type=str, default='data/output/games_config.json', help='Output path for combined config')
    parser.add_argument('--games-dir', type=str, default='data/raw/games', help='Directory for game folders')
    parser.add_argument('--dry-run', action='store_true', help='Print config without saving')
    
    args = parser.parse_args()
    
    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    xlsx_path = project_root / args.xlsx
    output_path = project_root / args.output
    games_dir = project_root / args.games_dir
    
    if not xlsx_path.exists():
        print(f"Error: BLB_Tables.xlsx not found at {xlsx_path}")
        sys.exit(1)
    
    print(f"Loading BLB tables from {xlsx_path}...")
    tables = load_blb_tables(str(xlsx_path))
    
    schedule = tables['schedule']
    gameroster = tables['gameroster']
    
    # Filter games
    if args.game:
        game_ids = [args.game]
    elif args.season:
        game_ids = schedule[schedule['season'] == args.season]['game_id'].unique().tolist()
    else:
        # Get current/recent season (20252026 or latest)
        seasons = schedule['season'].dropna().unique()
        current_season = '20252026' if '20252026' in seasons else sorted(seasons)[-1] if len(seasons) else None
        if current_season:
            game_ids = schedule[schedule['season'] == current_season]['game_id'].unique().tolist()
        else:
            game_ids = schedule['game_id'].unique().tolist()
    
    print(f"Processing {len(game_ids)} games...")
    
    games_config = {}
    success_count = 0
    
    for gid in sorted(game_ids):
        try:
            config = build_game_config(schedule, gameroster, gid)
            games_config[str(gid)] = config
            
            if not args.dry_run:
                save_game_roster_json(config, games_dir)
            
            roster_count = len(config['homeRoster']) + len(config['awayRoster'])
            print(f"  ✓ Game {gid}: {config['homeTeam']} vs {config['awayTeam']} ({roster_count} players)")
            success_count += 1
            
        except Exception as e:
            print(f"  ✗ Game {gid}: {e}")
    
    # Save combined config
    if not args.dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(games_config, f, indent=2)
        print(f"\nSaved combined config to {output_path}")
    
    print(f"\nProcessed {success_count}/{len(game_ids)} games successfully")
    
    if args.dry_run and game_ids:
        print("\n=== Sample Config ===")
        sample = games_config[str(game_ids[0])]
        print(json.dumps(sample, indent=2)[:2000])


if __name__ == '__main__':
    main()
