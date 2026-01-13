"""
Team Stats Builder

Builds fact_team_game_stats table by aggregating player stats.
Extracted from core_facts.py for better organization and testability.

Version: 29.4
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from src.core.table_writer import save_output_table

# Import utility functions from core_facts
from src.tables.core_facts import load_table

OUTPUT_DIR = Path('data/output')


class TeamStatsBuilder:
    """
    Builder for fact_team_game_stats table.
    
    Aggregates player game stats to create team-level statistics.
    """
    
    def __init__(self, output_dir: Path = None):
        """
        Initialize the builder.
        
        Args:
            output_dir: Path to output directory (default: data/output)
        """
        self.output_dir = output_dir or OUTPUT_DIR
    
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
                
                # Sum columns (aggregate from players)
                sum_cols = [
                    'goals', 'assists', 'points', 'shots', 'sog', 
                    'giveaways', 'takeaways', 'blocks', 'hits', 
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
