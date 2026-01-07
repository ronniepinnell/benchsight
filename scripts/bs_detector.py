#!/usr/bin/env python3
"""
██████╗ ███████╗    ██████╗ ███████╗████████╗███████╗ ██████╗████████╗ ██████╗ ██████╗ 
██╔══██╗██╔════╝    ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗
██████╔╝███████╗    ██║  ██║█████╗     ██║   █████╗  ██║        ██║   ██║   ██║██████╔╝
██╔══██╗╚════██║    ██║  ██║██╔══╝     ██║   ██╔══╝  ██║        ██║   ██║   ██║██╔══██╗
██████╔╝███████║    ██████╔╝███████╗   ██║   ███████╗╚██████╗   ██║   ╚██████╔╝██║  ██║
╚═════╝ ╚══════╝    ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝

BS DETECTOR - Verifies ETL produces correct output from scratch.

LOCATION: scripts/bs_detector.py

PURPOSE:
    Deletes all output, runs ETL fresh, verifies against ground truth.
    If this script fails, the ETL is broken - regardless of what anyone claims.

USAGE:
    python scripts/bs_detector.py

EXIT CODES:
    0 = PASS (ETL works correctly)
    1 = FAIL (ETL is broken)

=============================================================================
FOR LLMs: HOW TO UPDATE THIS FILE
=============================================================================

When to update GROUND_TRUTH:
    1. New game added         → Add game_id to 'games' list, add goal count
    2. Table count changes    → Update 'tables', 'dims', 'facts', 'qa' counts
    3. Goal counts verified   → Update 'goals' dict with per-game counts

How to get correct values:
    
    # Count tables after fresh ETL run:
    ls data/output/*.csv | wc -l                    # total
    ls data/output/dim_*.csv | wc -l                # dims
    ls data/output/fact_*.csv | wc -l               # facts  
    ls data/output/qa_*.csv | wc -l                 # qa

    # Count goals per game from RAW data (not ETL output):
    python -c "
    import pandas as pd
    for gid in [18969, 18977, 18981, 18987]:  # Add new game IDs here
        df = pd.read_excel(f'data/raw/games/{gid}/{gid}_tracking.xlsx', sheet_name='events')
        goals = df[(df['event_type_']=='Goal') & (df['event_detail_']=='Goal_Scored')]
        unique = goals['event_index_'].nunique()
        print(f'{gid}: {unique} goals')
    "

    # Verify noradhockey.com matches (manual check)

CRITICAL: Always verify goal counts from RAW source data, not ETL output!
=============================================================================
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# =============================================================================
# GROUND TRUTH - UPDATE THESE VALUES WHEN DATA CHANGES
# =============================================================================
# Last updated: 2025-01-07
# Verified by: Running against raw tracking.xlsx files
#
# TO UPDATE: See instructions in docstring above
# =============================================================================

GROUND_TRUTH = {
    # Table counts (from fresh ETL run - VERIFIED 2026-01-07)
    # Run: ls data/output/*.csv | wc -l
    'tables': 59,       # Actual count from fresh ETL
    'dims': 33,         # ls data/output/dim_*.csv | wc -l
    'facts': 24,        # ls data/output/fact_*.csv | wc -l
    'qa': 2,            # ls data/output/qa_*.csv | wc -l
    
    # Games tracked (add new game IDs here)
    'games': [18969, 18977, 18981, 18987],
    
    # Goals per game (from raw tracking.xlsx, NOT ETL output)
    # These are UNIQUE event counts (event_index_), not row counts
    'goals': {
        18969: 7,   # Verified from 18969_tracking.xlsx events sheet
        18977: 6,   # Verified from 18977_tracking.xlsx events sheet  
        18981: 3,   # Verified from 18981_tracking.xlsx events sheet
        18987: 1,   # Verified from 18987_tracking.xlsx events sheet
    },
    'total_goals': 17,  # Sum of above
    
    # Minimum passing tests (may have some skipped/xfail)
    'tests_min': 15,
}

# =============================================================================
# SCRIPT LOGIC - DO NOT MODIFY UNLESS FIXING BUGS
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'data' / 'output'

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BOLD = '\033[1m'
    END = '\033[0m'

def red(s): return f"{Colors.RED}{s}{Colors.END}"
def green(s): return f"{Colors.GREEN}{s}{Colors.END}"
def yellow(s): return f"{Colors.YELLOW}{s}{Colors.END}"
def bold(s): return f"{Colors.BOLD}{s}{Colors.END}"

PASS = green("✓ PASS")
FAIL = red("✗ FAIL")

failures = []

def check(name, condition, expected=None, actual=None):
    """Record a check result."""
    if condition:
        print(f"  {PASS}: {name}")
        return True
    else:
        msg = f"{name}"
        if expected is not None and actual is not None:
            msg += f" (expected {expected}, got {actual})"
        print(f"  {FAIL}: {msg}")
        failures.append(msg)
        return False


def phase1_wipe():
    """Delete all output files for clean slate."""
    print(f"\n{bold('PHASE 1: NUCLEAR WIPE')}")
    print("-" * 50)
    
    if OUTPUT_DIR.exists():
        csv_count = len(list(OUTPUT_DIR.glob('*.csv')))
        print(f"  Deleting {csv_count} files in {OUTPUT_DIR}...")
        shutil.rmtree(OUTPUT_DIR)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    remaining = len(list(OUTPUT_DIR.glob('*.csv')))
    check("Output directory empty", remaining == 0, 0, remaining)


def phase2_run_etl():
    """Run full ETL from scratch."""
    print(f"\n{bold('PHASE 2: RUN ETL FROM SCRATCH')}")
    print("-" * 50)
    print("  Running: python -m src.etl_orchestrator full")
    print("  (This takes 1-2 minutes...)")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'src.etl_orchestrator', 'full'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            print(f"\n  {red('ETL FAILED!')}")
            print(f"  STDERR:\n{result.stderr[:2000]}")
            failures.append("ETL execution failed")
            return False
        
        print(f"  {green('ETL completed')}")
        return True
        
    except subprocess.TimeoutExpired:
        print(f"  {red('ETL TIMEOUT (5 min)')}")
        failures.append("ETL timeout")
        return False
    except Exception as e:
        print(f"  {red(f'ETL ERROR: {e}')}")
        failures.append(f"ETL error: {e}")
        return False


def phase3_verify_tables():
    """Verify correct number of tables generated."""
    print(f"\n{bold('PHASE 3: VERIFY TABLE COUNTS')}")
    print("-" * 50)
    
    all_csv = list(OUTPUT_DIR.glob('*.csv'))
    dims = list(OUTPUT_DIR.glob('dim_*.csv'))
    facts = list(OUTPUT_DIR.glob('fact_*.csv'))
    qas = list(OUTPUT_DIR.glob('qa_*.csv'))
    
    check("Total tables", len(all_csv) == GROUND_TRUTH['tables'], 
          GROUND_TRUTH['tables'], len(all_csv))
    check("Dimension tables", len(dims) == GROUND_TRUTH['dims'], 
          GROUND_TRUTH['dims'], len(dims))
    check("Fact tables", len(facts) == GROUND_TRUTH['facts'], 
          GROUND_TRUTH['facts'], len(facts))
    check("QA tables", len(qas) == GROUND_TRUTH['qa'], 
          GROUND_TRUTH['qa'], len(qas))


def phase4_verify_goals():
    """Verify goal counts match raw source data."""
    print(f"\n{bold('PHASE 4: VERIFY GOAL COUNTS')}")
    print("-" * 50)
    print(f"  {yellow('Goals must be: event_type=Goal AND event_detail=Goal_Scored')}")
    print(f"  {yellow('NOT Shot_Goal (that is the shot, not the goal)')}")
    
    try:
        import pandas as pd
    except ImportError:
        print(f"  {red('pandas not installed')}")
        failures.append("pandas not installed")
        return
    
    events_file = OUTPUT_DIR / 'fact_events.csv'
    if not events_file.exists():
        print(f"  {FAIL}: fact_events.csv not found!")
        failures.append("fact_events.csv missing")
        return
    
    df = pd.read_csv(events_file)
    
    total_goals = 0
    for game_id, expected_goals in GROUND_TRUTH['goals'].items():
        actual = len(df[
            (df['game_id'] == game_id) & 
            (df['event_type'] == 'Goal') & 
            (df['event_detail'] == 'Goal_Scored')
        ])
        total_goals += actual
        check(f"Game {game_id} goals", actual == expected_goals, expected_goals, actual)
    
    check("Total goals (all games)", total_goals == GROUND_TRUTH['total_goals'], 
          GROUND_TRUTH['total_goals'], total_goals)


def phase5_run_tests():
    """Run pytest and verify minimum pass count."""
    print(f"\n{bold('PHASE 5: RUN PYTEST')}")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=line', '-q'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        output = result.stdout + result.stderr
        
        # Count passed tests
        import re
        match = re.search(r'(\d+) passed', output)
        passed = int(match.group(1)) if match else 0
        
        # Show any failures
        for line in output.split('\n'):
            if 'FAILED' in line:
                print(f"  {red(line.strip()[:80])}")
        
        check(f"Tests passed (minimum {GROUND_TRUTH['tests_min']})", 
              passed >= GROUND_TRUTH['tests_min'], 
              f"{GROUND_TRUTH['tests_min']}+", passed)
        
    except Exception as e:
        print(f"  {red(f'Pytest error: {e}')}")
        failures.append("Pytest failed to run")


def phase6_verify_critical_files():
    """Verify critical source files exist."""
    print(f"\n{bold('PHASE 6: VERIFY CRITICAL FILES')}")
    print("-" * 50)
    
    critical_files = [
        'src/etl_orchestrator.py',
        'src/core/base_etl.py',
        'LLM_REQUIREMENTS.md',
    ]
    
    for f in critical_files:
        path = PROJECT_ROOT / f
        check(f"Exists: {f}", path.exists())


def final_verdict():
    """Print final pass/fail verdict."""
    print(f"\n{'='*60}")
    
    if len(failures) == 0:
        print(f"""
{green('██╗     ███████╗ ██████╗ ██╗████████╗')}
{green('██║     ██╔════╝██╔════╝ ██║╚══██╔══╝')}
{green('██║     █████╗  ██║  ███╗██║   ██║   ')}
{green('██║     ██╔══╝  ██║   ██║██║   ██║   ')}
{green('███████╗███████╗╚██████╔╝██║   ██║   ')}
{green('╚══════╝╚══════╝ ╚═════╝ ╚═╝   ╚═╝   ')}

{bold('ETL VERIFIED.')}
Tables: {GROUND_TRUTH['tables']}
Goals: {GROUND_TRUTH['total_goals']}
""")
        return 0
    else:
        print(f"""
{red('███████╗ █████╗ ██╗██╗     ')}
{red('██╔════╝██╔══██╗██║██║     ')}
{red('█████╗  ███████║██║██║     ')}
{red('██╔══╝  ██╔══██║██║██║     ')}
{red('██║     ██║  ██║██║███████╗')}
{red('╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝')}

{bold(f'FAILURES ({len(failures)}):')}
""")
        for f in failures:
            print(f"  • {red(f)}")
        
        print(f"\n{red('ETL is broken. Do not accept any fixes until this passes.')}")
        return 1


def main():
    print(f"""
{'='*60}
{bold('BS DETECTOR v1.0')}
{'='*60}
Location: scripts/bs_detector.py
Purpose: Verify ETL works from scratch

Ground Truth:
  Tables: {GROUND_TRUTH['tables']} ({GROUND_TRUTH['dims']} dim, {GROUND_TRUTH['facts']} fact, {GROUND_TRUTH['qa']} qa)
  Games: {GROUND_TRUTH['games']}
  Goals: {GROUND_TRUTH['total_goals']} total
""")
    
    os.chdir(PROJECT_ROOT)
    
    phase1_wipe()
    
    if not phase2_run_etl():
        return final_verdict()
    
    phase3_verify_tables()
    phase4_verify_goals()
    phase5_run_tests()
    phase6_verify_critical_files()
    
    return final_verdict()


if __name__ == '__main__':
    sys.exit(main())
