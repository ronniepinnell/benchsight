#!/usr/bin/env python3
"""
BenchSight Table-by-Table Quality Assurance
============================================

Systematic validation of all 111 tables across 6 dimensions:
1. STRUCTURE  - PKs, FKs, data types, nulls
2. INTEGRITY  - Referential integrity, orphan records
3. ACCURACY   - Values match ground truth (goals, scores)
4. CONSISTENCY - Cross-table alignment
5. COMPLETENESS - Expected data present
6. BUSINESS RULES - Domain-specific validations

Usage:
    python qa_all_tables.py                    # Full QA
    python qa_all_tables.py --table dim_player # Single table
    python qa_all_tables.py --category dims    # All dimensions
    python qa_all_tables.py --report html      # HTML report
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import argparse
import sys

# Configuration
OUTPUT_DIR = Path("data/output")
QA_REPORT_DIR = Path("qa_reports")

# Expected values
EXPECTED_GAMES = [18969, 18977, 18981, 18987]
EXPECTED_GOALS = {18969: 7, 18977: 6, 18981: 3, 18987: 1}
TOTAL_EXPECTED_GOALS = sum(EXPECTED_GOALS.values())  # 17

# ============================================================
# TABLE REGISTRY - All 111 tables with their validation rules
# ============================================================

TABLE_REGISTRY = {
    # ===================
    # DIMENSION TABLES
    # ===================
    "dim_player": {
        "pk": "player_id",
        "required": ["player_id", "player_name"],
        "expected_rows": (100, 500),
        "checks": ["pk_unique", "no_null_pk"]
    },
    "dim_team": {
        "pk": "team_id",
        "required": ["team_id", "team_name"],
        "expected_rows": (10, 50),
        "checks": ["pk_unique", "no_null_pk"]
    },
    "dim_schedule": {
        "pk": "game_id",
        "required": ["game_id", "home_team", "away_team"],
        "expected_rows": (100, 1000),
        "checks": ["pk_unique", "no_null_pk", "games_present"]
    },
    "dim_season": {
        "pk": "season_id",
        "required": ["season_id"],
        "expected_rows": (1, 20),
        "checks": ["pk_unique"]
    },
    "dim_league": {
        "pk": "league_id",
        "required": ["league_id"],
        "expected_rows": (1, 10),
        "checks": ["pk_unique"]
    },
    "dim_event_type": {
        "pk": "event_type_id",
        "required": ["event_type_id", "event_type_code"],
        "expected_rows": (10, 50),
        "checks": ["pk_unique", "no_null_pk"]
    },
    "dim_event_detail": {
        "pk": "event_detail_id",
        "required": ["event_detail_id"],
        "expected_rows": (20, 200),
        "checks": ["pk_unique"]
    },
    "dim_event_detail_2": {
        "pk": "event_detail_2_id",
        "required": ["event_detail_2_id"],
        "expected_rows": (20, 200),
        "checks": ["pk_unique"]
    },
    "dim_play_detail": {
        "pk": "play_detail_id",
        "required": ["play_detail_id"],
        "expected_rows": (50, 300),
        "checks": ["pk_unique"]
    },
    "dim_play_detail_2": {
        "pk": "play_detail_2_id",
        "required": ["play_detail_2_id"],
        "expected_rows": (20, 200),
        "checks": ["pk_unique"]
    },
    "dim_position": {
        "pk": "position_id",
        "required": ["position_id"],
        "expected_rows": (3, 20),
        "checks": ["pk_unique"]
    },
    "dim_zone": {
        "pk": "zone_id",
        "required": ["zone_id"],
        "expected_rows": (3, 10),
        "checks": ["pk_unique"]
    },
    "dim_period": {
        "pk": "period_id",
        "required": ["period_id"],
        "expected_rows": (3, 10),
        "checks": ["pk_unique"]
    },
    "dim_venue": {
        "pk": "venue_id",
        "required": ["venue_id"],
        "expected_rows": (2, 10),
        "checks": ["pk_unique"]
    },
    "dim_player_role": {
        "pk": "role_id",
        "required": ["role_id"],
        "expected_rows": (5, 30),
        "checks": ["pk_unique"]
    },
    "dim_strength": {
        "pk": "strength_id",
        "required": ["strength_id"],
        "expected_rows": (5, 30),
        "checks": ["pk_unique"]
    },
    "dim_situation": {
        "pk": "situation_id",
        "required": ["situation_id"],
        "expected_rows": (3, 20),
        "checks": ["pk_unique"]
    },
    "dim_shot_type": {
        "pk": "shot_type_id",
        "required": ["shot_type_id"],
        "expected_rows": (5, 30),
        "checks": ["pk_unique"]
    },
    "dim_pass_type": {
        "pk": "pass_type_id",
        "required": ["pass_type_id"],
        "expected_rows": (5, 30),
        "checks": ["pk_unique"]
    },
    "dim_success": {
        "pk": "success_id",
        "required": ["success_id"],
        "expected_rows": (1, 10),
        "checks": ["pk_unique"]
    },
    "dim_shift_start_type": {
        "pk": "shift_start_type_id",
        "required": ["shift_start_type_id"],
        "expected_rows": (3, 20),
        "checks": ["pk_unique"]
    },
    "dim_shift_stop_type": {
        "pk": "shift_stop_type_id",
        "required": ["shift_stop_type_id"],
        "expected_rows": (5, 50),
        "checks": ["pk_unique"]
    },
    "dim_shift_slot": {
        "pk": "shift_slot_id",
        "required": ["shift_slot_id"],
        "expected_rows": (3, 20),
        "checks": ["pk_unique"]
    },
    "dim_stoppage_type": {
        "pk": "stoppage_type_id",
        "required": ["stoppage_type_id"],
        "expected_rows": (5, 30),
        "checks": ["pk_unique"]
    },
    "dim_turnover_type": {
        "pk": "turnover_type_id",
        "required": ["turnover_type_id"],
        "expected_rows": (5, 50),
        "checks": ["pk_unique"]
    },
    "dim_turnover_quality": {
        "pk": "turnover_quality_id",
        "required": ["turnover_quality_id"],
        "expected_rows": (2, 10),
        "checks": ["pk_unique"]
    },
    "dim_takeaway_type": {
        "pk": "takeaway_type_id",
        "required": ["takeaway_type_id"],
        "expected_rows": (3, 20),
        "checks": ["pk_unique"]
    },
    "dim_giveaway_type": {
        "pk": "giveaway_type_id",
        "required": ["giveaway_type_id"],
        "expected_rows": (3, 20),
        "checks": ["pk_unique"]
    },
    "dim_zone_entry_type": {
        "pk": "zone_entry_type_id",
        "required": ["zone_entry_type_id"],
        "expected_rows": (3, 20),
        "checks": ["pk_unique"]
    },
    "dim_zone_exit_type": {
        "pk": "zone_exit_type_id",
        "required": ["zone_exit_type_id"],
        "expected_rows": (3, 20),
        "checks": ["pk_unique"]
    },
    "dim_stat": {
        "pk": "stat_id",
        "required": ["stat_id"],
        "expected_rows": (20, 200),
        "checks": ["pk_unique"]
    },
    "dim_stat_type": {
        "pk": "stat_type_id",
        "required": ["stat_type_id"],
        "expected_rows": (10, 100),
        "checks": ["pk_unique"]
    },
    "dim_stat_category": {
        "pk": "stat_category_id",
        "required": ["stat_category_id"],
        "expected_rows": (5, 30),
        "checks": ["pk_unique"]
    },
    "dim_micro_stat": {
        "pk": "micro_stat_id",
        "required": ["micro_stat_id"],
        "expected_rows": (10, 50),
        "checks": ["pk_unique"]
    },
    "dim_danger_zone": {
        "pk": "danger_zone_id",
        "required": ["danger_zone_id"],
        "expected_rows": (3, 10),
        "checks": ["pk_unique"]
    },
    "dim_composite_rating": {
        "pk": "rating_id",
        "required": ["rating_id"],
        "expected_rows": (3, 20),
        "checks": ["pk_unique"]
    },
    "dim_comparison_type": {
        "pk": "comparison_type_id",
        "required": ["comparison_type_id"],
        "expected_rows": (3, 20),
        "checks": ["pk_unique"]
    },
    "dim_net_location": {
        "pk": "net_location_id",
        "required": ["net_location_id"],
        "expected_rows": (5, 20),
        "checks": ["pk_unique"]
    },
    "dim_rink_coord": {
        "pk": "rink_coord_id",
        "required": ["rink_coord_id"],
        "expected_rows": (10, 50),
        "checks": ["pk_unique"]
    },
    "dim_terminology_mapping": {
        "pk": None,
        "required": ["dimension", "old_value", "new_value"],
        "expected_rows": (10, 200),
        "checks": []
    },
    "dim_playerurlref": {
        "pk": None,
        "required": ["player_id"],
        "expected_rows": (100, 1000),
        "checks": []
    },
    "dim_rinkboxcoord": {
        "pk": None,
        "required": [],
        "expected_rows": (10, 100),
        "checks": []
    },
    "dim_rinkcoordzones": {
        "pk": None,
        "required": [],
        "expected_rows": (50, 500),
        "checks": []
    },
    "dim_randomnames": {
        "pk": None,
        "required": [],
        "expected_rows": (100, 1000),
        "checks": []
    },
    # NEW EXTENDED DIMS
    "dim_assist_type": {
        "pk": "assist_type_id",
        "required": ["assist_type_id", "assist_type_code"],
        "expected_rows": (3, 10),
        "checks": ["pk_unique"]
    },
    "dim_game_state": {
        "pk": "game_state_id",
        "required": ["game_state_id", "game_state_code"],
        "expected_rows": (3, 10),
        "checks": ["pk_unique"]
    },
    "dim_time_bucket": {
        "pk": "time_bucket_id",
        "required": ["time_bucket_id", "time_bucket_code"],
        "expected_rows": (3, 10),
        "checks": ["pk_unique"]
    },
    "dim_shift_quality_tier": {
        "pk": "tier_id",
        "required": ["tier_id", "tier_code"],
        "expected_rows": (3, 10),
        "checks": ["pk_unique"]
    },
    
    # ===================
    # FACT TABLES
    # ===================
    "fact_events": {
        "pk": "event_id",
        "fks": {"game_id": "dim_schedule"},
        "required": ["event_id", "game_id", "event_type"],
        "expected_rows": (1000, 20000),
        "checks": ["pk_unique", "fk_integrity", "games_present", "goal_count"]
    },
    "fact_events_long": {
        "pk": None,
        "fks": {"game_id": "dim_schedule", "player_id": "dim_player"},
        "required": ["game_id", "event_index"],
        "expected_rows": (2000, 50000),
        "checks": ["fk_integrity", "games_present"]
    },
    "fact_events_tracking": {
        "pk": "event_id",
        "fks": {"game_id": "dim_schedule", "player_id": "dim_player"},
        "required": ["event_id", "game_id"],
        "expected_rows": (5000, 50000),
        "checks": ["fk_integrity", "games_present"]
    },
    "fact_events_player": {
        "pk": None,
        "fks": {"game_id": "dim_schedule", "player_id": "dim_player"},
        "required": ["game_id"],
        "expected_rows": (5000, 50000),
        "checks": ["fk_integrity"]
    },
    "fact_shifts": {
        "pk": "shift_id",
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id", "shift_index"],
        "expected_rows": (100, 2000),
        "checks": ["fk_integrity", "games_present"]
    },
    "fact_shifts_tracking": {
        "pk": None,
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id"],
        "expected_rows": (100, 2000),
        "checks": ["fk_integrity"]
    },
    "fact_shift_players": {
        "pk": None,
        "fks": {"game_id": "dim_schedule", "player_id": "dim_player"},
        "required": ["game_id"],
        "expected_rows": (1000, 20000),
        "checks": ["fk_integrity"]
    },
    "fact_shifts_player": {
        "pk": None,
        "fks": {"game_id": "dim_schedule", "player_id": "dim_player"},
        "required": ["game_id"],
        "expected_rows": (1000, 20000),
        "checks": ["fk_integrity"]
    },
    "fact_shifts_long": {
        "pk": None,
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id"],
        "expected_rows": (1000, 20000),
        "checks": ["fk_integrity"]
    },
    "fact_gameroster": {
        "pk": "player_game_id",
        "fks": {"game_id": "dim_schedule", "player_id": "dim_player"},
        "required": ["player_game_id", "game_id", "player_id"],
        "expected_rows": (5000, 50000),
        "checks": ["pk_unique", "fk_integrity"]
    },
    "fact_playergames": {
        "pk": "player_game_id",
        "fks": {"game_id": "dim_schedule", "player_id": "dim_player"},
        "required": ["player_game_id"],
        "expected_rows": (1000, 10000),
        "checks": ["pk_unique", "fk_integrity"]
    },
    "fact_player_game_stats": {
        "pk": "player_game_key",
        "fks": {"game_id": "dim_schedule", "player_id": "dim_player"},
        "required": ["player_id", "game_id"],
        "expected_rows": (50, 500),
        "checks": ["pk_unique", "fk_integrity", "stats_sum", "goal_count"]
    },
    "fact_player_period_stats": {
        "pk": None,
        "fks": {"game_id": "dim_schedule", "player_id": "dim_player"},
        "required": ["player_id", "game_id", "period"],
        "expected_rows": (100, 2000),
        "checks": ["fk_integrity"]
    },
    "fact_team_game_stats": {
        "pk": None,
        "fks": {"game_id": "dim_schedule", "team_id": "dim_team"},
        "required": ["team_id", "game_id"],
        "expected_rows": (5, 100),
        "checks": ["fk_integrity", "games_present"]
    },
    "fact_goalie_game_stats": {
        "pk": "goalie_game_key",
        "fks": {"game_id": "dim_schedule", "player_id": "dim_player"},
        "required": ["player_id", "game_id"],
        "expected_rows": (5, 50),
        "checks": ["fk_integrity"]
    },
    "fact_h2h": {
        "pk": None,
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id", "player_id", "opp_player_id"],
        "expected_rows": (100, 5000),
        "checks": ["fk_integrity"]
    },
    "fact_head_to_head": {
        "pk": None,
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id"],
        "expected_rows": (100, 5000),
        "checks": ["fk_integrity"]
    },
    "fact_wowy": {
        "pk": None,
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id", "player_id", "partner_id"],
        "expected_rows": (100, 5000),
        "checks": ["fk_integrity"]
    },
    "fact_line_combos": {
        "pk": None,
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id"],
        "expected_rows": (50, 1000),
        "checks": ["fk_integrity"]
    },
    "fact_sequences": {
        "pk": "sequence_id",
        "fks": {"game_id": "dim_schedule"},
        "required": ["sequence_id", "game_id"],
        "expected_rows": (100, 5000),
        "checks": ["fk_integrity"]
    },
    "fact_plays": {
        "pk": "play_id",
        "fks": {"game_id": "dim_schedule"},
        "required": ["play_id", "game_id"],
        "expected_rows": (500, 10000),
        "checks": ["fk_integrity"]
    },
    "fact_linked_events": {
        "pk": None,
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id"],
        "expected_rows": (100, 5000),
        "checks": ["fk_integrity"]
    },
    "fact_cycle_events": {
        "pk": None,
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id"],
        "expected_rows": (1, 1000),
        "checks": ["fk_integrity"]
    },
    "fact_rush_events": {
        "pk": None,
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id"],
        "expected_rows": (10, 1000),
        "checks": ["fk_integrity"]
    },
    "fact_scoring_chances": {
        "pk": None,
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id"],
        "expected_rows": (50, 2000),
        "checks": ["fk_integrity"]
    },
    "fact_shot_danger": {
        "pk": None,
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id"],
        "expected_rows": (50, 2000),
        "checks": ["fk_integrity"]
    },
    "fact_shift_quality": {
        "pk": None,
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id"],
        "expected_rows": (500, 10000),
        "checks": ["fk_integrity"]
    },
    "fact_shift_quality_logical": {
        "pk": None,
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id"],
        "expected_rows": (10, 500),
        "checks": ["fk_integrity"]
    },
    "fact_team_zone_time": {
        "pk": None,
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id"],
        "expected_rows": (5, 100),
        "checks": ["fk_integrity"]
    },
    "fact_matchup_summary": {
        "pk": None,
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id"],
        "expected_rows": (50, 2000),
        "checks": ["fk_integrity"]
    },
    "fact_player_stats_long": {
        "pk": None,
        "fks": {"player_id": "dim_player"},
        "required": ["player_id"],
        "expected_rows": (500, 50000),
        "checks": ["fk_integrity"]
    },
    "fact_player_micro_stats": {
        "pk": None,
        "fks": {"player_id": "dim_player"},
        "required": ["player_id"],
        "expected_rows": (50, 2000),
        "checks": ["fk_integrity"]
    },
    "fact_player_event_chains": {
        "pk": None,
        "fks": {"game_id": "dim_schedule", "player_id": "dim_player"},
        "required": ["game_id", "player_id"],
        "expected_rows": (500, 20000),
        "checks": ["fk_integrity"]
    },
    "fact_shot_chains": {
        "pk": None,
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id"],
        "expected_rows": (50, 2000),
        "checks": ["fk_integrity"]
    },
    "fact_player_pair_stats": {
        "pk": None,
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id"],
        "expected_rows": (50, 2000),
        "checks": ["fk_integrity"]
    },
    "fact_possession_time": {
        "pk": None,
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id"],
        "expected_rows": (10, 500),
        "checks": ["fk_integrity"]
    },
    "fact_game_status": {
        "pk": None,
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id"],
        "expected_rows": (100, 1000),
        "checks": ["fk_integrity", "games_present"]
    },
    "fact_suspicious_stats": {
        "pk": None,
        "required": [],
        "expected_rows": (0, 100),
        "checks": []
    },
    "fact_player_game_position": {
        "pk": None,
        "fks": {"game_id": "dim_schedule", "player_id": "dim_player"},
        "required": ["game_id", "player_id"],
        "expected_rows": (10, 500),
        "checks": ["fk_integrity"]
    },
    "fact_player_boxscore_all": {
        "pk": None,
        "fks": {"player_id": "dim_player"},
        "required": ["player_id"],
        "expected_rows": (1000, 50000),
        "checks": ["fk_integrity"]
    },
    "fact_league_leaders_snapshot": {
        "pk": None,
        "required": [],
        "expected_rows": (1000, 50000),
        "checks": []
    },
    "fact_team_standings_snapshot": {
        "pk": None,
        "required": [],
        "expected_rows": (100, 5000),
        "checks": []
    },
    "fact_video": {
        "pk": None,
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id"],
        "expected_rows": (1, 100),
        "checks": ["fk_integrity"]
    },
    "fact_draft": {
        "pk": None,
        "fks": {"player_id": "dim_player"},
        "required": ["player_id"],
        "expected_rows": (50, 500),
        "checks": ["fk_integrity"]
    },
    "fact_registration": {
        "pk": None,
        "fks": {"player_id": "dim_player"},
        "required": ["player_id"],
        "expected_rows": (50, 500),
        "checks": ["fk_integrity"]
    },
    "fact_leadership": {
        "pk": None,
        "required": [],
        "expected_rows": (10, 100),
        "checks": []
    },
    # XY Tables
    "fact_player_xy_long": {
        "pk": None,
        "required": [],
        "expected_rows": (0, 100000),
        "checks": []
    },
    "fact_player_xy_wide": {
        "pk": None,
        "required": [],
        "expected_rows": (0, 100000),
        "checks": []
    },
    "fact_puck_xy_long": {
        "pk": None,
        "required": [],
        "expected_rows": (0, 100000),
        "checks": []
    },
    "fact_puck_xy_wide": {
        "pk": None,
        "required": [],
        "expected_rows": (0, 100000),
        "checks": []
    },
    "fact_shot_xy": {
        "pk": None,
        "required": [],
        "expected_rows": (0, 10000),
        "checks": []
    },
    # NEW EXTENDED FACTS
    "fact_player_career_stats": {
        "pk": "player_career_key",
        "fks": {"player_id": "dim_player"},
        "required": ["player_id", "games_played"],
        "expected_rows": (20, 200),
        "checks": ["pk_unique", "fk_integrity", "career_totals"]
    },
    "fact_team_season_stats": {
        "pk": "team_season_key",
        "fks": {"team_id": "dim_team"},
        "required": ["team_id", "games_played"],
        "expected_rows": (2, 50),
        "checks": ["pk_unique", "fk_integrity"]
    },
    "fact_season_summary": {
        "pk": "season_summary_key",
        "required": ["games_tracked", "total_goals"],
        "expected_rows": (1, 5),
        "checks": ["pk_unique", "season_totals"]
    },
    "fact_player_trends": {
        "pk": "player_trend_key",
        "fks": {"player_id": "dim_player", "game_id": "dim_schedule"},
        "required": ["player_id", "game_id"],
        "expected_rows": (50, 1000),
        "checks": ["pk_unique", "fk_integrity", "cumulative_check"]
    },
    "fact_zone_entry_summary": {
        "pk": "zone_entry_key",
        "fks": {"player_id": "dim_player"},
        "required": ["player_id"],
        "expected_rows": (20, 200),
        "checks": ["pk_unique", "fk_integrity"]
    },
    "fact_zone_exit_summary": {
        "pk": "zone_exit_key",
        "fks": {"player_id": "dim_player"},
        "required": ["player_id"],
        "expected_rows": (20, 200),
        "checks": ["pk_unique", "fk_integrity"]
    },
    "fact_player_position_splits": {
        "pk": "position_split_key",
        "required": ["position", "player_count"],
        "expected_rows": (2, 10),
        "checks": ["pk_unique"]
    },
    "fact_period_momentum": {
        "pk": "momentum_key",
        "fks": {"game_id": "dim_schedule"},
        "required": ["game_id", "period"],
        "expected_rows": (5, 50),
        "checks": ["pk_unique", "fk_integrity"]
    },
    "fact_special_teams_summary": {
        "pk": "special_teams_key",
        "fks": {"team_id": "dim_team"},
        "required": ["team_id"],
        "expected_rows": (2, 50),
        "checks": ["pk_unique", "fk_integrity"]
    },
    
    # ===================
    # QA TABLES
    # ===================
    "qa_suspicious_stats": {
        "pk": None,
        "required": [],
        "expected_rows": (0, 100),
        "checks": []
    },
    "qa_goal_accuracy": {
        "pk": "qa_key",
        "required": ["game_id", "expected_goals", "actual_goals"],
        "expected_rows": (1, 20),
        "checks": ["pk_unique", "goal_accuracy"]
    },
    "qa_data_completeness": {
        "pk": "qa_key",
        "required": ["game_id", "is_complete"],
        "expected_rows": (1, 20),
        "checks": ["pk_unique"]
    },
}


# ============================================================
# VALIDATION FUNCTIONS
# ============================================================

class TableValidator:
    """Validates a single table."""
    
    def __init__(self, table_name, df, config, all_tables):
        self.table_name = table_name
        self.df = df
        self.config = config
        self.all_tables = all_tables
        self.issues = []
        self.warnings = []
        self.passed = []
        
    def validate(self):
        """Run all configured checks."""
        checks = self.config.get("checks", [])
        
        # Always check row count
        self._check_row_count()
        
        # Always check required columns
        self._check_required_columns()
        
        # Run configured checks
        for check in checks:
            method = getattr(self, f"_check_{check}", None)
            if method:
                method()
        
        return {
            "table": self.table_name,
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "issues": self.issues,
            "warnings": self.warnings,
            "passed": self.passed,
            "status": "FAIL" if self.issues else ("WARN" if self.warnings else "PASS")
        }
    
    def _check_row_count(self):
        """Check if row count is within expected range."""
        expected = self.config.get("expected_rows", (0, 1000000))
        if len(self.df) < expected[0]:
            self.issues.append(f"Row count {len(self.df)} below minimum {expected[0]}")
        elif len(self.df) > expected[1]:
            self.warnings.append(f"Row count {len(self.df)} above expected max {expected[1]}")
        else:
            self.passed.append(f"Row count {len(self.df)} in expected range")
    
    def _check_required_columns(self):
        """Check that required columns exist."""
        required = self.config.get("required", [])
        missing = [c for c in required if c not in self.df.columns]
        if missing:
            self.issues.append(f"Missing required columns: {missing}")
        elif required:
            self.passed.append(f"All {len(required)} required columns present")
    
    def _check_pk_unique(self):
        """Check primary key uniqueness."""
        pk = self.config.get("pk")
        if pk and pk in self.df.columns:
            duplicates = self.df[pk].duplicated().sum()
            if duplicates > 0:
                self.issues.append(f"PK '{pk}' has {duplicates} duplicates")
            else:
                self.passed.append(f"PK '{pk}' is unique")
    
    def _check_no_null_pk(self):
        """Check for null values in primary key."""
        pk = self.config.get("pk")
        if pk and pk in self.df.columns:
            nulls = self.df[pk].isna().sum()
            if nulls > 0:
                self.issues.append(f"PK '{pk}' has {nulls} null values")
            else:
                self.passed.append(f"PK '{pk}' has no nulls")
    
    def _check_fk_integrity(self):
        """Check foreign key referential integrity."""
        fks = self.config.get("fks", {})
        for fk_col, ref_table in fks.items():
            if fk_col not in self.df.columns:
                continue
            
            ref_df = self.all_tables.get(ref_table)
            if ref_df is None:
                self.warnings.append(f"FK '{fk_col}' -> '{ref_table}' (ref table not loaded)")
                continue
            
            # Determine the PK column in reference table
            ref_config = TABLE_REGISTRY.get(ref_table, {})
            ref_pk = ref_config.get("pk")
            if not ref_pk:
                # Try common patterns
                ref_pk = fk_col
            
            if ref_pk not in ref_df.columns:
                self.warnings.append(f"FK '{fk_col}' -> '{ref_table}.{ref_pk}' (PK col not found)")
                continue
            
            # Check for orphans
            fk_values = set(self.df[fk_col].dropna().unique())
            ref_values = set(ref_df[ref_pk].dropna().unique())
            orphans = fk_values - ref_values
            
            if len(orphans) > 0:
                sample = list(orphans)[:3]
                self.warnings.append(f"FK '{fk_col}' has {len(orphans)} orphan values (e.g., {sample})")
            else:
                self.passed.append(f"FK '{fk_col}' -> '{ref_table}' integrity OK")
    
    def _check_games_present(self):
        """Check that expected games are present."""
        if 'game_id' not in self.df.columns:
            return
        
        game_ids = self.df['game_id'].unique()
        
        # Convert to int for comparison
        try:
            game_ids_int = set([int(g) for g in game_ids if pd.notna(g)])
        except:
            game_ids_int = set()
        
        missing = set(EXPECTED_GAMES) - game_ids_int
        if missing:
            self.warnings.append(f"Missing expected games: {missing}")
        else:
            self.passed.append(f"All {len(EXPECTED_GAMES)} expected games present")
    
    def _check_goal_count(self):
        """Check that goal counts match expected."""
        if 'game_id' not in self.df.columns:
            return
        
        # Try different goal identification methods
        goals_found = False
        
        # Method 1: event_type contains 'Goal'
        if 'event_type' in self.df.columns:
            for game_id, expected_goals in EXPECTED_GOALS.items():
                game_df = self.df[self.df['game_id'] == game_id]
                goal_events = game_df[game_df['event_type'].astype(str).str.contains('Goal', case=False, na=False)]
                if len(goal_events) != expected_goals:
                    self.warnings.append(f"Game {game_id}: {len(goal_events)} goals (expected {expected_goals})")
                else:
                    self.passed.append(f"Game {game_id}: {expected_goals} goals ✓")
            goals_found = True
        
        # Method 2: goals column sum
        if 'goals' in self.df.columns and not goals_found:
            total_goals = self.df['goals'].sum()
            if abs(total_goals - TOTAL_EXPECTED_GOALS) > 0.1:
                self.warnings.append(f"Total goals {total_goals} vs expected {TOTAL_EXPECTED_GOALS}")
            else:
                self.passed.append(f"Total goals {total_goals} matches expected")
    
    def _check_stats_sum(self):
        """Check that points = goals + assists."""
        if all(c in self.df.columns for c in ['points', 'goals', 'assists']):
            calc_points = self.df['goals'].fillna(0) + self.df['assists'].fillna(0)
            actual_points = self.df['points'].fillna(0)
            mismatches = (calc_points != actual_points).sum()
            if mismatches > 0:
                self.warnings.append(f"{mismatches} rows where points != goals + assists")
            else:
                self.passed.append("points = goals + assists ✓")
    
    def _check_career_totals(self):
        """Check career stats are sums of game stats."""
        # This would need to compare against fact_player_game_stats
        pgs = self.all_tables.get("fact_player_game_stats")
        if pgs is None or len(pgs) == 0:
            return
        
        # Spot check a few players
        for _, row in self.df.head(3).iterrows():
            player_id = row.get('player_id')
            if player_id:
                player_games = pgs[pgs['player_id'] == player_id]
                if 'career_goals' in row and 'goals' in player_games.columns:
                    expected = player_games['goals'].sum()
                    actual = row['career_goals']
                    if abs(expected - actual) > 0.1:
                        self.warnings.append(f"Player {player_id}: career_goals {actual} vs sum {expected}")
                    else:
                        self.passed.append(f"Player {player_id}: career_goals matches sum")
    
    def _check_season_totals(self):
        """Check season summary totals."""
        if 'total_goals' in self.df.columns:
            total = self.df['total_goals'].iloc[0] if len(self.df) > 0 else 0
            if total != TOTAL_EXPECTED_GOALS:
                self.warnings.append(f"Season total_goals {total} vs expected {TOTAL_EXPECTED_GOALS}")
            else:
                self.passed.append(f"Season total_goals {TOTAL_EXPECTED_GOALS} ✓")
    
    def _check_cumulative_check(self):
        """Check cumulative values are monotonically increasing per player."""
        if 'cumulative_points' not in self.df.columns or 'player_id' not in self.df.columns:
            return
        
        issues = 0
        for player_id, group in self.df.groupby('player_id'):
            sorted_group = group.sort_values('game_number')
            if not sorted_group['cumulative_points'].is_monotonic_increasing:
                issues += 1
        
        if issues > 0:
            self.warnings.append(f"{issues} players with non-monotonic cumulative_points")
        else:
            self.passed.append("cumulative_points monotonically increasing ✓")
    
    def _check_goal_accuracy(self):
        """Check qa_goal_accuracy table."""
        if 'match' in self.df.columns:
            mismatches = (~self.df['match']).sum()
            if mismatches > 0:
                self.issues.append(f"{mismatches} goal count mismatches")
            else:
                self.passed.append("All goal counts match ✓")


# ============================================================
# MAIN QA RUNNER
# ============================================================

def load_all_tables():
    """Load all CSV tables from output directory."""
    tables = {}
    for csv_file in OUTPUT_DIR.glob("*.csv"):
        try:
            tables[csv_file.stem] = pd.read_csv(csv_file)
        except Exception as e:
            print(f"  Warning: Could not load {csv_file.name}: {e}")
    return tables


def run_qa(tables=None, table_filter=None, category=None):
    """Run QA on all or selected tables."""
    print("=" * 70)
    print("BENCHSIGHT TABLE-BY-TABLE QUALITY ASSURANCE")
    print("=" * 70)
    
    if tables is None:
        print("\nLoading tables...")
        tables = load_all_tables()
        print(f"  Loaded {len(tables)} tables")
    
    # Filter tables if requested
    tables_to_check = list(TABLE_REGISTRY.keys())
    
    if table_filter:
        tables_to_check = [t for t in tables_to_check if table_filter.lower() in t.lower()]
    
    if category:
        if category == "dims":
            tables_to_check = [t for t in tables_to_check if t.startswith("dim_")]
        elif category == "facts":
            tables_to_check = [t for t in tables_to_check if t.startswith("fact_")]
        elif category == "qa":
            tables_to_check = [t for t in tables_to_check if t.startswith("qa_")]
    
    results = []
    pass_count = 0
    warn_count = 0
    fail_count = 0
    missing_count = 0
    
    print(f"\nValidating {len(tables_to_check)} tables...\n")
    
    for table_name in sorted(tables_to_check):
        config = TABLE_REGISTRY.get(table_name, {})
        
        if table_name not in tables:
            print(f"  ✗ {table_name}: NOT FOUND")
            missing_count += 1
            results.append({
                "table": table_name,
                "status": "MISSING",
                "rows": 0,
                "columns": 0,
                "issues": ["Table not found"],
                "warnings": [],
                "passed": []
            })
            continue
        
        df = tables[table_name]
        validator = TableValidator(table_name, df, config, tables)
        result = validator.validate()
        results.append(result)
        
        status = result["status"]
        if status == "PASS":
            pass_count += 1
            print(f"  ✓ {table_name}: PASS ({result['rows']} rows)")
        elif status == "WARN":
            warn_count += 1
            print(f"  ⚠ {table_name}: WARN ({result['rows']} rows)")
            for w in result["warnings"][:2]:
                print(f"      - {w}")
        else:
            fail_count += 1
            print(f"  ✗ {table_name}: FAIL ({result['rows']} rows)")
            for i in result["issues"][:2]:
                print(f"      - {i}")
    
    # Summary
    print("\n" + "=" * 70)
    print("QA SUMMARY")
    print("=" * 70)
    print(f"  Tables checked: {len(tables_to_check)}")
    print(f"  PASS: {pass_count}")
    print(f"  WARN: {warn_count}")
    print(f"  FAIL: {fail_count}")
    print(f"  MISSING: {missing_count}")
    
    return results


def generate_report(results, format="text"):
    """Generate QA report."""
    QA_REPORT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == "json":
        report_path = QA_REPORT_DIR / f"qa_report_{timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
    
    elif format == "html":
        report_path = QA_REPORT_DIR / f"qa_report_{timestamp}.html"
        html = generate_html_report(results)
        with open(report_path, 'w') as f:
            f.write(html)
    
    else:  # text
        report_path = QA_REPORT_DIR / f"qa_report_{timestamp}.txt"
        with open(report_path, 'w') as f:
            f.write("BENCHSIGHT QA REPORT\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("=" * 70 + "\n\n")
            
            for r in results:
                f.write(f"\n{r['table']}: {r['status']}\n")
                f.write(f"  Rows: {r['rows']}, Columns: {r['columns']}\n")
                
                if r['issues']:
                    f.write("  Issues:\n")
                    for i in r['issues']:
                        f.write(f"    - {i}\n")
                
                if r['warnings']:
                    f.write("  Warnings:\n")
                    for w in r['warnings']:
                        f.write(f"    - {w}\n")
    
    print(f"\nReport saved: {report_path}")
    return report_path


def generate_html_report(results):
    """Generate HTML report."""
    pass_count = sum(1 for r in results if r['status'] == 'PASS')
    warn_count = sum(1 for r in results if r['status'] == 'WARN')
    fail_count = sum(1 for r in results if r['status'] == 'FAIL')
    missing_count = sum(1 for r in results if r['status'] == 'MISSING')
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>BenchSight QA Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .summary-box {{ padding: 15px; border-radius: 8px; min-width: 100px; text-align: center; }}
        .pass {{ background: #d4edda; color: #155724; }}
        .warn {{ background: #fff3cd; color: #856404; }}
        .fail {{ background: #f8d7da; color: #721c24; }}
        .missing {{ background: #e2e3e5; color: #383d41; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f4f4f4; }}
        tr:hover {{ background: #f5f5f5; }}
        .status-pass {{ color: green; font-weight: bold; }}
        .status-warn {{ color: orange; font-weight: bold; }}
        .status-fail {{ color: red; font-weight: bold; }}
        .status-missing {{ color: gray; font-weight: bold; }}
        .issues {{ color: red; font-size: 0.9em; }}
        .warnings {{ color: orange; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>BenchSight QA Report</h1>
    <p>Generated: {datetime.now().isoformat()}</p>
    
    <div class="summary">
        <div class="summary-box pass"><h2>{pass_count}</h2>PASS</div>
        <div class="summary-box warn"><h2>{warn_count}</h2>WARN</div>
        <div class="summary-box fail"><h2>{fail_count}</h2>FAIL</div>
        <div class="summary-box missing"><h2>{missing_count}</h2>MISSING</div>
    </div>
    
    <table>
        <tr>
            <th>Table</th>
            <th>Status</th>
            <th>Rows</th>
            <th>Cols</th>
            <th>Issues/Warnings</th>
        </tr>
"""
    
    for r in sorted(results, key=lambda x: (x['status'] != 'FAIL', x['status'] != 'WARN', x['table'])):
        status_class = f"status-{r['status'].lower()}"
        issues_html = ""
        if r['issues']:
            issues_html += '<br>'.join([f'<span class="issues">✗ {i}</span>' for i in r['issues'][:3]])
        if r['warnings']:
            issues_html += '<br>'.join([f'<span class="warnings">⚠ {w}</span>' for w in r['warnings'][:3]])
        
        html += f"""
        <tr>
            <td>{r['table']}</td>
            <td class="{status_class}">{r['status']}</td>
            <td>{r['rows']:,}</td>
            <td>{r['columns']}</td>
            <td>{issues_html}</td>
        </tr>
"""
    
    html += """
    </table>
</body>
</html>
"""
    return html


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="BenchSight Table QA")
    parser.add_argument('--table', type=str, help='Filter to specific table(s)')
    parser.add_argument('--category', type=str, choices=['dims', 'facts', 'qa'],
                        help='Check only this category')
    parser.add_argument('--report', type=str, choices=['text', 'json', 'html'],
                        default='text', help='Report format')
    
    args = parser.parse_args()
    
    results = run_qa(table_filter=args.table, category=args.category)
    generate_report(results, format=args.report)
    
    # Exit code based on failures
    fail_count = sum(1 for r in results if r['status'] == 'FAIL')
    return 1 if fail_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
