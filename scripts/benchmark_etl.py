#!/usr/bin/env python3
"""
ETL Performance Benchmark Script

Measures ETL performance and compares against baseline.
Useful for validating v29.2 optimizations and tracking improvements.

Usage:
    python scripts/benchmark_etl.py              # Run full ETL with timing
    python scripts/benchmark_etl.py --baseline   # Save current run as baseline
    python scripts/benchmark_etl.py --compare    # Compare against saved baseline
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Baseline file
BASELINE_FILE = PROJECT_ROOT / 'data' / '.etl_baseline.json'


@contextmanager
def timer(name):
    """Context manager for timing operations."""
    start = time.time()
    yield
    elapsed = time.time() - start
    print(f"  ⏱️  {name}: {elapsed:.2f}s")


def save_baseline(results):
    """Save current run as baseline."""
    baseline = {
        'timestamp': datetime.now().isoformat(),
        'version': 'v29.2',
        'results': results
    }
    BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(BASELINE_FILE, 'w') as f:
        json.dump(baseline, f, indent=2)
    print(f"\n✅ Baseline saved to {BASELINE_FILE}")


def load_baseline():
    """Load saved baseline."""
    if not BASELINE_FILE.exists():
        return None
    with open(BASELINE_FILE, 'r') as f:
        return json.load(f)


def compare_results(current, baseline):
    """Compare current results against baseline."""
    if not baseline:
        print("\n⚠️  No baseline found. Run with --baseline first.")
        return
    
    baseline_results = baseline.get('results', {})
    baseline_total = baseline_results.get('total_time', 0)
    current_total = current.get('total_time', 0)
    
    if baseline_total == 0:
        print("\n⚠️  Baseline has no timing data.")
        return
    
    speedup = baseline_total / current_total if current_total > 0 else 0
    improvement = ((baseline_total - current_total) / baseline_total * 100) if baseline_total > 0 else 0
    
    print("\n" + "=" * 70)
    print("PERFORMANCE COMPARISON")
    print("=" * 70)
    print(f"Baseline (v{baseline.get('version', 'unknown')}): {baseline_total:.2f}s")
    print(f"Current (v29.2):     {current_total:.2f}s")
    print(f"Speedup:             {speedup:.2f}x")
    print(f"Improvement:         {improvement:.1f}% faster")
    print("=" * 70)
    
    # Compare phase timings
    baseline_phases = baseline_results.get('phases', {})
    current_phases = current.get('phases', {})
    
    if baseline_phases and current_phases:
        print("\nPhase-by-Phase Comparison:")
        print("-" * 70)
        print(f"{'Phase':<30} {'Baseline':<12} {'Current':<12} {'Speedup':<10}")
        print("-" * 70)
        
        all_phases = set(list(baseline_phases.keys()) + list(current_phases.keys()))
        for phase in sorted(all_phases):
            base_time = baseline_phases.get(phase, 0)
            curr_time = current_phases.get(phase, 0)
            if base_time > 0 and curr_time > 0:
                phase_speedup = base_time / curr_time
                print(f"{phase:<30} {base_time:>10.2f}s {curr_time:>10.2f}s {phase_speedup:>8.2f}x")
            elif base_time > 0:
                print(f"{phase:<30} {base_time:>10.2f}s {'N/A':<12} {'N/A':<10}")
            elif curr_time > 0:
                print(f"{phase:<30} {'N/A':<12} {curr_time:>10.2f}s {'N/A':<10}")


def run_benchmark():
    """Run ETL with detailed timing."""
    results = {
        'timestamp': datetime.now().isoformat(),
        'version': 'v29.2',
        'phases': {},
        'total_time': 0,
        'games_processed': 0
    }
    
    print("=" * 70)
    print("BENCHSIGHT ETL PERFORMANCE BENCHMARK")
    print("=" * 70)
    print(f"Started: {datetime.now().isoformat()}")
    print()
    
    # Games will be discovered during ETL
    
    # Time the full ETL
    start_total = time.time()
    
    # Import and run ETL
    try:
        # Phase 1: Base ETL
        with timer("Phase 1: Base ETL"):
            from src.core.base_etl import main as run_base_etl, discover_games
            valid_games, _ = discover_games()
            run_base_etl()
            results['phases']['base_etl'] = time.time() - start_total
        
        # Get games count from discovery or output
        if valid_games:
            results['games_processed'] = len(valid_games)
        else:
            # Fallback: count unique game_ids in fact_events
            try:
                import pandas as pd
                from pathlib import Path
                events_path = Path(__file__).parent.parent / 'data' / 'output' / 'fact_events.csv'
                if events_path.exists():
                    events = pd.read_csv(events_path, usecols=['game_id'], nrows=0)
                    # Actually, just count from the log output or use a simpler method
                    results['games_processed'] = len(valid_games) if valid_games else 0
                else:
                    results['games_processed'] = 0
            except:
                results['games_processed'] = 0
        
        # Phase 2: Dimension Tables
        phase_start = time.time()
        with timer("Phase 2: Dimension Tables"):
            from src.tables.dimension_tables import create_all_dimension_tables
            create_all_dimension_tables()
        results['phases']['dimension_tables'] = time.time() - phase_start
        
        # Phase 3: Core Facts
        phase_start = time.time()
        with timer("Phase 3: Core Facts"):
            from src.tables.core_facts import create_all_core_facts
            create_all_core_facts()
        results['phases']['core_facts'] = time.time() - phase_start
        
        # Phase 4: Shift Analytics
        phase_start = time.time()
        with timer("Phase 4: Shift Analytics"):
            from src.tables.shift_analytics import create_all_shift_analytics
            create_all_shift_analytics()
        results['phases']['shift_analytics'] = time.time() - phase_start
        
        # Phase 5: Remaining Facts
        phase_start = time.time()
        with timer("Phase 5: Remaining Facts"):
            from src.tables.remaining_facts import build_remaining_tables
            build_remaining_tables(verbose=False)
        results['phases']['remaining_facts'] = time.time() - phase_start
        
        # Phase 6: Event Analytics
        phase_start = time.time()
        with timer("Phase 6: Event Analytics"):
            from src.tables.event_analytics import create_all_event_analytics
            create_all_event_analytics()
        results['phases']['event_analytics'] = time.time() - phase_start
        
        # Phase 7: Shot Chains
        phase_start = time.time()
        with timer("Phase 7: Shot Chains"):
            try:
                from src.chains.shot_chain_builder import build_shot_chains
                build_shot_chains()
            except Exception as e:
                print(f"  ⚠️  Shot chains skipped: {e}")
        results['phases']['shot_chains'] = time.time() - phase_start
        
        # Phase 8: Foreign Keys
        phase_start = time.time()
        with timer("Phase 8: Foreign Keys"):
            from src.core.add_all_fkeys import main as add_fkeys
            add_fkeys()
        results['phases']['foreign_keys'] = time.time() - phase_start
        
        # Phase 9: Extended Tables
        phase_start = time.time()
        with timer("Phase 9: Extended Tables"):
            from src.advanced.extended_tables import create_extended_tables
            create_extended_tables()
        results['phases']['extended_tables'] = time.time() - phase_start
        
        # Phase 10: Post Processing
        phase_start = time.time()
        with timer("Phase 10: Post Processing"):
            try:
                from src.etl.post_etl_processor import main as post_process
                post_process()
            except Exception as e:
                print(f"  ⚠️  Post processing skipped: {e}")
        results['phases']['post_processing'] = time.time() - phase_start
        
        # Phase 11: Event Time Context
        phase_start = time.time()
        with timer("Phase 11: Event Time Context"):
            try:
                from src.advanced.event_time_context import enhance_event_tables
                enhance_event_tables()
            except Exception as e:
                print(f"  ⚠️  Event time context skipped: {e}")
        results['phases']['event_time_context'] = time.time() - phase_start
        
        # Phase 12: QA Tables
        phase_start = time.time()
        with timer("Phase 12: QA Tables"):
            try:
                from src.qa.build_qa_facts import main as build_qa
                build_qa()
            except Exception as e:
                print(f"  ⚠️  QA tables skipped: {e}")
        results['phases']['qa_tables'] = time.time() - phase_start
        
        # Phase 13: V11 Enhancements
        phase_start = time.time()
        with timer("Phase 13: V11 Enhancements"):
            try:
                from src.advanced.v11_enhancements import run_all_enhancements
                run_all_enhancements()
            except Exception as e:
                print(f"  ⚠️  V11 enhancements skipped: {e}")
        results['phases']['v11_enhancements'] = time.time() - phase_start
        
        # Phase 14: XY Tables
        phase_start = time.time()
        with timer("Phase 14: XY Tables"):
            try:
                from src.xy.xy_table_builder import build_all_xy_tables
                build_all_xy_tables()
            except Exception as e:
                print(f"  ⚠️  XY tables skipped: {e}")
        results['phases']['xy_tables'] = time.time() - phase_start
        
        # Phase 15: Macro Stats
        phase_start = time.time()
        with timer("Phase 15: Macro Stats"):
            try:
                from src.tables.macro_stats import create_all_macro_stats
                create_all_macro_stats()
            except Exception as e:
                print(f"  ⚠️  Macro stats skipped: {e}")
        results['phases']['macro_stats'] = time.time() - phase_start
        
    except Exception as e:
        print(f"\n❌ ETL failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    results['total_time'] = time.time() - start_total
    
    # Print summary
    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)
    print(f"Total Time:          {results['total_time']:.2f}s")
    print(f"Games Processed:     {results['games_processed']}")
    if results['games_processed'] > 0:
        print(f"Time per Game:       {results['total_time'] / results['games_processed']:.2f}s")
    print("\nPhase Breakdown:")
    print("-" * 70)
    for phase, duration in sorted(results['phases'].items(), key=lambda x: x[1], reverse=True):
        pct = (duration / results['total_time'] * 100) if results['total_time'] > 0 else 0
        print(f"  {phase:<30} {duration:>8.2f}s ({pct:>5.1f}%)")
    print("=" * 70)
    
    return results


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Benchmark ETL performance',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--baseline', action='store_true',
                        help='Save current run as baseline')
    parser.add_argument('--compare', action='store_true',
                        help='Compare against saved baseline')
    
    args = parser.parse_args()
    
    # Run benchmark
    results = run_benchmark()
    
    if results:
        # Save baseline if requested
        if args.baseline:
            save_baseline(results)
        
        # Compare if requested
        if args.compare:
            baseline = load_baseline()
            compare_results(results, baseline)
        
        # Always save results for reference
        results_file = PROJECT_ROOT / 'data' / f'.etl_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✅ Results saved to {results_file}")
