"""
NORAD Schedule Scraper
Pulls upcoming games from noradhockey.com

Usage:
    python3 src/norad_schedule.py                    # Show upcoming games
    python3 src/norad_schedule.py --season 20242025  # Specific season
    python3 src/norad_schedule.py --add              # Add to Supabase
"""

import sys
import re
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Install required packages:")
    print("  pip3 install requests beautifulsoup4")
    sys.exit(1)

try:
    from supabase import create_client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False

# Config
SUPABASE_URL = "https://uuaowslhpgyiudmbvqze.supabase.co"
SUPABASE_KEY = "sb_publishable_t1lIOebbbCjAu_YBKc8tLg_B_zH_l73"

# NORAD URLs - adjust these based on your league
NORAD_BASE = "https://www.noradhockey.com"
# Common schedule URL patterns:
# https://www.noradhockey.com/schedule/day/league_id/XXXXX
# https://www.noradhockey.com/schedule/list/league_id/XXXXX


def fetch_page(url):
    """Fetch HTML from URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def parse_schedule(html):
    """Parse schedule from NORAD HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    games = []
    
    # Find schedule table/rows - adjust selectors based on actual NORAD structure
    # This is a common pattern, may need adjustment
    
    # Look for game rows
    game_rows = soup.find_all('tr', class_=re.compile(r'game|schedule'))
    
    if not game_rows:
        # Try alternate structure
        game_rows = soup.find_all('div', class_=re.compile(r'game|match'))
    
    for row in game_rows:
        try:
            game = {}
            
            # Try to extract game ID from link
            link = row.find('a', href=re.compile(r'/game/'))
            if link:
                match = re.search(r'/game/(\d+)', link.get('href', ''))
                if match:
                    game['game_id'] = int(match.group(1))
            
            # Extract date
            date_elem = row.find(class_=re.compile(r'date'))
            if date_elem:
                game['date'] = date_elem.get_text(strip=True)
            
            # Extract time
            time_elem = row.find(class_=re.compile(r'time'))
            if time_elem:
                game['time'] = time_elem.get_text(strip=True)
            
            # Extract teams
            teams = row.find_all(class_=re.compile(r'team'))
            if len(teams) >= 2:
                game['away_team'] = teams[0].get_text(strip=True)
                game['home_team'] = teams[1].get_text(strip=True)
            
            # Extract score if available
            scores = row.find_all(class_=re.compile(r'score'))
            if len(scores) >= 2:
                try:
                    game['away_score'] = int(scores[0].get_text(strip=True))
                    game['home_score'] = int(scores[1].get_text(strip=True))
                except:
                    pass
            
            if game.get('game_id') or (game.get('home_team') and game.get('away_team')):
                games.append(game)
                
        except Exception as e:
            continue
    
    return games


def get_schedule_url(league_id=None, season=None):
    """Build schedule URL. Adjust based on your NORAD league."""
    # You'll need to customize this with your actual league ID
    # Example patterns:
    # https://www.noradhockey.com/schedule/day/league_id/12345
    # https://www.noradhockey.com/schedule/list/league_id/12345/season/20242025
    
    if league_id:
        url = f"{NORAD_BASE}/schedule/list/league_id/{league_id}"
        if season:
            url += f"/season/{season}"
        return url
    
    # Default - you'll need to set your league ID
    print("WARNING: No league_id set. Edit norad_schedule.py with your league ID.")
    print("Find your league ID in the URL when viewing your schedule on noradhockey.com")
    return None


def display_games(games):
    """Display games in a table."""
    print("\n" + "=" * 70)
    print(f"{'ID':<8} {'Date':<12} {'Time':<8} {'Away':<20} {'Home':<20}")
    print("=" * 70)
    
    for g in games:
        gid = g.get('game_id', '-')
        date = g.get('date', '-')
        time = g.get('time', '-')
        away = g.get('away_team', '-')[:18]
        home = g.get('home_team', '-')[:18]
        
        print(f"{gid:<8} {date:<12} {time:<8} {away:<20} {home:<20}")
    
    print("=" * 70)
    print(f"Total: {len(games)} games")


def add_to_supabase(games):
    """Add games to Supabase dim_schedule."""
    if not HAS_SUPABASE:
        print("Supabase not installed: pip3 install supabase")
        return
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    added = 0
    skipped = 0
    
    for g in games:
        if not g.get('game_id'):
            skipped += 1
            continue
        
        # Check if exists
        existing = supabase.table('dim_schedule').select('game_id').eq('game_id', g['game_id']).execute()
        
        if existing.data:
            print(f"  Skip {g['game_id']} - already exists")
            skipped += 1
            continue
        
        # Insert
        record = {
            'game_id': g['game_id'],
            'date': g.get('date'),
            'game_time': g.get('time'),
            'home_team_name': g.get('home_team'),
            'away_team_name': g.get('away_team'),
            'home_total_goals': g.get('home_score'),
            'away_total_goals': g.get('away_score'),
        }
        
        try:
            supabase.table('dim_schedule').insert(record).execute()
            print(f"  ✓ Added {g['game_id']}: {g.get('away_team')} @ {g.get('home_team')}")
            added += 1
        except Exception as e:
            print(f"  Error adding {g['game_id']}: {e}")
            skipped += 1
    
    print(f"\nAdded: {added}, Skipped: {skipped}")


def main():
    # Parse args
    season = None
    add_mode = '--add' in sys.argv
    
    if '--season' in sys.argv:
        idx = sys.argv.index('--season')
        if idx + 1 < len(sys.argv):
            season = sys.argv[idx + 1]
    
    # TODO: Set your league ID here
    LEAGUE_ID = None  # e.g., "12345"
    
    print("NORAD Schedule Scraper")
    print("=" * 50)
    
    url = get_schedule_url(LEAGUE_ID, season)
    
    if not url:
        print("\nTo use this script:")
        print("1. Go to noradhockey.com and view your league schedule")
        print("2. Copy the league_id from the URL")
        print("3. Edit this script and set LEAGUE_ID")
        print("\nExample URL: https://www.noradhockey.com/schedule/list/league_id/12345")
        print("             Your league_id would be: 12345")
        sys.exit(1)
    
    print(f"Fetching: {url}")
    
    html = fetch_page(url)
    if not html:
        print("Failed to fetch schedule")
        sys.exit(1)
    
    games = parse_schedule(html)
    
    if not games:
        print("No games found. The HTML structure may have changed.")
        print("You may need to adjust the parse_schedule() function.")
        sys.exit(1)
    
    display_games(games)
    
    if add_mode:
        print("\nAdding to Supabase...")
        add_to_supabase(games)
    else:
        print("\nTo add these to Supabase, run:")
        print("  python3 src/norad_schedule.py --add")


if __name__ == "__main__":
    main()
