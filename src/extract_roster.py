#!/usr/bin/env python3
"""
=============================================================================
BENCHSIGHT ROSTER EXTRACTOR
=============================================================================
File: extract_roster.py

PURPOSE:
    Extract game rosters from BLB_Tables.xlsx and create JSON files
    that can be loaded into the game tracker.

USAGE:
    python extract_roster.py 18969           # Single game
    python extract_roster.py 18969 18977     # Multiple games
    python extract_roster.py --all           # All games with roster data

OUTPUT:
    Creates roster.json files in each game folder:
    data/raw/games/{game_id}/roster.json

=============================================================================
"""

import sys
import json
import argparse
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("Error: pandas not installed. Run: pip install pandas openpyxl")
    sys.exit(1)


def extract_roster(game_id: int, blb_file: Path, output_dir: Path) -> dict:
    """
    Extract roster for a specific game from BLB_Tables.xlsx
    
    Args:
        game_id: Game ID number
        blb_file: Path to BLB_Tables.xlsx
        output_dir: Path to game output directory
        
    Returns:
        dict: Roster data in tracker format
    """
    # Load BLB Tables
    try:
        xl = pd.ExcelFile(blb_file)
    except Exception as e:
        print(f"Error loading BLB_Tables.xlsx: {e}")
        return None
    
    # Find roster sheet
    roster_sheet = None
    for sheet in ['fact_gameroster', 'gameroster', 'roster', 'fact_roster']:
        if sheet in xl.sheet_names:
            roster_sheet = sheet
            break
    
    if not roster_sheet:
        print(f"No roster sheet found in BLB_Tables.xlsx")
        print(f"Available sheets: {xl.sheet_names}")
        return None
    
    # Load roster data
    roster_df = pd.read_excel(xl, sheet_name=roster_sheet)
    
    # Filter for specific game
    game_col = None
    for col in ['game_id', 'GameID', 'game_id_num']:
        if col in roster_df.columns:
            game_col = col
            break
    
    if not game_col:
        print(f"No game_id column found. Columns: {roster_df.columns.tolist()}")
        return None
    
    game_roster = roster_df[roster_df[game_col] == game_id]
    
    if len(game_roster) == 0:
        print(f"No roster data found for game {game_id}")
        return None
    
    # Build tracker format
    roster_data = {
        'gid': str(game_id),
        'homeRoster': [],
        'awayRoster': []
    }
    
    # Column mappings (try multiple variants)
    def get_col(df, variants, default=None):
        for v in variants:
            if v in df.columns:
                return v
        return default
    
    number_col = get_col(game_roster, ['player_game_number', 'player_number', 'jersey', 'number', 'Jersey'])
    name_col = get_col(game_roster, ['player_full_name', 'display_name', 'name', 'Player'])
    venue_col = get_col(game_roster, ['team_venue', 'venue', 'home_away', 'HomeAway'])
    pos_col = get_col(game_roster, ['player_position', 'position', 'pos', 'Position'])
    skill_col = get_col(game_roster, ['skill_rating', 'skill', 'rating', 'Skill'])
    
    if not number_col or not name_col:
        print(f"Required columns not found. Available: {game_roster.columns.tolist()}")
        return None
    
    for _, row in game_roster.iterrows():
        try:
            number = int(row[number_col]) if pd.notna(row[number_col]) else 0
        except:
            number = 0
            
        player = {
            'n': number,
            'name': str(row[name_col]) if name_col and pd.notna(row[name_col]) else f'#{number}',
            'pos': str(row[pos_col])[0] if pos_col and pd.notna(row[pos_col]) else 'F',
            'skill': int(row[skill_col]) if skill_col and pd.notna(row[skill_col]) else 4
        }
        
        # Determine home/away
        venue = str(row[venue_col]).lower() if venue_col and pd.notna(row[venue_col]) else ''
        
        if venue in ['home', 'h', 'Home']:
            roster_data['homeRoster'].append(player)
        elif venue in ['away', 'a', 'Away', 'visitor']:
            roster_data['awayRoster'].append(player)
        else:
            # Default to home if unclear
            roster_data['homeRoster'].append(player)
    
    # Sort by jersey number
    roster_data['homeRoster'].sort(key=lambda x: x['n'])
    roster_data['awayRoster'].sort(key=lambda x: x['n'])
    
    # Save to file
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'roster.json'
    
    with open(output_file, 'w') as f:
        json.dump(roster_data, f, indent=2)
    
    print(f"✅ Game {game_id}: {len(roster_data['homeRoster'])} home, {len(roster_data['awayRoster'])} away players")
    print(f"   Saved to: {output_file}")
    
    return roster_data


def main():
    parser = argparse.ArgumentParser(
        description='Extract game rosters for tracker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_roster.py 18969           # Single game
  python extract_roster.py 18969 18977     # Multiple games
  python extract_roster.py --all           # All games
        """
    )
    
    parser.add_argument('games', nargs='*', type=int, help='Game IDs to extract')
    parser.add_argument('--all', action='store_true', help='Extract all games with roster data')
    parser.add_argument('--blb', type=str, default='data/BLB_Tables.xlsx', help='Path to BLB_Tables.xlsx')
    
    args = parser.parse_args()
    
    blb_file = Path(args.blb)
    if not blb_file.exists():
        print(f"Error: BLB file not found at {blb_file}")
        sys.exit(1)
    
    games_dir = Path('data/raw/games')
    
    if args.all:
        # Get all games from roster sheet
        xl = pd.ExcelFile(blb_file)
        for sheet in ['fact_gameroster', 'gameroster', 'roster']:
            if sheet in xl.sheet_names:
                df = pd.read_excel(xl, sheet_name=sheet)
                for col in ['game_id', 'GameID', 'game_id_num']:
                    if col in df.columns:
                        game_ids = df[col].dropna().unique().astype(int).tolist()
                        args.games = game_ids
                        break
                break
    
    if not args.games:
        print("No games specified. Use: python extract_roster.py 18969")
        print("Or use --all to extract all games")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print("BENCHSIGHT ROSTER EXTRACTOR")
    print(f"{'='*60}\n")
    
    for game_id in args.games:
        output_dir = games_dir / str(game_id)
        extract_roster(game_id, blb_file, output_dir)
    
    print(f"\n{'='*60}")
    print("COMPLETE!")
    print(f"{'='*60}")
    print("\nTo load in tracker:")
    print("1. Open tracker/tracker_v16.html")
    print("2. Enter game ID")
    print("3. Click 📁 Import")
    print("4. Select the roster.json file")


if __name__ == '__main__':
    main()
