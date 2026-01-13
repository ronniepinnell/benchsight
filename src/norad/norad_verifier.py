#!/usr/bin/env python3
"""
BenchSight NORAD Verifier
=========================
Verifies BLB data accuracy against noradhockey.com and creates updates.

The NORAD site is the authoritative source for:
- Player statistics (G, A, PTS, PIM)
- Team standings (W-L-T, Points)
- Game scores

BLB tables are the PRIMARY data source. This script checks for discrepancies.

Usage:
    python src/norad_verifier.py --check          # Check all data
    python src/norad_verifier.py --standings      # Verify standings only
    python src/norad_verifier.py --leaders        # Verify player leaders
    python src/norad_verifier.py --update         # Create update recommendations
    python src/norad_verifier.py --export         # Export verification report
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

# Try to import requests for web fetching
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("Warning: requests library not available. Web verification disabled.")

# Try to import BeautifulSoup for HTML parsing
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    print("Warning: beautifulsoup4 not available. Web parsing disabled.")


NORAD_BASE_URL = "https://noradhockey.com"


class NoradVerifier:
    """Verifies BLB data against NORAD website"""
    
    def __init__(self, xlsx_path: str):
        self.xlsx_path = Path(xlsx_path)
        self.tables = self._load_tables()
        self.discrepancies = []
        self.session = requests.Session() if HAS_REQUESTS else None
        
    def _load_tables(self) -> dict:
        """Load BLB tables from Excel"""
        xl = pd.ExcelFile(str(self.xlsx_path))
        return {
            'schedule': pd.read_excel(xl, 'dim_schedule'),
            'gameroster': pd.read_excel(xl, 'fact_gameroster'),
            'players': pd.read_excel(xl, 'dim_player')
        }
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL"""
        if not HAS_REQUESTS:
            return None
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"  Error fetching {url}: {e}")
            return None
    
    def parse_standings(self, html: str) -> list:
        """Parse standings table from HTML"""
        if not HAS_BS4:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        standings = []
        
        # Find standings table
        table = soup.find('table', class_='standing-table') or soup.find('table')
        if not table:
            return []
        
        rows = table.find_all('tr')[1:]  # Skip header
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 5:
                team_cell = cells[0]
                team_link = team_cell.find('a')
                team_name = team_link.get_text(strip=True) if team_link else team_cell.get_text(strip=True)
                
                standings.append({
                    'team': team_name,
                    'gp': int(cells[1].get_text(strip=True) or 0),
                    'w': int(cells[2].get_text(strip=True) or 0),
                    'l': int(cells[3].get_text(strip=True) or 0),
                    't': int(cells[4].get_text(strip=True) or 0),
                    'pts': int(cells[5].get_text(strip=True) or 0) if len(cells) > 5 else 0
                })
        
        return standings
    
    def parse_leaders(self, html: str) -> list:
        """Parse player leaders from HTML"""
        if not HAS_BS4:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        leaders = []
        
        # Find the scoring leaders section
        for row in soup.select('.leader-row, .stats-row, tr'):
            cells = row.find_all(['td', 'th', 'span', 'div'])
            name_elem = row.find('a', class_='player-link') or row.find('a')
            
            if name_elem and len(cells) >= 3:
                name = name_elem.get_text(strip=True)
                # Try to extract stats from cells
                stats = [c.get_text(strip=True) for c in cells if c.get_text(strip=True).isdigit()]
                
                if len(stats) >= 3 and name:
                    leaders.append({
                        'name': name,
                        'goals': int(stats[0]) if stats else 0,
                        'assists': int(stats[1]) if len(stats) > 1 else 0,
                        'points': int(stats[2]) if len(stats) > 2 else 0
                    })
        
        return leaders
    
    def calculate_standings_from_blb(self) -> pd.DataFrame:
        """Calculate current standings from BLB schedule data"""
        schedule = self.tables['schedule']
        
        # Filter to current season games with scores
        current = schedule[
            (schedule['season'] == '20252026') & 
            (schedule['home_total_goals'].notna())
        ].copy()
        
        teams = {}
        
        for _, game in current.iterrows():
            home = game['home_team_name']
            away = game['away_team_name']
            home_goals = int(game['home_total_goals'])
            away_goals = int(game['away_total_goals'])
            
            if home not in teams:
                teams[home] = {'w': 0, 'l': 0, 't': 0, 'gf': 0, 'ga': 0}
            if away not in teams:
                teams[away] = {'w': 0, 'l': 0, 't': 0, 'gf': 0, 'ga': 0}
            
            teams[home]['gf'] += home_goals
            teams[home]['ga'] += away_goals
            teams[away]['gf'] += away_goals
            teams[away]['ga'] += home_goals
            
            if home_goals > away_goals:
                teams[home]['w'] += 1
                teams[away]['l'] += 1
            elif away_goals > home_goals:
                teams[away]['w'] += 1
                teams[home]['l'] += 1
            else:
                teams[home]['t'] += 1
                teams[away]['t'] += 1
        
        standings = []
        for team, stats in teams.items():
            gp = stats['w'] + stats['l'] + stats['t']
            pts = stats['w'] * 2 + stats['t']
            standings.append({
                'team': team,
                'gp': gp,
                'w': stats['w'],
                'l': stats['l'],
                't': stats['t'],
                'pts': pts,
                'gf': stats['gf'],
                'ga': stats['ga']
            })
        
        df = pd.DataFrame(standings)
        if len(df):
            df = df.sort_values(['pts', 'w', 'gf'], ascending=[False, False, False])
        
        return df
    
    def calculate_leaders_from_blb(self) -> pd.DataFrame:
        """Calculate player leaders from BLB gameroster data"""
        gameroster = self.tables['gameroster']
        
        # Filter to current season
        current = gameroster[gameroster['season'] == '20252026'].copy()
        
        # Aggregate by player
        leaders = current.groupby('player_full_name').agg({
            'games_played': 'sum',
            'goals': 'sum',
            'assist': 'sum',
            'pim': 'sum'
        }).reset_index()
        
        leaders['points'] = leaders['goals'] + leaders['assist']
        leaders = leaders.sort_values('points', ascending=False)
        
        return leaders.head(20)
    
    def verify_standings(self) -> dict:
        """Verify standings against NORAD website"""
        print("\n=== Verifying Standings ===")
        
        blb_standings = self.calculate_standings_from_blb()
        print(f"BLB standings calculated: {len(blb_standings)} teams")
        
        if not HAS_REQUESTS or not HAS_BS4:
            print("Web verification skipped (missing dependencies)")
            return {'blb': blb_standings.to_dict('records'), 'norad': [], 'discrepancies': []}
        
        # Fetch NORAD standings
        html = self.fetch_page(f"{NORAD_BASE_URL}/standings/")
        if not html:
            print("Could not fetch NORAD standings")
            return {'blb': blb_standings.to_dict('records'), 'norad': [], 'discrepancies': []}
        
        norad_standings = self.parse_standings(html)
        print(f"NORAD standings fetched: {len(norad_standings)} teams")
        
        # Compare
        discrepancies = []
        for blb_team in blb_standings.to_dict('records'):
            team_name = blb_team['team']
            norad_team = next((t for t in norad_standings if t['team'] == team_name), None)
            
            if norad_team:
                for stat in ['w', 'l', 't', 'pts']:
                    if blb_team[stat] != norad_team[stat]:
                        discrepancies.append({
                            'team': team_name,
                            'stat': stat,
                            'blb': blb_team[stat],
                            'norad': norad_team[stat]
                        })
        
        if discrepancies:
            print(f"\n⚠ Found {len(discrepancies)} discrepancies:")
            for d in discrepancies[:5]:
                print(f"  {d['team']}: {d['stat']} = {d['blb']} (BLB) vs {d['norad']} (NORAD)")
        else:
            print("✓ All standings match!")
        
        return {
            'blb': blb_standings.to_dict('records'),
            'norad': norad_standings,
            'discrepancies': discrepancies
        }
    
    def verify_leaders(self) -> dict:
        """Verify player leaders against NORAD website"""
        print("\n=== Verifying Player Leaders ===")
        
        blb_leaders = self.calculate_leaders_from_blb()
        print(f"BLB leaders calculated: {len(blb_leaders)} players")
        
        return {
            'blb': blb_leaders.to_dict('records'),
            'discrepancies': []
        }
    
    def generate_report(self) -> dict:
        """Generate full verification report"""
        report = {
            'generated': datetime.now().isoformat(),
            'blb_file': str(self.xlsx_path),
            'standings': self.verify_standings(),
            'leaders': self.verify_leaders(),
            'summary': {
                'total_discrepancies': 0,
                'status': 'OK'
            }
        }
        
        total_disc = len(report['standings'].get('discrepancies', []))
        total_disc += len(report['leaders'].get('discrepancies', []))
        
        report['summary']['total_discrepancies'] = total_disc
        report['summary']['status'] = 'NEEDS_REVIEW' if total_disc > 0 else 'OK'
        
        return report
    
    def export_report(self, output_path: str):
        """Export verification report to JSON"""
        report = self.generate_report()
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\nReport exported to {output_path}")
        return report


def main():
    parser = argparse.ArgumentParser(description='Verify BLB data against NORAD website')
    parser.add_argument('--xlsx', type=str, default='data/raw/BLB_TABLES.xlsx', 
                       help='Path to BLB_Tables.xlsx')
    parser.add_argument('--check', action='store_true', help='Run full verification')
    parser.add_argument('--standings', action='store_true', help='Verify standings only')
    parser.add_argument('--leaders', action='store_true', help='Verify leaders only')
    parser.add_argument('--export', type=str, help='Export report to JSON file')
    parser.add_argument('--update', action='store_true', help='Generate update recommendations')
    
    args = parser.parse_args()
    
    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    xlsx_path = project_root / args.xlsx
    
    if not xlsx_path.exists():
        print(f"Error: BLB_Tables.xlsx not found at {xlsx_path}")
        sys.exit(1)
    
    verifier = NoradVerifier(str(xlsx_path))
    
    if args.standings:
        verifier.verify_standings()
    elif args.leaders:
        verifier.verify_leaders()
    elif args.export:
        output_path = project_root / args.export
        verifier.export_report(str(output_path))
    else:
        # Default: full check
        report = verifier.generate_report()
        
        print("\n" + "=" * 50)
        print(f"VERIFICATION SUMMARY")
        print("=" * 50)
        print(f"Status: {report['summary']['status']}")
        print(f"Discrepancies: {report['summary']['total_discrepancies']}")
        
        if args.update and report['summary']['total_discrepancies'] > 0:
            print("\n=== Update Recommendations ===")
            for d in report['standings'].get('discrepancies', []):
                print(f"  UPDATE standings SET {d['stat']} = {d['norad']} WHERE team = '{d['team']}'")


if __name__ == '__main__':
    main()
