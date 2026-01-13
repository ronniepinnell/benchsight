"""
Goalie Stats Builder

Builds fact_goalie_game_stats table from tracking data.
Extracted from core_facts.py for better organization and testability.

Version: 29.4
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from src.core.table_writer import save_output_table

# Import the original function from core_facts
# We'll refactor this later to extract calculation logic
from src.tables.core_facts import _create_fact_goalie_game_stats_original

OUTPUT_DIR = Path('data/output')


class GoalieStatsBuilder:
    """
    Builder for fact_goalie_game_stats table.
    
    Creates comprehensive goalie game statistics with advanced metrics.
    Currently wraps the existing create_fact_goalie_game_stats function.
    Future refactoring will extract calculation logic into separate methods.
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
        Build the complete fact_goalie_game_stats table.
        
        Args:
            save: Whether to save the table (default: True)
            
        Returns:
            DataFrame with goalie game stats
        """
        # For now, delegate to the original function
        # Future: Extract calculation logic into builder methods
        df = _create_fact_goalie_game_stats_original()
        
        # Save if requested (the original function saves by default, so we need to handle this)
        if save and len(df) > 0:
            save_output_table(df, 'fact_goalie_game_stats', self.output_dir)
        
        return df


def build_fact_goalie_game_stats(output_dir: Path = None, save: bool = True) -> pd.DataFrame:
    """
    Convenience function to build fact_goalie_game_stats.
    
    Args:
        output_dir: Path to output directory (default: data/output)
        save: Whether to save the table (default: True)
        
    Returns:
        DataFrame with goalie game stats
    """
    builder = GoalieStatsBuilder(output_dir=output_dir)
    return builder.build(save=save)
