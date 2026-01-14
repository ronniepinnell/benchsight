"""
Player Stats Builder

Builds fact_player_game_stats table from tracking data.
Extracted from core_facts.py for better organization and testability.

Version: 29.4
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from src.formulas.formula_applier import apply_player_stats_formulas
from src.core.table_writer import save_output_table

# Import calculation functions from core_facts
from src.tables.core_facts import (
    get_game_ids, get_players_in_game,
    calculate_player_event_stats, calculate_player_shift_stats,
    calculate_advanced_shift_stats, calculate_zone_entry_exit_stats,
    calculate_possession_time_by_zone, calculate_faceoff_zone_stats, calculate_wdbe_faceoffs, calculate_period_splits,
    calculate_danger_zone_stats, calculate_rush_stats,
    calculate_micro_stats, calculate_advanced_micro_stats, calculate_xg_stats,
    calculate_strength_splits, calculate_shot_type_stats,
    calculate_pass_type_stats, calculate_playmaking_stats,
    calculate_pressure_stats, calculate_competition_tier_stats,
    calculate_game_state_stats, calculate_linemate_stats,
    calculate_time_bucket_stats, calculate_rebound_stats,
    calculate_game_score, calculate_war_stats,
    calculate_performance_vs_rating, calculate_relative_stats,
    calculate_ratings_adjusted_stats,
    load_table
)

OUTPUT_DIR = Path('data/output')


class PlayerStatsBuilder:
    """
    Builder for fact_player_game_stats table.
    
    Creates comprehensive player game statistics for skaters (excludes goalies).
    Includes event stats, shift stats, advanced metrics, and formula-based calculations.
    """
    
    def __init__(self, output_dir: Path = None):
        """
        Initialize the builder.
        
        Args:
            output_dir: Path to output directory (default: data/output)
        """
        self.output_dir = output_dir or OUTPUT_DIR
        self._data_cache = {}
    
    def load_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all required input tables.
        
        Returns:
            Dict mapping table names to DataFrames
        """
        return {
            'event_players': load_table('fact_event_players'),
            'events': load_table('fact_events'),
            'shifts': load_table('fact_shifts'),
            'shift_players': load_table('fact_shift_players'),
            'roster': load_table('fact_gameroster'),
            'players': load_table('dim_player'),
            'schedule': load_table('dim_schedule'),
            'zone_entry_types': load_table('dim_zone_entry_type'),
            'zone_exit_types': load_table('dim_zone_exit_type'),
            'registration': load_table('fact_registration'),
        }
    
    def validate_data(self, data: Dict[str, pd.DataFrame]) -> bool:
        """
        Validate that required data is present.
        
        Args:
            data: Dict of loaded tables
            
        Returns:
            True if data is valid, False otherwise
        """
        if len(data['event_players']) == 0:
            print("  ERROR: fact_event_players not found!")
            return False
        return True
    
    def build_player_stats(self, 
                          player_id: str,
                          game_id: int,
                          data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Build stats for a single player in a single game.
        
        Args:
            player_id: Player ID
            game_id: Game ID
            data: Dict of loaded tables
            
        Returns:
            Dict of player stats
        """
        roster = data['roster']
        players = data['players']
        schedule = data['schedule']
        registration = data['registration']
        event_players = data['event_players']
        events = data['events']
        shifts = data['shifts']
        shift_players = data['shift_players']
        zone_entry_types = data['zone_entry_types']
        zone_exit_types = data['zone_exit_types']
        
        # Get team info
        team_id = ''
        team_name = ''
        position = ''
        if len(roster) > 0:
            player_roster = roster[(roster['game_id'] == game_id) & (roster['player_id'] == player_id)]
            if len(player_roster) > 0:
                team_id = player_roster['team_id'].values[0] if 'team_id' in player_roster.columns else ''
                team_name = player_roster['team_name'].values[0] if 'team_name' in player_roster.columns else ''
                position = player_roster['player_position'].values[0] if 'player_position' in player_roster.columns else ''
        
        # Initialize stats dict
        stats = {
            'player_game_key': f"p{game_id}{team_id}{player_id}",
            'player_game_id': f"pg{game_id}{team_id}{player_id}",
            'game_id': game_id,
            'player_id': player_id,
            'team_id': team_id,
            'team_name': team_name,
            'position': position,
            '_export_timestamp': datetime.now().isoformat(),
        }
        
        # Player info
        if len(players) > 0:
            player_info = players[players['player_id'] == player_id]
            stats['player_name'] = player_info['player_full_name'].values[0] if len(player_info) > 0 and 'player_full_name' in player_info.columns else ''
        else:
            stats['player_name'] = ''
        
        # Season info
        if len(schedule) > 0:
            game_info = schedule[schedule['game_id'] == game_id]
            stats['season_id'] = game_info['season_id'].values[0] if len(game_info) > 0 and 'season_id' in game_info.columns else None
        
        # Player rating
        player_rating = 4.0
        if len(registration) > 0:
            reg = registration[registration['player_id'] == player_id]
            if len(reg) > 0 and 'skill_rating' in reg.columns:
                val = reg['skill_rating'].values[0]
                if pd.notna(val):
                    player_rating = float(val)
        
        # All stat calculations
        stats.update(calculate_player_event_stats(player_id, game_id, event_players, events))
        stats.update(calculate_player_shift_stats(player_id, game_id, shifts, shift_players))
        stats.update(calculate_advanced_shift_stats(player_id, game_id, shift_players))
        stats.update(calculate_zone_entry_exit_stats(player_id, game_id, event_players, zone_entry_types, zone_exit_types, events))
        stats.update(calculate_possession_time_by_zone(player_id, game_id, event_players, events))
        stats.update(calculate_faceoff_zone_stats(player_id, game_id, event_players))
        stats.update(calculate_wdbe_faceoffs(player_id, game_id, event_players, events))
        stats.update(calculate_period_splits(player_id, game_id, event_players, shift_players))
        stats.update(calculate_danger_zone_stats(player_id, game_id, event_players, events))
        stats.update(calculate_rush_stats(player_id, game_id, event_players, events))
        
        # Calculate micro stats and advanced micro stats
        micro_stats = calculate_micro_stats(player_id, game_id, event_players, events)
        stats.update(micro_stats)
        
        # Get zone stats for advanced micro stats
        zone_entry_types = data.get('zone_entry_types', pd.DataFrame())
        zone_exit_types = data.get('zone_exit_types', pd.DataFrame())
        zone_stats = calculate_zone_entry_exit_stats(player_id, game_id, event_players, zone_entry_types, zone_exit_types, events)
        
        # Calculate advanced composite micro stats
        advanced_micro = calculate_advanced_micro_stats(player_id, game_id, event_players, events, micro_stats, zone_stats)
        stats.update(advanced_micro)
        
        stats.update(calculate_xg_stats(player_id, game_id, event_players, events))
        
        # v25.2 stats
        stats.update(calculate_strength_splits(player_id, game_id, event_players, shift_players, events))
        stats.update(calculate_shot_type_stats(player_id, game_id, event_players, events))
        stats.update(calculate_pass_type_stats(player_id, game_id, event_players, events))
        stats.update(calculate_playmaking_stats(player_id, game_id, event_players, events))
        stats.update(calculate_pressure_stats(player_id, game_id, event_players, events))
        stats.update(calculate_competition_tier_stats(player_id, game_id, shift_players))
        stats.update(calculate_game_state_stats(player_id, game_id, shift_players, events))
        
        # Phase 3 stats (v26.1)
        stats.update(calculate_linemate_stats(player_id, game_id, shift_players))
        stats.update(calculate_time_bucket_stats(player_id, game_id, event_players, events, shift_players))
        stats.update(calculate_rebound_stats(player_id, game_id, event_players, events))
        
        # Composite stats (game score, WAR, etc.)
        stats.update(calculate_game_score(stats))
        stats.update(calculate_war_stats(stats))
        stats.update(calculate_performance_vs_rating(stats, player_rating))
        stats.update(calculate_relative_stats(stats))
        
        # Ratings-adjusted stats (NEW)
        stats.update(calculate_ratings_adjusted_stats(player_id, game_id, shift_players, stats))
        
        return stats
    
    def build(self, save: bool = True) -> pd.DataFrame:
        """
        Build the complete fact_player_game_stats table.
        
        Args:
            save: Whether to save the table (default: True)
            
        Returns:
            DataFrame with player game stats
        """
        print("\nBuilding fact_player_game_stats (v29.4 - Builder Pattern, SKATERS ONLY)...")
        
        # Load data
        data = self.load_data()
        
        # Validate
        if not self.validate_data(data):
            return pd.DataFrame()
        
        # Get game IDs
        game_ids = get_game_ids()
        print(f"  Processing {len(game_ids)} games: {sorted(game_ids)}")
        
        all_stats = []
        
        # Process each game
        for game_id in game_ids:
            if game_id == 99999:
                continue
            
            # Get players in game (excludes goalies)
            player_ids = get_players_in_game(game_id, data['event_players'], data['roster'])
            
            # Process each player
            for player_id in player_ids:
                if pd.isna(player_id) or str(player_id) in ['nan', '', 'None']:
                    continue
                
                stats = self.build_player_stats(player_id, game_id, data)
                all_stats.append(stats)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_stats)
        
        # Apply formula system (replaces calculate_rate_stats and other hardcoded formulas)
        if len(df) > 0:
            # Ensure toi_minutes exists for per-60 formulas
            if 'toi_minutes' not in df.columns and 'toi_seconds' in df.columns:
                df['toi_minutes'] = df['toi_seconds'] / 60.0
            
            # Apply all formulas from registry
            df = apply_player_stats_formulas(df)
            
            # Reorder columns
            key_cols = ['player_game_key', 'player_game_id', 'game_id', 'season_id', 
                       'player_id', 'player_name', 'team_id', 'team_name', 'position']
            other_cols = [c for c in df.columns if c not in key_cols]
            df = df[[c for c in key_cols if c in df.columns] + other_cols]
        
        print(f"  Created {len(df)} SKATER records with {len(df.columns)} columns")
        
        # Save if requested
        if save and len(df) > 0:
            save_output_table(df, 'fact_player_game_stats', self.output_dir)
        
        return df


def build_fact_player_game_stats(output_dir: Path = None, save: bool = True) -> pd.DataFrame:
    """
    Convenience function to build fact_player_game_stats.
    
    Args:
        output_dir: Path to output directory (default: data/output)
        save: Whether to save the table (default: True)
        
    Returns:
        DataFrame with player game stats
    """
    builder = PlayerStatsBuilder(output_dir=output_dir)
    return builder.build(save=save)
