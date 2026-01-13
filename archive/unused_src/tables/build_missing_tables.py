#!/usr/bin/env python3
"""
BenchSight Missing Tables Builder - Main Orchestrator

This module creates ALL missing tables for the BenchSight schema.
It coordinates the dimension tables, core facts, shift analytics,
and event analytics modules.

CRITICAL RULES:
1. ALL tables derive DYNAMICALLY from base ETL output
2. NO hardcoded game IDs - works on ANY game
3. NO patchwork code - complete implementations only
4. Runs AFTER base ETL completes

Usage:
    from src.tables.build_missing_tables import build_all_missing_tables
    build_all_missing_tables()
    
    # Or from command line:
    python -m src.tables.build_missing_tables

Tables Created:
    Dimension Tables (21):
        dim_comparison_type, dim_competition_tier, dim_composite_rating,
        dim_danger_zone, dim_micro_stat, dim_net_location, dim_pass_outcome,
        dim_rating, dim_rating_matchup, dim_rink_zone, dim_save_outcome,
        dim_shift_slot, dim_shot_outcome, dim_stat, dim_stat_category,
        dim_stat_type, dim_strength, dim_terminology_mapping,
        dim_turnover_quality, dim_turnover_type, dim_zone_outcome
    
    Core Fact Tables (3):
        fact_player_game_stats, fact_team_game_stats, fact_goalie_game_stats
    
    Shift Analytics Tables (5):
        fact_h2h, fact_wowy, fact_line_combos, fact_shift_quality,
        fact_shift_quality_logical
    
    Event Analytics Tables (5):
        fact_scoring_chances, fact_shot_danger, fact_linked_events,
        fact_rush_events, fact_possession_time
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / 'data' / 'output'


def build_all_missing_tables(verbose: bool = True, include_remaining: bool = True) -> dict:
    """
    Build ALL missing tables in the correct order.
    
    Order:
    1. Dimension tables (prerequisites for fact tables)
    2. Core fact tables (player/team/goalie stats)
    3. Shift analytics (H2H, WOWY, line combos)
    4. Event analytics (scoring chances, shot danger)
    
    Args:
        verbose: Print progress messages
    
    Returns:
        dict: Results with table counts and any errors
    """
    results = {
        'timestamp': datetime.now().isoformat(),
        'tables_created': {},
        'errors': [],
        'total_tables': 0,
        'total_rows': 0,
    }
    
    if verbose:
        print("\n" + "=" * 70)
        print("BUILDING ALL MISSING TABLES")
        print("=" * 70)
        print(f"Timestamp: {results['timestamp']}")
        print(f"Output directory: {OUTPUT_DIR}")
    
    # Verify base tables exist
    required_tables = ['fact_events', 'fact_event_players', 'fact_shifts']
    missing = [t for t in required_tables if not (OUTPUT_DIR / f"{t}.csv").exists()]
    
    if missing:
        error = f"Missing required base tables: {missing}"
        results['errors'].append(error)
        if verbose:
            print(f"\nERROR: {error}")
            print("Run base ETL first: python -m src.etl_orchestrator full")
        return results
    
    # ========================================================================
    # PHASE 1: DIMENSION TABLES
    # ========================================================================
    try:
        from src.tables.dimension_tables import create_all_dimension_tables
        dim_results = create_all_dimension_tables()
        results['tables_created'].update(dim_results)
        results['total_tables'] += len(dim_results)
        results['total_rows'] += sum(dim_results.values())
    except Exception as e:
        results['errors'].append(f"Dimension tables failed: {e}")
        if verbose:
            print(f"\nERROR creating dimension tables: {e}")
    
    # ========================================================================
    # PHASE 2: CORE FACT TABLES
    # ========================================================================
    try:
        from src.tables.core_facts import create_all_core_facts
        core_results = create_all_core_facts()
        results['tables_created'].update(core_results)
        results['total_tables'] += len(core_results)
        results['total_rows'] += sum(core_results.values())
    except Exception as e:
        results['errors'].append(f"Core facts failed: {e}")
        if verbose:
            print(f"\nERROR creating core fact tables: {e}")
    
    # ========================================================================
    # PHASE 3: SHIFT ANALYTICS
    # ========================================================================
    try:
        from src.tables.shift_analytics import create_all_shift_analytics
        shift_results = create_all_shift_analytics()
        results['tables_created'].update(shift_results)
        results['total_tables'] += len(shift_results)
        results['total_rows'] += sum(shift_results.values())
    except Exception as e:
        results['errors'].append(f"Shift analytics failed: {e}")
        if verbose:
            print(f"\nERROR creating shift analytics tables: {e}")
    
    # ========================================================================
    # PHASE 4: EVENT ANALYTICS
    # ========================================================================
    try:
        from src.tables.event_analytics import create_all_event_analytics
        event_results = create_all_event_analytics()
        results['tables_created'].update(event_results)
        results['total_tables'] += len(event_results)
        results['total_rows'] += sum(event_results.values())
    except Exception as e:
        results['errors'].append(f"Event analytics failed: {e}")
        if verbose:
            print(f"\nERROR creating event analytics tables: {e}")
    
    # ========================================================================
    # PHASE 5: REMAINING TABLES
    # ========================================================================
    if include_remaining:
        try:
            from src.tables.remaining_facts import build_remaining_tables
            remaining_results = build_remaining_tables(verbose=verbose)
            results['total_tables'] += len(remaining_results['tables_created'])
            results['total_rows'] += remaining_results['total_rows']
            for err in remaining_results.get('errors', []):
                results['errors'].append(f"Remaining: {err}")
        except Exception as e:
            results['errors'].append(f"Remaining tables failed: {e}")
            if verbose:
                print(f"\nERROR creating remaining tables: {e}")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    if verbose:
        print("\n" + "=" * 70)
        print("MISSING TABLES BUILD COMPLETE")
        print("=" * 70)
        print(f"Tables created: {results['total_tables']}")
        print(f"Total rows: {results['total_rows']:,}")
        
        if results['errors']:
            print(f"\nErrors ({len(results['errors'])}):")
            for err in results['errors']:
                print(f"  - {err}")
        else:
            print("\n✓ All tables created successfully!")
        
        # Count final table total
        csv_count = len(list(OUTPUT_DIR.glob('*.csv')))
        dim_count = len(list(OUTPUT_DIR.glob('dim_*.csv')))
        fact_count = len(list(OUTPUT_DIR.glob('fact_*.csv')))
        qa_count = len(list(OUTPUT_DIR.glob('qa_*.csv')))
        
        print(f"\nFinal table counts:")
        print(f"  Total: {csv_count}")
        print(f"  Dimensions: {dim_count}")
        print(f"  Facts: {fact_count}")
        print(f"  QA: {qa_count}")
    
    return results


def main():
    """Main entry point."""
    results = build_all_missing_tables(verbose=True)
    return 0 if not results['errors'] else 1


if __name__ == "__main__":
    sys.exit(main())
