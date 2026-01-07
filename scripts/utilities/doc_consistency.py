#!/usr/bin/env python3
"""
BenchSight Documentation Consistency System
============================================
Single source of truth for all documentation values.
Auto-updates ALL docs (.md, .html, .mermaid) on every run.

Usage:
    python scripts/utilities/doc_consistency.py              # Check only
    python scripts/utilities/doc_consistency.py --fix        # Auto-fix all docs
    python scripts/utilities/doc_consistency.py --bump       # Increment output (13.02 -> 13.03)
    python scripts/utilities/doc_consistency.py --new-chat   # New chat (13.xx -> 14.01)
    python scripts/utilities/doc_consistency.py --status     # Show current version
    python scripts/utilities/doc_consistency.py --add-banned OLD NEW  # Add banned table

VERSION is stored in config/VERSION.json - that's the ONLY file you need to update.
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# =============================================================================
# PATHS
# =============================================================================

BASE_DIR = Path(__file__).parent.parent.parent  # Project root
VERSION_FILE = BASE_DIR / 'config' / 'VERSION.json'

# =============================================================================
# VERSION MANAGEMENT
# =============================================================================

def load_version():
    """Load version info from VERSION.json."""
    if VERSION_FILE.exists():
        with open(VERSION_FILE) as f:
            return json.load(f)
    else:
        # Default if file doesn't exist
        return {
            "version": "13.02",
            "chat": 13,
            "output": 2,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "tables": {
                "banned": {
                    "fact_events_tracking": "fact_event_players",
                    "fact_shifts_tracking": "fact_shifts",
                    "fact_shifts_player": "fact_shift_players",
                    "fact_player_shifts": "fact_shift_players"
                }
            }
        }

def save_version(version_data):
    """Save version info to VERSION.json."""
    version_data['date'] = datetime.now().strftime("%Y-%m-%d")
    with open(VERSION_FILE, 'w') as f:
        json.dump(version_data, f, indent=4)
    print(f"✓ Updated {VERSION_FILE}")

def bump_output():
    """Increment output number (13.02 -> 13.03)."""
    v = load_version()
    v['output'] += 1
    v['version'] = f"{v['chat']}.{v['output']:02d}"
    save_version(v)
    print(f"Version bumped to v{v['version']}")
    return v

def new_chat():
    """Start new chat (13.xx -> 14.01)."""
    v = load_version()
    v['chat'] += 1
    v['output'] = 1
    v['version'] = f"{v['chat']}.{v['output']:02d}"
    save_version(v)
    print(f"New chat started: v{v['version']}")
    return v

def add_banned_table(old_name, new_name):
    """Add a banned table name mapping."""
    v = load_version()
    v['tables']['banned'][old_name] = new_name
    save_version(v)
    print(f"Added banned table: {old_name} -> {new_name}")

# =============================================================================
# CONFIGURATION - Read from VERSION.json
# =============================================================================

def get_config():
    """Get current configuration from VERSION.json."""
    v = load_version()
    return {
        'version': v['version'],
        'chat': v['chat'],
        'output': v['output'],
        'next_chat_version': f"{v['chat'] + 1}.01",
        'banned_tables': v.get('tables', {}).get('banned', {})
    }

# Files/patterns to scan
DOC_PATTERNS = ['*.md', '*.html', '*.mermaid', '*.txt']
DOC_DIRS_REL = [
    '',  # Root level
    'docs',
    'docs/html',
    'docs/html/tables',
    'docs/html/diagrams',
    'docs/html/dashboard',
    'docs/html/prototypes',
    'docs/diagrams',
]

# Files to skip entirely
SKIP_FILES = {
    'CHANGELOG.md',
    'CHANGELOG.html',
}

# Files where only table names should be fixed (not versions)
VERSION_HISTORY_FILES = {
    'LLM_REQUIREMENTS.md',
}

# =============================================================================
# VERSION REPLACEMENT PATTERNS
# =============================================================================

def get_version_replacements(config):
    """Generate version replacement patterns based on current config."""
    current = config['version']
    chat = config['chat']
    
    # Build list of old versions to replace
    old_versions = []
    
    # All previous outputs in current chat
    for out in range(1, config['output']):
        old_versions.append(f"{chat}.{out:02d}")
    
    # Previous chats (go back a few)
    for old_chat in range(max(1, chat - 5), chat):
        for out in range(1, 20):  # Assume max 20 outputs per chat
            old_versions.append(f"{old_chat}.{out:02d}")
    
    replacements = {}
    
    for old_ver in old_versions:
        # Version numbers NOT in file paths (no underscore or slash before)
        replacements[rf'(?<![_/])v{re.escape(old_ver)}(?![_/\d])'] = f'v{current}'
        replacements[rf'Version: {re.escape(old_ver)}'] = f'Version: {current}'
        replacements[rf'Version:\s*{re.escape(old_ver)}'] = f'Version: {current}'
    
    # Package name patterns
    for old_chat in range(max(1, chat - 5), chat):
        replacements[rf'benchsight_v{old_chat}(?!\.)'] = f'benchsight_v{chat}'
        replacements[rf'Chat {old_chat}(?!\d)'] = f'Chat {chat}'
    
    return replacements

# =============================================================================
# DYNAMIC VALUES
# =============================================================================

def get_dynamic_values():
    """Get current values from actual CSV files."""
    output_dir = BASE_DIR / 'data' / 'output'
    
    values = {
        'table_count': 0,
        'dim_count': 0,
        'fact_count': 0,
        'qa_count': 0,
        'games_tracked': 0,
    }
    
    if output_dir.exists():
        csv_files = list(output_dir.glob('*.csv'))
        values['table_count'] = len(csv_files)
        values['dim_count'] = len([f for f in csv_files if f.stem.startswith('dim_')])
        values['fact_count'] = len([f for f in csv_files if f.stem.startswith('fact_')])
        values['qa_count'] = len([f for f in csv_files if f.stem.startswith('qa_')])
        
        # Get game count
        events_path = output_dir / 'fact_events.csv'
        if events_path.exists():
            try:
                events = pd.read_csv(events_path, usecols=['game_id'])
                values['games_tracked'] = len(events['game_id'].unique())
            except:
                pass
    
    return values

# =============================================================================
# FILE SCANNING
# =============================================================================

def get_all_doc_files():
    """Get all documentation files to check."""
    files = []
    for rel_dir in DOC_DIRS_REL:
        dir_path = BASE_DIR / rel_dir if rel_dir else BASE_DIR
        if dir_path.exists():
            for pattern in DOC_PATTERNS:
                for f in dir_path.glob(pattern):
                    if f.is_file() and f.name not in SKIP_FILES:
                        files.append(f)
    return files

def check_file(filepath, config, fix=False):
    """Check a single file for issues. Optionally fix them."""
    issues = []
    
    try:
        content = filepath.read_text(encoding='utf-8', errors='ignore')
        original_content = content
    except Exception as e:
        return [f"Could not read {filepath}: {e}"]
    
    # Check for banned table names (always)
    for banned, replacement in config['banned_tables'].items():
        if banned in content:
            issues.append(f"  {filepath.name}: Contains banned '{banned}' -> '{replacement}'")
            if fix:
                content = content.replace(banned, replacement)
    
    # Check for old versions (skip certain files)
    if filepath.name not in SKIP_FILES and filepath.name not in VERSION_HISTORY_FILES:
        for old_pattern, new_value in get_version_replacements(config).items():
            matches = re.findall(old_pattern, content)
            if matches:
                issues.append(f"  {filepath.name}: Contains old version pattern")
                if fix:
                    content = re.sub(old_pattern, new_value, content)
    
    # Write fixes
    if fix and content != original_content:
        try:
            filepath.write_text(content, encoding='utf-8')
            issues.append(f"  ✓ FIXED: {filepath.name}")
        except Exception as e:
            issues.append(f"  ✗ Could not write {filepath}: {e}")
    
    return issues

def check_all_docs(fix=False, verbose=False):
    """Check all documentation files."""
    config = get_config()
    
    print("=" * 70)
    print("BENCHSIGHT DOCUMENTATION CONSISTENCY CHECK")
    print("=" * 70)
    print(f"Current Version: v{config['version']} (Chat {config['chat']}, Output {config['output']})")
    print(f"Mode: {'AUTO-FIX' if fix else 'CHECK ONLY'}")
    print()
    
    values = get_dynamic_values()
    print(f"Detected: {values['table_count']} tables, {values['games_tracked']} games")
    print()
    
    files = get_all_doc_files()
    print(f"Scanning {len(files)} documentation files...")
    print()
    
    all_issues = []
    files_with_issues = 0
    
    for filepath in files:
        issues = check_file(filepath, config, fix=fix)
        if issues:
            files_with_issues += 1
            all_issues.extend(issues)
            if verbose:
                for issue in issues:
                    print(issue)
    
    print()
    print("=" * 70)
    
    if all_issues:
        fixed = len([i for i in all_issues if '✓ FIXED' in i])
        remaining = len(all_issues) - fixed
        
        if fix:
            print(f"✓ FIXED {fixed} files")
            if remaining > 0:
                print(f"⚠ {remaining} issues noted")
        else:
            print(f"❌ FOUND {len(all_issues)} issues in {files_with_issues} files")
            print()
            print("Run with --fix to auto-repair")
    else:
        print("✅ ALL DOCS CONSISTENT")
    
    print("=" * 70)
    return len([i for i in all_issues if '✗' in i]) == 0

def show_status():
    """Show current version status."""
    config = get_config()
    values = get_dynamic_values()
    
    print("=" * 50)
    print("BENCHSIGHT VERSION STATUS")
    print("=" * 50)
    print(f"Version:     v{config['version']}")
    print(f"Chat:        {config['chat']}")
    print(f"Output:      {config['output']}")
    print(f"Next Chat:   v{config['next_chat_version']}")
    print()
    print(f"Tables:      {values['table_count']}")
    print(f"Games:       {values['games_tracked']}")
    print()
    print("Banned Table Names:")
    for old, new in config['banned_tables'].items():
        print(f"  {old} -> {new}")
    print("=" * 50)

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='BenchSight Documentation Consistency')
    parser.add_argument('--fix', action='store_true', help='Auto-fix issues')
    parser.add_argument('--bump', action='store_true', help='Bump output version (13.02 -> 13.03)')
    parser.add_argument('--new-chat', action='store_true', help='Start new chat (13.xx -> 14.01)')
    parser.add_argument('--status', action='store_true', help='Show version status')
    parser.add_argument('--add-banned', nargs=2, metavar=('OLD', 'NEW'), help='Add banned table name')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.bump:
        bump_output()
        print("\nNow run: python scripts/utilities/doc_consistency.py --fix")
    elif args.new_chat:
        new_chat()
        print("\nNow run: python scripts/utilities/doc_consistency.py --fix")
    elif args.add_banned:
        add_banned_table(args.add_banned[0], args.add_banned[1])
        print("\nNow run: python scripts/utilities/doc_consistency.py --fix")
    elif args.status:
        show_status()
    else:
        success = check_all_docs(fix=args.fix, verbose=args.verbose or args.fix)
        sys.exit(0 if success else 1)
