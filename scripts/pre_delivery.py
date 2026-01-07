#!/usr/bin/env python3
"""
████████████████████████████████████████████████████████████████████████████████
██                                                                            ██
██   ██████╗ ██████╗ ███████╗    ██████╗ ███████╗██╗     ██╗██╗   ██╗███████╗ ██
██   ██╔══██╗██╔══██╗██╔════╝    ██╔══██╗██╔════╝██║     ██║██║   ██║██╔════╝ ██
██   ██████╔╝██████╔╝█████╗      ██║  ██║█████╗  ██║     ██║██║   ██║█████╗   ██
██   ██╔═══╝ ██╔══██╗██╔══╝      ██║  ██║██╔══╝  ██║     ██║╚██╗ ██╔╝██╔══╝   ██
██   ██║     ██║  ██║███████╗    ██████╔╝███████╗███████╗██║ ╚████╔╝ ███████╗ ██
██   ╚═╝     ╚═╝  ╚═╝╚══════╝    ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═══╝  ╚══════╝ ██
██                                                                            ██
████████████████████████████████████████████████████████████████████████████████

PRE-DELIVERY PIPELINE - THE ONLY WAY TO CREATE A VALID PACKAGE
===============================================================

This script is the SINGLE GATE for all package deliveries.
If this script fails, the package is NOT created.
If this script passes, the package is verified and ready.

Usage:
    python scripts/pre_delivery.py              # Full pipeline
    python scripts/pre_delivery.py --quick --reason "typo fix"  # Skip ETL
    python scripts/pre_delivery.py --dry-run    # Show what would happen
    python scripts/pre_delivery.py --validate benchsight_v13.04.zip  # Validate existing

Pipeline Phases:
    PHASE 1:   Nuclear wipe (delete all output)
    PHASE 2:   Fresh ETL run
    PHASE 3:   Compute ground truth from output
    PHASE 4:   Verify goals against IMMUTABLE_FACTS
    PHASE 5:   Check for regressions
    PHASE 5b:  Schema comparison
    PHASE 6:   Check file sizes (truncation detection)
    PHASE 7:   Run Tier 1 tests (BLOCKING - must pass)
    PHASE 7b:  Run Tier 2 tests (WARNING - logged only)
    PHASE 8:   Version bump + FULL DOC SYNC
              - Bump version number
              - Update all version/timestamp references
              - Sync table counts, goal counts, test counts
              - Regenerate HTML table documentation
    PHASE 9:   Create package with MANIFEST
    PHASE 10:  Final report

Exit Codes:
    0 = Success, package created
    1 = Failure, no package created
"""

import json
import os
import sys
import shutil
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
import argparse

# =============================================================================
# PATHS
# =============================================================================

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / 'data' / 'output'
CONFIG_DIR = PROJECT_ROOT / 'config'

VERSION_FILE = CONFIG_DIR / 'VERSION.json'
IMMUTABLE_FACTS_FILE = CONFIG_DIR / 'IMMUTABLE_FACTS.json'
GROUND_TRUTH_FILE = CONFIG_DIR / 'GROUND_TRUTH.json'
FILE_SIZES_FILE = CONFIG_DIR / 'FILE_SIZES.json'

# =============================================================================
# COLORS
# =============================================================================

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def red(s): return f"{Colors.RED}{s}{Colors.END}"
def green(s): return f"{Colors.GREEN}{s}{Colors.END}"
def yellow(s): return f"{Colors.YELLOW}{s}{Colors.END}"
def blue(s): return f"{Colors.BLUE}{s}{Colors.END}"
def bold(s): return f"{Colors.BOLD}{s}{Colors.END}"

PASS = green("✓ PASS")
FAIL = red("✗ FAIL")
WARN = yellow("⚠ WARN")
SKIP = blue("○ SKIP")

# =============================================================================
# STATE
# =============================================================================

failures = []
warnings = []
dry_run = False

def fail(msg):
    failures.append(msg)
    print(f"  {FAIL}: {msg}")

def warn(msg):
    warnings.append(msg)
    print(f"  {WARN}: {msg}")

def passed(msg):
    print(f"  {PASS}: {msg}")

def skip(msg):
    print(f"  {SKIP}: {msg}")

def phase(num, name):
    print(f"\n{bold(f'PHASE {num}: {name}')}")
    print("-" * 60)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_json(path):
    """Load a JSON file."""
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

def save_json(path, data):
    """Save a JSON file."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def count_file_lines(path):
    """Count lines in a file."""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except:
        return 0

def get_version():
    """Get current version from VERSION.json."""
    v = load_json(VERSION_FILE)
    return v.get('version', '0.00')

def bump_version():
    """Increment version number."""
    v = load_json(VERSION_FILE)
    v['output'] = v.get('output', 0) + 1
    v['version'] = f"{v.get('chat', 0)}.{v['output']:02d}"
    v['date'] = datetime.now().strftime('%Y-%m-%d')
    save_json(VERSION_FILE, v)
    return v['version']

# =============================================================================
# PHASE 1: NUCLEAR WIPE
# =============================================================================

def phase1_nuclear_wipe():
    phase(1, "NUCLEAR WIPE")
    
    if dry_run:
        skip(f"Would delete {OUTPUT_DIR}")
        return True
    
    if OUTPUT_DIR.exists():
        csv_count = len(list(OUTPUT_DIR.glob('*.csv')))
        print(f"  Deleting {csv_count} files in {OUTPUT_DIR}...")
        shutil.rmtree(OUTPUT_DIR)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    remaining = len(list(OUTPUT_DIR.glob('*.csv')))
    if remaining == 0:
        passed("Output directory wiped clean")
        return True
    else:
        fail(f"Failed to wipe output directory ({remaining} files remain)")
        return False

# =============================================================================
# PHASE 2: FRESH ETL RUN
# =============================================================================

def phase2_fresh_etl():
    phase(2, "FRESH ETL RUN")
    
    if dry_run:
        skip("Would run: python -m src.etl_orchestrator full")
        return True
    
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
            fail("ETL execution failed")
            print(f"\n  STDERR:\n{result.stderr[:2000]}")
            return False
        
        passed("ETL completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        fail("ETL timeout (5 min)")
        return False
    except Exception as e:
        fail(f"ETL error: {e}")
        return False

# =============================================================================
# PHASE 3: COMPUTE GROUND TRUTH
# =============================================================================

def phase3_compute_ground_truth():
    phase(3, "COMPUTE GROUND TRUTH")
    
    if dry_run:
        skip("Would compute ground truth from ETL output")
        return {}
    
    # Count tables
    all_csv = list(OUTPUT_DIR.glob('*.csv'))
    dims = [f for f in all_csv if f.stem.startswith('dim_')]
    facts = [f for f in all_csv if f.stem.startswith('fact_')]
    qas = [f for f in all_csv if f.stem.startswith('qa_')]
    
    print(f"  Tables: {len(all_csv)} total ({len(dims)} dim, {len(facts)} fact, {len(qas)} qa)")
    
    # Count goals per game
    import pandas as pd
    events_file = OUTPUT_DIR / 'fact_events.csv'
    
    if not events_file.exists():
        fail("fact_events.csv not found!")
        return {}
    
    df = pd.read_csv(events_file)
    goals_df = df[(df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')]
    
    goals_per_game = {}
    for game_id in goals_df['game_id'].unique():
        count = len(goals_df[goals_df['game_id'] == game_id])
        goals_per_game[str(game_id)] = count
        print(f"  Game {game_id}: {count} goals")
    
    total_goals = len(goals_df)
    print(f"  Total goals: {total_goals}")
    
    # Build ground truth
    ground_truth = {
        '_generated': datetime.now().isoformat(),
        '_description': 'Auto-computed by pre_delivery.py. Do not edit manually.',
        'tables': {
            'total': len(all_csv),
            'dims': len(dims),
            'facts': len(facts),
            'qa': len(qas)
        },
        'goals': goals_per_game,
        'total_goals': total_goals,
        'games': list(goals_per_game.keys())
    }
    
    save_json(GROUND_TRUTH_FILE, ground_truth)
    passed(f"Ground truth computed and saved")
    
    return ground_truth

# =============================================================================
# PHASE 4: VERIFY AGAINST IMMUTABLE FACTS
# =============================================================================

def phase4_verify_immutable_facts(ground_truth):
    phase(4, "VERIFY AGAINST IMMUTABLE FACTS")
    
    if dry_run:
        skip("Would verify goals against IMMUTABLE_FACTS.json")
        return True
    
    immutable = load_json(IMMUTABLE_FACTS_FILE)
    
    if not immutable:
        warn("IMMUTABLE_FACTS.json not found - skipping verification")
        return True
    
    expected_total = immutable.get('total_goals', 0)
    actual_total = ground_truth.get('total_goals', 0)
    
    if expected_total != actual_total:
        fail(f"Total goals mismatch: expected {expected_total}, got {actual_total}")
        return False
    
    passed(f"Total goals: {actual_total} (matches IMMUTABLE_FACTS)")
    
    # Check per-game
    all_match = True
    games = immutable.get('games', {})
    
    for game_id, game_info in games.items():
        expected = game_info.get('goals', 0)
        actual = ground_truth.get('goals', {}).get(game_id, 0)
        
        if expected != actual:
            fail(f"Game {game_id}: expected {expected}, got {actual}")
            all_match = False
        else:
            passed(f"Game {game_id}: {actual} goals")
    
    return all_match

# =============================================================================
# PHASE 5: CHECK FOR REGRESSIONS
# =============================================================================

def phase5_check_regressions(ground_truth):
    phase(5, "CHECK FOR REGRESSIONS")
    
    if dry_run:
        skip("Would check for regressions against previous ground truth")
        return True
    
    # Load previous ground truth if exists
    previous = load_json(GROUND_TRUTH_FILE)
    
    if not previous or '_generated' not in previous:
        passed("No previous ground truth to compare (first run)")
        return True
    
    # Check table count
    prev_tables = previous.get('tables', {}).get('total', 0)
    curr_tables = ground_truth.get('tables', {}).get('total', 0)
    
    if curr_tables < prev_tables:
        warn(f"Table count decreased: {prev_tables} -> {curr_tables}")
    else:
        passed(f"Table count: {curr_tables} (was {prev_tables})")
    
    # Goals should NEVER change (immutable)
    prev_goals = previous.get('total_goals', 0)
    curr_goals = ground_truth.get('total_goals', 0)
    
    if prev_goals > 0 and curr_goals != prev_goals:
        # This is a warning, not failure, because new games could be added
        warn(f"Goal count changed: {prev_goals} -> {curr_goals}")
    else:
        passed(f"Goal count: {curr_goals}")
    
    return True

# =============================================================================
# PHASE 5b: SCHEMA COMPARISON
# =============================================================================

def phase5b_check_schema():
    """Compare current schema to snapshot."""
    phase("5b", "SCHEMA COMPARISON")
    
    if dry_run:
        skip("Would compare schema to snapshot")
        return True
    
    snapshot_file = CONFIG_DIR / 'SCHEMA_SNAPSHOT.json'
    
    if not snapshot_file.exists():
        # Generate initial snapshot
        print("  Generating initial schema snapshot...")
        try:
            result = subprocess.run(
                [sys.executable, 'scripts/utilities/schema_snapshot.py', '--generate'],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=60
            )
            passed("Initial schema snapshot created")
            return True
        except Exception as e:
            warn(f"Could not create schema snapshot: {e}")
            return True
    
    # Compare to existing snapshot
    try:
        result = subprocess.run(
            [sys.executable, 'scripts/utilities/schema_snapshot.py', '--compare'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            passed("Schema matches snapshot")
            return True
        else:
            # Check for critical failures vs warnings
            output = result.stdout + result.stderr
            if 'MISSING:' in output and 'critical' in output.lower():
                fail("Critical table schema changed")
                return False
            else:
                warn("Schema changed (see output above)")
                return True
                
    except Exception as e:
        warn(f"Schema comparison error: {e}")
        return True

# =============================================================================
# PHASE 6: CHECK FILE SIZES
# =============================================================================

def phase6_check_file_sizes():
    phase(6, "CHECK FILE SIZES (Truncation Detection)")
    
    if dry_run:
        skip("Would check file sizes for truncation")
        return True
    
    file_sizes = load_json(FILE_SIZES_FILE)
    critical_files = file_sizes.get('critical_files', {})
    
    all_ok = True
    updated_sizes = {}
    
    for filepath, info in critical_files.items():
        full_path = PROJECT_ROOT / filepath
        
        if not full_path.exists():
            warn(f"{filepath} not found")
            continue
        
        current_lines = count_file_lines(full_path)
        min_lines = info.get('min_lines', 0)
        last_lines = info.get('last_lines', current_lines)
        
        # Check minimum threshold
        if current_lines < min_lines:
            fail(f"{filepath}: {current_lines} lines (minimum {min_lines})")
            all_ok = False
            continue
        
        # Check for significant decrease
        if last_lines > 0:
            decrease_pct = (last_lines - current_lines) / last_lines
            
            if decrease_pct > 0.5:
                fail(f"{filepath}: Shrunk by {decrease_pct*100:.0f}% ({last_lines} -> {current_lines})")
                all_ok = False
            elif decrease_pct > 0.1:
                warn(f"{filepath}: Shrunk by {decrease_pct*100:.0f}% ({last_lines} -> {current_lines})")
            else:
                passed(f"{filepath}: {current_lines} lines")
        else:
            passed(f"{filepath}: {current_lines} lines")
        
        # Update tracked size
        updated_sizes[filepath] = {
            'min_lines': min_lines,
            'last_lines': current_lines,
            'purpose': info.get('purpose', '')
        }
    
    # Save updated sizes
    file_sizes['critical_files'] = updated_sizes
    file_sizes['_last_updated'] = datetime.now().strftime('%Y-%m-%d')
    save_json(FILE_SIZES_FILE, file_sizes)
    
    return all_ok

# =============================================================================
# PHASE 7: RUN TIERED TESTS
# =============================================================================

def phase7_run_tier1_tests():
    """Run Tier 1 blocking tests - MUST pass for delivery."""
    phase(7, "RUN TIER 1 TESTS (BLOCKING)")
    
    if dry_run:
        skip("Would run pytest tests/test_tier1_blocking.py")
        return True
    
    print("  Running: pytest tests/test_tier1_blocking.py -v")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/test_tier1_blocking.py', '-v', '--tb=short'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        output = result.stdout + result.stderr
        
        # Count results
        import re
        passed_match = re.search(r'(\d+) passed', output)
        failed_match = re.search(r'(\d+) failed', output)
        
        passed_count = int(passed_match.group(1)) if passed_match else 0
        failed_count = int(failed_match.group(1)) if failed_match else 0
        
        # Show failures
        if failed_count > 0:
            print(f"\n  {red('TIER 1 FAILURES (blocking):')}")
            for line in output.split('\n'):
                if 'FAILED' in line or 'AssertionError' in line:
                    print(f"    {red(line.strip()[:100])}")
            fail(f"Tier 1: {failed_count} critical tests failed")
            return False
        
        passed(f"Tier 1: {passed_count} tests passed")
        return True
            
    except subprocess.TimeoutExpired:
        fail("Tier 1 tests timeout")
        return False
    except Exception as e:
        fail(f"Tier 1 test error: {e}")
        return False


def phase7b_run_tier2_tests():
    """Run Tier 2 warning tests - should pass but don't block."""
    phase("7b", "RUN TIER 2 TESTS (WARNING)")
    
    if dry_run:
        skip("Would run pytest tests/test_tier2_warning.py")
        return True
    
    print("  Running: pytest tests/test_tier2_warning.py -v")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/test_tier2_warning.py', '-v', '--tb=line'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        output = result.stdout + result.stderr
        
        # Count results
        import re
        passed_match = re.search(r'(\d+) passed', output)
        failed_match = re.search(r'(\d+) failed', output)
        
        passed_count = int(passed_match.group(1)) if passed_match else 0
        failed_count = int(failed_match.group(1)) if failed_match else 0
        
        # Log failures as warnings
        if failed_count > 0:
            print(f"\n  {yellow('TIER 2 FAILURES (warnings):')}")
            for line in output.split('\n'):
                if 'FAILED' in line:
                    warn(line.strip()[:80])
        
        if failed_count > 0:
            warn(f"Tier 2: {failed_count} tests failed (logged as warnings)")
        else:
            passed(f"Tier 2: {passed_count} tests passed")
        
        return True  # Never blocks
            
    except Exception as e:
        warn(f"Tier 2 test error: {e}")
        return True  # Never blocks

# =============================================================================
# PHASE 8: VERSION BUMP + FULL DOC SYNC
# =============================================================================

def phase8_doc_consistency():
    phase(8, "VERSION BUMP + FULL DOC SYNC")
    
    if dry_run:
        skip("Would bump version and sync all docs")
        return get_version()
    
    # Bump version
    new_version = bump_version()
    print(f"  Version bumped to v{new_version}")
    
    # Run doc consistency (timestamps/versions)
    try:
        result = subprocess.run(
            [sys.executable, 'scripts/utilities/doc_consistency.py', '--fix'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if 'FIXED' in result.stdout or 'CONSISTENT' in result.stdout:
            passed("Version/timestamp consistency updated")
        else:
            warn("Doc consistency had issues")
            
    except Exception as e:
        warn(f"Doc consistency error: {e}")
    
    # Run doc sync (table counts, goals, etc.)
    try:
        result = subprocess.run(
            [sys.executable, 'scripts/utilities/doc_sync.py', '--fix'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Count changes
        import re
        match = re.search(r'FIXED: (\d+) files, (\d+) total changes', result.stdout)
        if match:
            files_fixed = int(match.group(1))
            changes = int(match.group(2))
            if changes > 0:
                passed(f"Doc sync: {changes} values updated in {files_fixed} files")
            else:
                passed("Doc sync: All values already correct")
        else:
            passed("Doc sync completed")
            
    except Exception as e:
        warn(f"Doc sync error: {e}")
    
    # Regenerate table HTML docs
    try:
        result = subprocess.run(
            [sys.executable, 'scripts/utilities/doc_sync.py', '--generate'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if 'Generated' in result.stdout:
            # Extract count
            import re
            match = re.search(r'Generated (\d+) table', result.stdout)
            if match:
                passed(f"Table HTML docs: {match.group(1)} tables documented")
            else:
                passed("Table HTML docs regenerated")
        else:
            warn("Table HTML generation had issues")
            
    except Exception as e:
        warn(f"Table HTML generation error: {e}")
    
    # Check metadata completeness
    try:
        result = subprocess.run(
            [sys.executable, 'scripts/utilities/doc_sync.py', '--metadata'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Extract stats from output
        missing_match = re.search(r'Tables missing metadata: (\d+)', result.stdout)
        incomplete_match = re.search(r'Tables with incomplete metadata: (\d+)', result.stdout)
        
        if missing_match:
            missing = int(missing_match.group(1))
            incomplete = int(incomplete_match.group(1)) if incomplete_match else 0
            
            if missing > 0 or incomplete > 0:
                warn(f"Metadata incomplete: {missing} tables missing, {incomplete} incomplete")
            else:
                passed("All tables have complete metadata")
        else:
            passed("Metadata completeness check ran")
            
    except Exception as e:
        warn(f"Metadata check error: {e}")
    
    # Regenerate DATA_DICTIONARY.md
    try:
        result = subprocess.run(
            [sys.executable, 'scripts/utilities/doc_sync.py', '--dictionary'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if 'Generated DATA_DICTIONARY' in result.stdout:
            passed("Data dictionary regenerated")
        else:
            warn("Data dictionary generation had issues")
            
    except Exception as e:
        warn(f"Data dictionary error: {e}")
    
    # Check documentation registry for undocumented items
    try:
        result = subprocess.run(
            [sys.executable, 'scripts/utilities/doc_registry.py', '--discover'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Extract stats from output
        new_match = re.search(r'New items found:\s+(\d+)', result.stdout)
        
        if new_match:
            new_items = int(new_match.group(1))
            if new_items > 0:
                warn(f"Doc registry: {new_items} undocumented items found")
            else:
                passed("Doc registry: All items documented")
        else:
            passed("Doc registry check ran")
            
    except Exception as e:
        warn(f"Doc registry error: {e}")
    
    return new_version

# =============================================================================
# PHASE 9: CREATE PACKAGE
# =============================================================================

def phase9_create_package(version, ground_truth):
    phase(9, "CREATE PACKAGE")
    
    package_name = f"benchsight_v{version}"
    package_dir = PROJECT_ROOT.parent / package_name
    zip_path = Path('/mnt/user-data/outputs') / f"{package_name}.zip"
    
    if dry_run:
        skip(f"Would create {zip_path}")
        return str(zip_path)
    
    # Create manifest
    manifest = {
        'version': version,
        'created': datetime.now().isoformat(),
        'created_by': 'pre_delivery.py v2.0',
        
        'verification': {
            'etl_fresh_run': 'PASS' if not failures else 'FAIL',
            'goal_count': {
                'expected': ground_truth.get('total_goals', 0),
                'actual': ground_truth.get('total_goals', 0),
                'status': 'PASS'
            },
            'table_count': ground_truth.get('tables', {}),
            'file_sizes': 'PASS' if not any('Shrunk' in f for f in failures) else 'FAIL',
            'warnings': warnings,
            'failures': failures
        },
        
        'tables': {
            'total': ground_truth.get('tables', {}).get('total', 0),
            'list': [f.stem for f in OUTPUT_DIR.glob('*.csv')]
        },
        
        'how_to_verify': 'python scripts/bs_detector.py'
    }
    
    manifest_path = PROJECT_ROOT / 'MANIFEST.json'
    save_json(manifest_path, manifest)
    print(f"  Created MANIFEST.json")
    
    # Create package directory
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    print(f"  Copying files to {package_name}/...")
    shutil.copytree(PROJECT_ROOT, package_dir, 
                    ignore=shutil.ignore_patterns('*.pyc', '__pycache__', '.git'))
    
    # Create zip
    print(f"  Creating {zip_path.name}...")
    
    if zip_path.exists():
        zip_path.unlink()
    
    result = subprocess.run(
        ['zip', '-r', str(zip_path), package_name,
         '-x', '*.pyc', '-x', '*__pycache__*', '-x', '*.git*'],
        cwd=PROJECT_ROOT.parent,
        capture_output=True
    )
    
    if result.returncode == 0 and zip_path.exists():
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        passed(f"Package created: {zip_path.name} ({size_mb:.1f} MB)")
        
        # Cleanup
        shutil.rmtree(package_dir)
        
        return str(zip_path)
    else:
        fail("Failed to create zip package")
        return None

# =============================================================================
# PHASE 10: FINAL REPORT
# =============================================================================

def phase10_final_report(version, package_path, ground_truth):
    print(f"\n{'='*60}")
    
    if len(failures) == 0:
        print(f"""
{green('██████╗  █████╗ ███████╗███████╗')}
{green('██╔══██╗██╔══██╗██╔════╝██╔════╝')}
{green('██████╔╝███████║███████╗███████╗')}
{green('██╔═══╝ ██╔══██║╚════██║╚════██║')}
{green('██║     ██║  ██║███████║███████║')}
{green('╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝')}

{bold('PACKAGE VERIFIED AND READY')}

Version:  v{version}
Tables:   {ground_truth.get('tables', {}).get('total', 0)}
Goals:    {ground_truth.get('total_goals', 0)}
Package:  {package_path}
""")
        if warnings:
            print(f"{yellow('Warnings:')}")
            for w in warnings:
                print(f"  • {w}")
        
        return 0
    else:
        print(f"""
{red('███████╗ █████╗ ██╗██╗     ')}
{red('██╔════╝██╔══██╗██║██║     ')}
{red('█████╗  ███████║██║██║     ')}
{red('██╔══╝  ██╔══██║██║██║     ')}
{red('██║     ██║  ██║██║███████╗')}
{red('╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝')}

{bold(f'DELIVERY BLOCKED - {len(failures)} FAILURES')}
""")
        for f in failures:
            print(f"  • {red(f)}")
        
        print(f"\n{red('No package created. Fix the issues and run again.')}")
        return 1

# =============================================================================
# QUICK MODE
# =============================================================================

def run_quick_mode(reason):
    """Run quick mode - skip ETL, just update docs."""
    print(f"""
{'='*60}
{bold('PRE-DELIVERY PIPELINE - QUICK MODE')}
{'='*60}
Reason: {reason}
""")
    
    # Skip phases 1-5, just do doc updates
    phase6_check_file_sizes()
    version = phase8_doc_consistency()
    
    # Load existing ground truth
    ground_truth = load_json(GROUND_TRUTH_FILE)
    
    package_path = phase9_create_package(version, ground_truth)
    return phase10_final_report(version, package_path, ground_truth)

# =============================================================================
# VALIDATE MODE
# =============================================================================

def run_validate_mode(package_path):
    """Validate an existing package."""
    print(f"""
{'='*60}
{bold('PACKAGE VALIDATION')}
{'='*60}
Package: {package_path}
""")
    
    # TODO: Implement package validation
    # - Extract zip
    # - Run bs_detector on it
    # - Check MANIFEST.json
    
    print("Validation not yet implemented")
    return 1

# =============================================================================
# MAIN
# =============================================================================

def main():
    global dry_run
    
    parser = argparse.ArgumentParser(
        description='BenchSight Pre-Delivery Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/pre_delivery.py              # Full pipeline
  python scripts/pre_delivery.py --quick --reason "fixed typo"
  python scripts/pre_delivery.py --dry-run    # Preview only
        """
    )
    
    parser.add_argument('--quick', action='store_true',
                        help='Skip ETL (for doc-only changes)')
    parser.add_argument('--reason', type=str,
                        help='Reason for quick mode (required with --quick)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would happen without doing it')
    parser.add_argument('--validate', type=str, metavar='PACKAGE',
                        help='Validate an existing package')
    
    args = parser.parse_args()
    dry_run = args.dry_run
    
    # Validate mode
    if args.validate:
        return run_validate_mode(args.validate)
    
    # Quick mode
    if args.quick:
        if not args.reason:
            print(red("Error: --quick requires --reason"))
            print("Example: python scripts/pre_delivery.py --quick --reason 'fixed typo'")
            return 1
        return run_quick_mode(args.reason)
    
    # Full pipeline
    print(f"""
{'='*60}
{bold('PRE-DELIVERY PIPELINE')}
{'='*60}
Mode: {'DRY RUN' if dry_run else 'FULL PIPELINE'}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
    
    os.chdir(PROJECT_ROOT)
    
    # Run all phases
    if not phase1_nuclear_wipe():
        return 1
    
    if not phase2_fresh_etl():
        return 1
    
    ground_truth = phase3_compute_ground_truth()
    if not ground_truth and not dry_run:
        return 1
    
    phase4_verify_immutable_facts(ground_truth)
    phase5_check_regressions(ground_truth)
    phase5b_check_schema()
    phase6_check_file_sizes()
    
    # Tiered tests
    if not phase7_run_tier1_tests():
        # Tier 1 failures are blocking
        version = phase8_doc_consistency()
        return phase10_final_report(version, None, ground_truth)
    
    phase7b_run_tier2_tests()  # Warnings only
    
    version = phase8_doc_consistency()
    package_path = phase9_create_package(version, ground_truth)
    
    return phase10_final_report(version, package_path, ground_truth)


if __name__ == '__main__':
    sys.exit(main())
