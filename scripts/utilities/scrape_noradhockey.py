#!/usr/bin/env python3
"""
NORAD Hockey Website Scraper
============================
Scrapes game scores from noradhockey.com to verify ETL goal counts.

This is the LIVE SOURCE OF TRUTH for goal counts.
If ETL output doesn't match the website, the ETL is wrong.

Usage:
    from scripts.utilities.scrape_noradhockey import get_game_scores
    scores = get_game_scores()
    # Returns: {18969: 7, 18977: 6, 18981: 3, 18987: 1, ...}
"""

import re
import urllib.request
import urllib.error
from typing import Dict, Optional, Tuple
import ssl

# Game IDs we're tracking (update when new games added)
TRACKED_GAMES = [18969, 18977, 18981, 18987]

def fetch_noradhockey_homepage() -> Optional[str]:
    """Fetch the noradhockey.com homepage HTML."""
    url = "https://www.noradhockey.com/"
    
    try:
        # Create SSL context that doesn't verify (some environments have cert issues)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; BenchSight/1.0)'}
        )
        
        with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
            return response.read().decode('utf-8')
            
    except urllib.error.URLError as e:
        print(f"  ⚠ Could not fetch noradhockey.com: {e}")
        return None
    except Exception as e:
        print(f"  ⚠ Error fetching website: {e}")
        return None


def parse_game_scores(html: str) -> Dict[int, dict]:
    """
    Parse game scores from the homepage HTML.
    
    Returns dict like:
    {
        18969: {'home': 'Platinum Group', 'away': 'COS Velodrome', 'home_score': 4, 'away_score': 3, 'total_goals': 7},
        ...
    }
    """
    games = {}
    
    # Pattern to find game links and scores in the "Previous Game" table
    # Format: [Date](url) [score](url) N/A [Teams](url)
    # Example: /event/18969/) [4 - 3]
    
    # Find all event links with scores
    # Pattern matches: /event/XXXXX/) [X - Y]
    pattern = r'/event/(\d+)/["\'][^>]*>.*?(\d+)\s*-\s*(\d+)'
    
    matches = re.findall(pattern, html, re.DOTALL)
    
    for match in matches:
        try:
            game_id = int(match[0])
            score1 = int(match[1])
            score2 = int(match[2])
            total_goals = score1 + score2
            
            games[game_id] = {
                'home_score': score1,
                'away_score': score2,
                'total_goals': total_goals
            }
        except (ValueError, IndexError):
            continue
    
    # Alternative pattern for different HTML structure
    # [October 5, 2025](url) [0 - 1](url) N/A [OUTCAN Outlaws vs COS Velodrome](url)
    alt_pattern = r'event/(\d+)/[^>]*>\s*\[?(\d+)\s*-\s*(\d+)\]?'
    alt_matches = re.findall(alt_pattern, html)
    
    for match in alt_matches:
        try:
            game_id = int(match[0])
            if game_id not in games:
                score1 = int(match[1])
                score2 = int(match[2])
                games[game_id] = {
                    'home_score': score1,
                    'away_score': score2,
                    'total_goals': score1 + score2
                }
        except (ValueError, IndexError):
            continue
    
    return games


def get_game_scores(game_ids: list = None) -> Dict[int, int]:
    """
    Get total goals for specified games from noradhockey.com.
    
    Args:
        game_ids: List of game IDs to get scores for. Default: TRACKED_GAMES
        
    Returns:
        Dict mapping game_id -> total_goals
        e.g., {18969: 7, 18977: 6, 18981: 3, 18987: 1}
    """
    if game_ids is None:
        game_ids = TRACKED_GAMES
    
    html = fetch_noradhockey_homepage()
    if html is None:
        return {}
    
    all_games = parse_game_scores(html)
    
    # Filter to only requested games
    result = {}
    for gid in game_ids:
        if gid in all_games:
            result[gid] = all_games[gid]['total_goals']
    
    return result


def get_all_game_scores() -> Dict[int, dict]:
    """Get detailed scores for ALL games on the website."""
    html = fetch_noradhockey_homepage()
    if html is None:
        return {}
    return parse_game_scores(html)


def verify_against_website(etl_goals: Dict[int, int]) -> Tuple[bool, str]:
    """
    Verify ETL goal counts against website.
    
    Args:
        etl_goals: Dict of game_id -> goal_count from ETL output
        
    Returns:
        (passed: bool, message: str)
    """
    print("  Fetching live scores from noradhockey.com...")
    website_goals = get_game_scores(list(etl_goals.keys()))
    
    if not website_goals:
        return True, "⚠ Could not verify (website unavailable)"
    
    errors = []
    for game_id, etl_count in etl_goals.items():
        if game_id in website_goals:
            website_count = website_goals[game_id]
            if etl_count != website_count:
                errors.append(f"Game {game_id}: ETL={etl_count}, Website={website_count}")
    
    if errors:
        return False, "Goal count mismatch:\n    " + "\n    ".join(errors)
    
    verified_count = len([g for g in etl_goals if g in website_goals])
    return True, f"✓ {verified_count} games verified against noradhockey.com"


# Quick test
if __name__ == "__main__":
    print("Testing noradhockey.com scraper...")
    print()
    
    scores = get_game_scores()
    
    if scores:
        print("Game scores from website:")
        total = 0
        for game_id in sorted(scores.keys()):
            goals = scores[game_id]
            total += goals
            print(f"  Game {game_id}: {goals} goals")
        print(f"  Total: {total} goals")
    else:
        print("Could not fetch scores from website")
    
    print()
    print("Testing verification...")
    test_etl = {18969: 7, 18977: 6, 18981: 3, 18987: 1}
    passed, msg = verify_against_website(test_etl)
    print(f"  Passed: {passed}")
    print(f"  {msg}")
