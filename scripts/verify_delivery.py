#!/usr/bin/env python3
"""
BenchSight Delivery Verification Script
Run before packaging to ensure all required files are present.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

REQUIRED_FILES = [
    # Documentation
    "docs/HANDOFF.md",
    "docs/PROJECT_REQUIREMENTS.md",
    "docs/VALIDATION_LOG.tsv",
    "docs/REQUEST_LOG.md",
    "docs/VALIDATION_SUMMARY.html",
    "README.md",
    
    # Scripts
    "scripts/validate_stats.py",
    "scripts/verify_delivery.py",
    
    # Core data outputs
    "data/output/fact_events_player.csv",
    "data/output/fact_shifts_player.csv",
    "data/output/fact_gameroster.csv",
    "data/output/dim_player.csv",
    "data/output/dim_team.csv",
    
    # ETL
    "etl.py",
    
    # Config
    "config/settings.py",
]

REQUIRED_DIRS = [
    "docs",
    "data/output",
    "data/raw",
    "scripts",
    "src",
    "sql",
    "dashboard",
    "config",
    "tests",
]

def verify():
    print("=" * 60)
    print("BENCHSIGHT DELIVERY VERIFICATION")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # Check required files
    print("\n📄 Checking required files...")
    for file in REQUIRED_FILES:
        path = BASE_DIR / file
        if path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} MISSING")
            errors.append(f"Missing file: {file}")
    
    # Check required directories
    print("\n📁 Checking required directories...")
    for dir in REQUIRED_DIRS:
        path = BASE_DIR / dir
        if path.exists() and path.is_dir():
            file_count = len(list(path.glob("*")))
            print(f"  ✓ {dir}/ ({file_count} items)")
        else:
            print(f"  ✗ {dir}/ MISSING")
            errors.append(f"Missing directory: {dir}")
    
    # Check validation log
    print("\n📊 Checking validation log...")
    val_log = BASE_DIR / "docs/VALIDATION_LOG.tsv"
    if val_log.exists():
        with open(val_log) as f:
            lines = f.readlines()
            true_count = sum(1 for line in lines if "TRUE" in line)
            print(f"  ✓ {true_count} stats validated")
    
    # Summary
    print("\n" + "=" * 60)
    if errors:
        print(f"❌ FAILED: {len(errors)} errors found")
        for e in errors:
            print(f"   - {e}")
        return False
    else:
        print("✅ PASSED: All checks passed")
        return True

if __name__ == "__main__":
    verify()
