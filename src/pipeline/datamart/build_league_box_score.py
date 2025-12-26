"""
=============================================================================
DATAMART: BUILD LEAGUE BOX SCORE
=============================================================================
File: src/pipeline/datamart/build_league_box_score.py

PURPOSE:
    Create simplified box score from league stats (fact_gameroster)
    for games without tracking data.

=============================================================================
"""

import pandas as pd

from src.database.table_operations import (
    table_exists,
    read_query,
    load_dataframe_to_table
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def build_league_box_score(game_id: int) -> int:
    """
    Build box score from league-provided stats.
    
    WHY THIS FUNCTION:
        Not all games have tracking files.
        Basic stats are available in fact_gameroster.
    
    Args:
        game_id: Game identifier.
    
    Returns:
        Number of rows added.
    """
    logger.info(f"Building league box score for game {game_id}")
    
    # Check if game exists in gameroster
    if not table_exists('fact_gameroster'):
        raise RuntimeError("fact_gameroster not found. Run BLB pipeline first.")
    
    # Get roster data for this game
    roster = read_query(f"""
        SELECT 
            player_game_key,
            player_game_number,
            player_id,
            player_full_name,
            display_name,
            team_name AS player_team,
            team_venue AS player_venue,
            player_position AS position,
            skill_rating,
            {game_id} AS game_id,
            goals,
            assists,
            goals + assists AS points,
            plus_minus,
            penalty_minutes,
            goals_against,
            saves,
            0 AS is_tracked
        FROM fact_gameroster
        WHERE game_id = {game_id}
    """)
    
    if len(roster) == 0:
        logger.warning(f"No roster data found for game {game_id}")
        return 0
    
    # Add to fact_box_score
    if not table_exists('fact_box_score'):
        load_dataframe_to_table(roster, 'fact_box_score', 'replace')
        return len(roster)
    
    # Append
    existing = read_query("SELECT * FROM fact_box_score")
    existing = existing[existing['game_id'] != game_id]
    
    combined = pd.concat([existing, roster], ignore_index=True)
    load_dataframe_to_table(combined, 'fact_box_score', 'replace')
    
    logger.info(f"Added {len(roster)} league stats rows for game {game_id}")
    return len(roster)
