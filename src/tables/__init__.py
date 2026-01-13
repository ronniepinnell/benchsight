"""
BenchSight Tables Module

Creates all tables for the BenchSight schema.

Submodules:
    dimension_tables - Static dimension/lookup tables
    core_facts - Player, team, goalie game stats
    shift_analytics - H2H, WOWY, line combos
    remaining_facts - Additional fact tables
    event_analytics - Scoring chances, shot danger, rush events

Usage:
    from src.tables.dimension_tables import create_all_dimension_tables
    from src.tables.core_facts import create_all_core_facts
    from src.tables.shift_analytics import create_all_shift_analytics
    from src.tables.remaining_facts import build_remaining_tables
    from src.tables.event_analytics import create_all_event_analytics
"""

__all__ = [
    'dimension_tables',
    'core_facts', 
    'shift_analytics',
    'remaining_facts',
    'event_analytics',
]
