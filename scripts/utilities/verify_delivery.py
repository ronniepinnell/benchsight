#!/usr/bin/env python3
"""
BenchSight Delivery Verification Script
Run before packaging to ensure all required files are present.

This script:
1. Checks required files exist
2. Checks required directories exist
3. Runs doc consistency check (table names, versions)
4. Validates outputs
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent  # Project root

REQUIRED_FILES = [
    # Documentation
    "docs/HONEST_ASSESSMENT.md",
    "docs/DATA_DICTIONARY.md",
    "README.md",
    "LLM_REQUIREMENTS.md",
    "MASTER_GUIDE.md",
    
    # Core data outputs
    "data/output/fact_event_players.csv",
    "data/output/fact_shift_players.csv",
    "data/output/fact_shifts.csv",
    "data/output/fact_events.csv",
    "data/output/fact_gameroster.csv",
    "data/output/dim_player.csv",
    "data/output/dim_team.csv",
    
    # ETL
    "run_etl.py",
    
    # Config
    "config/settings.py",
    
    # Tests
    "tests/test_etl.py",
]

REQUIRED_DIRS = [
    "docs",
    "docs/html",
    "docs/html/tables",
    "data/output",
    "data/raw",
    "scripts",
    "src",
    "config",
    "tests",
]

def check_doc_consistency():
    """Run the doc consistency checker."""
    print("\n📝 Checking documentation consistency...")
    
    # Import and run the doc consistency module
    try:
        sys.path.insert(0, str(BASE_DIR / 'scripts' / 'utilities'))
        from doc_consistency import get_config
        
        config = get_config()
        banned_tables = config.get('banned_tables', {})
        
        # Check for banned table names in docs
        errors = []
        doc_dirs = [BASE_DIR, BASE_DIR / 'docs']
        
        for dir_path in doc_dirs:
            if not dir_path.exists():
                continue
            for pattern in ['*.md', '*.html', '*.mermaid']:
                for f in dir_path.rglob(pattern):
                    if f.name == 'CHANGELOG.md':
                        continue
                    try:
                        content = f.read_text(encoding='utf-8', errors='ignore')
                        for banned in banned_tables:
                            if banned in content:
                                errors.append(f"  ✗ {f.relative_to(BASE_DIR)}: Contains banned '{banned}'")
                    except:
                        pass
        
        if errors:
            print("  ❌ Found banned table names in docs:")
            for e in errors[:10]:
                print(e)
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more")
            print("\n  Run: python scripts/utilities/doc_consistency.py --fix")
            return False
        else:
            print(f"  ✓ No banned table names found (v{config['version']})")
            return True
            
    except ImportError as e:
        print(f"  ⚠ Could not import doc_consistency: {e}")
        return True  # Don't fail if module not found

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
    
    # Check doc consistency
    if not check_doc_consistency():
        errors.append("Documentation contains banned table names")
    
    # Check table count
    print("\n📊 Checking data outputs...")
    output_dir = BASE_DIR / "data" / "output"
    if output_dir.exists():
        csv_count = len(list(output_dir.glob("*.csv")))
        print(f"  ✓ {csv_count} CSV tables in data/output/")
        if csv_count < 50:
            warnings.append(f"Only {csv_count} tables (expected 60+)")
    
    # Summary
    print("\n" + "=" * 60)
    if errors:
        print(f"❌ FAILED: {len(errors)} errors found")
        for e in errors:
            print(f"   - {e}")
        return False
    elif warnings:
        print(f"⚠️  PASSED WITH WARNINGS: {len(warnings)} warnings")
        for w in warnings:
            print(f"   - {w}")
        return True
    else:
        print("✅ PASSED: All checks passed")
        return True

if __name__ == "__main__":
    success = verify()
    sys.exit(0 if success else 1)
