"""
Team Stats Builder

Builds fact_team_game_stats table by aggregating player stats AND calculating
directly from events for accuracy (shots, giveaways, takeaways, blocks).

Extracted from core_facts.py for better organization and testability.

Version: 29.5 - Fixed team stats to calculate from events directly
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict
from src.calculations.goals import get_goal_filter
from src.core.table_writer import save_output_table

# Import utility functions from core_facts
from src.tables.core_facts import load_table

OUTPUT_DIR = Path('data/output')


class TeamStatsBuilder:
    """
    Builder for fact_team_game_stats table.
    
    Calculates team-level statistics by:
    1. Computing critical stats directly from events (shots, giveaways, takeaways, blocks, hits, goals)
       - This ensures accuracy because summing player stats can miss events where players
         aren't the primary actor (event_player_1)
    2. Aggregating other stats from player game stats where summing is accurate
       (assists, TOI, advanced metrics, etc.)
    
    Version 29.5 Fix:
    - Previous version summed ALL stats from player_game_stats, causing inaccuracies
    - Shots/Blocks/Giveaways/Takeaways now calculated from events directly
    - Goals now from events (was already mostly accurate but ensures consistency)
    """
    
    def __init__(self, output_dir: Path = None):
        """
        Initialize the builder.
        
        Args:
            output_dir: Path to output directory (default: data/output)
        """
        self.output_dir = output_dir or OUTPUT_DIR
    
    def calculate_team_stats_from_events(self, game_id: int, team_id: str, 
                                         events: pd.DataFrame, 
                                         event_players: pd.DataFrame,
                                         schedule: pd.DataFrame) -> Dict:
        """
        Calculate team stats directly from events for accuracy.
        
        This is critical because summing player stats can miss events where
        players aren't the primary actor (event_player_1).
        
        Args:
            game_id: Game ID
            team_id: Team ID
            events: fact_events DataFrame
            event_players: fact_event_players DataFrame
            schedule: dim_schedule DataFrame (for home/away identification)
            
        Returns:
            Dict with team stats calculated from events
        """
        stats = {}
        
        # Get game events
        game_events = events[events['game_id'] == game_id] if len(events) > 0 else pd.DataFrame()
        if len(game_events) == 0:
            return stats
        
        # Determine if team is home or away
        is_home = False
        if len(schedule) > 0:
            game_info = schedule[schedule['game_id'] == game_id]
            if len(game_info) > 0:
                home_team_id = game_info['home_team_id'].values[0] if 'home_team_id' in game_info.columns else None
                away_team_id = game_info['away_team_id'].values[0] if 'away_team_id' in game_info.columns else None
                is_home = (home_team_id == team_id) if home_team_id is not None else False
        
        # Identify team events - events "owned" by this team
        # An event is owned by a team if any player from that team is event_player_1
        team_event_mask = pd.Series([False] * len(game_events), index=game_events.index)
        
        # Method 1: Use event_players to find events where team has event_player_1
        if len(event_players) > 0:
            # Use player_team_id (actual column name) instead of team_id
            team_col = 'player_team_id' if 'player_team_id' in event_players.columns else 'team_id'
            team_primary_player_events = event_players[
                (event_players['game_id'] == game_id) &
                (event_players[team_col] == team_id) &
                (event_players['player_role'].astype(str).str.lower() == 'event_player_1')
            ]
            team_event_ids = team_primary_player_events['event_id'].unique()
            team_event_mask = game_events['event_id'].isin(team_event_ids)
        # Method 2: Fallback - use event_team_id if available
        elif 'event_team_id' in game_events.columns:
            team_event_mask = game_events['event_team_id'] == team_id
        # Method 3: Fallback - use team_venue if available
        elif 'team_venue' in game_events.columns:
            venue_filter = 'Home' if is_home else 'Away'
            team_event_mask = game_events['team_venue'] == venue_filter
        
        team_events = game_events[team_event_mask]
        
        if len(team_events) == 0:
            return stats
        
        # Ensure period column exists
        if 'period' not in team_events.columns:
            # Try to get period from event_players
            if len(event_players) > 0:
                team_event_ids = team_events['event_id'].unique()
                period_map = event_players[
                    event_players['event_id'].isin(team_event_ids)
                ].drop_duplicates(subset='event_id')[['event_id', 'period']].set_index('event_id')['period'].to_dict()
                team_events['period'] = team_events['event_id'].map(period_map)
            else:
                team_events['period'] = None
        
        # ========================================
        # SHOTS - Count ALL shot attempts (excluding goals to avoid double-counting)
        # Goals are tracked separately, Shot_Goal events count as shots AND goals
        # ========================================
        # Count shot events (including Shot_Goal which is a shot that scored)
        shot_events = team_events[team_events['event_type'].astype(str).str.lower() == 'shot']
        stats['shots'] = len(shot_events)
        
        # Shots on goal: event_detail contains 'onnet' or 'saved', plus goals from Shot_Goal
        sog_mask = shot_events['event_detail'].astype(str).str.lower().str.contains('onnet|saved|goal', na=False, regex=True)
        stats['sog'] = int(sog_mask.sum())
        
        # ========================================
        # GOALS - Count all goals by the team
        # Per CLAUDE.md: event_type='Goal' AND event_detail='Goal_Scored' ONLY
        # ========================================
        goal_events = team_events[get_goal_filter(team_events)]
        stats['goals'] = goal_events['event_id'].nunique() if len(goal_events) > 0 else 0
        
        # ========================================
        # GIVEAWAYS/TAKEAWAYS - Count all turnovers
        # ========================================
        turnovers = team_events[team_events['event_type'].astype(str).str.lower() == 'turnover']
        stats['giveaways'] = int(turnovers[turnovers['event_detail'].astype(str).str.lower().str.contains('giveaway', na=False)].shape[0])
        stats['takeaways'] = int(turnovers[turnovers['event_detail'].astype(str).str.lower().str.contains('takeaway', na=False)].shape[0])
        
        # ========================================
        # BLOCKS - Count all blocks by team players
        # ========================================
        # Blocks are tracked in event_players via play_detail1='BlockedShot'
        # Count all events where any team player has BlockedShot
        if len(event_players) > 0:
            team_event_players = event_players[
                (event_players['game_id'] == game_id) &
                (event_players[team_col] == team_id)
            ]
            if 'play_detail1' in team_event_players.columns:
                blocks_df = team_event_players[
                    team_event_players['play_detail1'].astype(str).str.lower().str.contains('blockedshot', na=False)
                ]
                if len(blocks_df) > 0:
                    # Avoid double-counting linked events
                    if 'linked_event_key' in blocks_df.columns:
                        linked = blocks_df[blocks_df['linked_event_key'].notna()]
                        unlinked = blocks_df[blocks_df['linked_event_key'].isna()]
                        stats['blocks'] = linked['linked_event_key'].nunique() + len(unlinked)
                    else:
                        # Deduplicate by event_id
                        stats['blocks'] = blocks_df['event_id'].nunique()
                else:
                    stats['blocks'] = 0
            else:
                stats['blocks'] = 0
        else:
            stats['blocks'] = 0
        
        # ========================================
        # HITS - Count all hits by the team
        # ========================================
        hits = team_events[team_events['event_type'].astype(str).str.lower() == 'hit']
        stats['hits'] = len(hits)
        
        # ========================================
        # PERIOD BREAKDOWNS - Add period-specific stats
        # ========================================
        for period in [1, 2, 3]:
            period_events = team_events[team_events['period'] == period] if 'period' in team_events.columns else pd.DataFrame()
            
            if len(period_events) == 0:
                # Initialize all period stats to 0
                stats[f'p{period}_shots'] = 0
                stats[f'p{period}_sog'] = 0
                stats[f'p{period}_goals'] = 0
                stats[f'p{period}_giveaways'] = 0
                stats[f'p{period}_takeaways'] = 0
                stats[f'p{period}_blocks'] = 0
                stats[f'p{period}_hits'] = 0
                continue
            
            # Period shots
            period_shots = period_events[period_events['event_type'].astype(str).str.lower() == 'shot']
            stats[f'p{period}_shots'] = len(period_shots)
            
            # Period SOG
            period_sog_mask = period_shots['event_detail'].astype(str).str.lower().str.contains('onnet|saved|goal', na=False, regex=True)
            stats[f'p{period}_sog'] = int(period_sog_mask.sum())
            
            # Period goals - per CLAUDE.md: event_type='Goal' AND event_detail='Goal_Scored' ONLY
            period_goals = period_events[get_goal_filter(period_events)]
            stats[f'p{period}_goals'] = period_goals['event_id'].nunique() if len(period_goals) > 0 else 0
            
            # Period giveaways/takeaways
            period_turnovers = period_events[period_events['event_type'].astype(str).str.lower() == 'turnover']
            stats[f'p{period}_giveaways'] = int(period_turnovers[period_turnovers['event_detail'].astype(str).str.lower().str.contains('giveaway', na=False)].shape[0])
            stats[f'p{period}_takeaways'] = int(period_turnovers[period_turnovers['event_detail'].astype(str).str.lower().str.contains('takeaway', na=False)].shape[0])
            
            # Period blocks (from event_players)
            if len(event_players) > 0:
                period_event_ids = period_events['event_id'].unique()
                period_team_event_players = event_players[
                    (event_players['game_id'] == game_id) &
                    (event_players[team_col] == team_id) &
                    (event_players['event_id'].isin(period_event_ids))
                ]
                if 'play_detail1' in period_team_event_players.columns:
                    period_blocks_df = period_team_event_players[
                        period_team_event_players['play_detail1'].astype(str).str.lower().str.contains('blockedshot', na=False)
                    ]
                    if len(period_blocks_df) > 0:
                        # Deduplicate by event_id
                        stats[f'p{period}_blocks'] = period_blocks_df['event_id'].nunique()
                    else:
                        stats[f'p{period}_blocks'] = 0
                else:
                    stats[f'p{period}_blocks'] = 0
            else:
                stats[f'p{period}_blocks'] = 0
            
            # Period hits
            period_hits = period_events[period_events['event_type'].astype(str).str.lower() == 'hit']
            stats[f'p{period}_hits'] = len(period_hits)
        
        return stats
    
    def build(self, save: bool = True) -> pd.DataFrame:
        """
        Build the complete fact_team_game_stats table.
        
        Args:
            save: Whether to save the table (default: True)
            
        Returns:
            DataFrame with team game stats
        """
        print("\nBuilding fact_team_game_stats...")
        
        pgs = load_table('fact_player_game_stats')
        schedule = load_table('dim_schedule')
        events = load_table('fact_events')
        event_players = load_table('fact_event_players')
        
        if len(pgs) == 0:
            print("  ERROR: fact_player_game_stats not found!")
            return pd.DataFrame()
        
        all_stats = []
        
        # Process each game
        for game_id in pgs['game_id'].unique():
            game_players = pgs[pgs['game_id'] == game_id]
            
            # Process each team in the game
            for team_id in game_players['team_id'].dropna().unique():
                team_players = game_players[game_players['team_id'] == team_id]
                if len(team_players) == 0:
                    continue
                
                stats = {
                    'team_game_key': f"{team_id}_{game_id}",
                    'game_id': game_id,
                    'team_id': team_id
                }
                
                # Season info
                if len(schedule) > 0:
                    game_info = schedule[schedule['game_id'] == game_id]
                    if len(game_info) > 0 and 'season_id' in game_info.columns:
                        stats['season_id'] = game_info['season_id'].values[0]
                
                # Team name
                if 'team_name' in team_players.columns:
                    stats['team_name'] = team_players['team_name'].values[0]
                
                # ========================================
                # CRITICAL: Calculate stats from events directly
                # This fixes accuracy issues with shots, giveaways, takeaways, blocks
                # ========================================
                event_stats = self.calculate_team_stats_from_events(
                    game_id, team_id, events, event_players, schedule
                )
                
                # Override shots, giveaways, takeaways, blocks with event-based calculations
                stats['shots'] = event_stats.get('shots', 0)
                stats['sog'] = event_stats.get('sog', 0)
                stats['goals'] = event_stats.get('goals', 0)
                stats['giveaways'] = event_stats.get('giveaways', 0)
                stats['takeaways'] = event_stats.get('takeaways', 0)
                stats['blocks'] = event_stats.get('blocks', 0)
                stats['hits'] = event_stats.get('hits', 0)
                
                # Sum other columns (aggregate from players) - these are accurate when summed
                # NOTE: shots, sog, goals, giveaways, takeaways, blocks, hits already set from events above
                sum_cols = [
                    'assists', 'points',  # goals/shots/sog already from events
                    # 'giveaways', 'takeaways', 'blocks', 'hits',  # Already from events
                    'toi_seconds', 'corsi_for', 'corsi_against', 
                    'fenwick_for', 'fenwick_against', 'plus_total', 
                    'minus_total', 'xg_for', 'gar_total', 'war', 
                    'shot_assists', 'goal_creating_actions',
                    # Micro stats
                    'dekes', 'drives_total', 'cutbacks', 'delays', 'crash_net', 'screens',
                    'give_and_go', 'second_touch', 'cycles', 'poke_checks', 'stick_checks',
                    'zone_ent_denials', 'backchecks', 'forechecks', 'breakouts', 'dump_ins',
                    'loose_puck_wins', 'puck_recoveries', 'puck_battles_total',
                    'board_battles_won', 'board_battles_lost',
                    'passes_cross_ice', 'passes_stretch', 'passes_breakout', 'passes_rim',
                    'passes_bank', 'passes_royal_road', 'passes_slot', 'passes_behind_net',
                    'shots_one_timer', 'shots_snap', 'shots_wrist', 'shots_slap',
                    'shots_tip', 'shots_deflection', 'shots_wrap_around',
                    'pressure_plays', 'pressure_successful',
                    # Advanced micro stats
                    'possession_quality_index', 'transition_efficiency', 'pressure_index',
                    'offensive_creativity_index', 'defensive_activity_index',
                    'playmaking_quality', 'net_front_presence', 'puck_battles_per_60'
                ]
                
                for col in sum_cols:
                    if col in team_players.columns:
                        # For rate/index metrics, use mean instead of sum
                        if col.endswith('_index') or col.endswith('_rate') or col.endswith('_pct') or col.endswith('_efficiency') or col.endswith('_quality') or col.endswith('_per_60'):
                            stats[col] = round(team_players[col].mean(), 2) if len(team_players) > 0 else 0.0
                        else:
                            stats[col] = team_players[col].sum()
                    else:
                        stats[col] = 0
                
                # Recalculate points based on event-based goals + summed assists
                stats['points'] = stats.get('goals', 0) + stats.get('assists', 0)
                
                # Calculated percentages
                stats['shooting_pct'] = round(
                    stats['goals'] / stats['sog'] * 100, 1
                ) if stats['sog'] > 0 else 0.0
                
                stats['cf_pct'] = round(
                    stats['corsi_for'] / (stats['corsi_for'] + stats['corsi_against']) * 100, 1
                ) if (stats['corsi_for'] + stats['corsi_against']) > 0 else 50.0
                
                stats['plus_minus_total'] = stats['plus_total'] - stats['minus_total']
                
                # Average metrics
                if 'game_score' in team_players.columns:
                    stats['avg_game_score'] = round(team_players['game_score'].mean(), 2)
                
                if 'adjusted_rating' in team_players.columns:
                    stats['avg_adjusted_rating'] = round(team_players['adjusted_rating'].mean(), 1)
                
                all_stats.append(stats)
        
        df = pd.DataFrame(all_stats)
        print(f"  Created {len(df)} team-game records")
        
        # Save if requested
        if save and len(df) > 0:
            save_output_table(df, 'fact_team_game_stats', self.output_dir)
        
        return df


def build_fact_team_game_stats(output_dir: Path = None, save: bool = True) -> pd.DataFrame:
    """
    Convenience function to build fact_team_game_stats.
    
    Args:
        output_dir: Path to output directory (default: data/output)
        save: Whether to save the table (default: True)
        
    Returns:
        DataFrame with team game stats
    """
    builder = TeamStatsBuilder(output_dir=output_dir)
    return builder.build(save=save)
