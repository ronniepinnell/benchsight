#!/usr/bin/env python3
"""
Run this script to automatically fix the ETL error.
It will find base_etl.py and fix line 5099.
"""

import re
import sys
from pathlib import Path
import os

def find_and_fix():
    # Search for the file
    search_dirs = [
        Path.cwd(),
        Path.cwd().parent,
        Path(__file__).parent,
    ]
    
    file_path = None
    for search_dir in search_dirs:
        candidate = search_dir / 'src' / 'core' / 'base_etl.py'
        if candidate.exists():
            file_path = candidate
            break
        
        # Also search recursively
        for root, dirs, files in os.walk(search_dir):
            if 'base_etl.py' in files:
                candidate = Path(root) / 'base_etl.py'
                if 'core' in str(candidate) or 'src' in str(candidate):
                    file_path = candidate
                    break
            if file_path:
                break
        if file_path:
            break
    
    if not file_path:
        print("ERROR: Could not find base_etl.py")
        print("\nPlease run this from your project root directory.")
        print("Or manually edit src/core/base_etl.py at line 5099:")
        print("\n  Find:")
        print("    sp = sp.merge(shifts_for_merge[all_pull_cols], ...)")
        print("\n  Replace with:")
        print("    # Filter all_pull_cols to only existing columns")
        print("    existing_pull_cols = [col for col in all_pull_cols if col in shifts_for_merge.columns]")
        print("    sp = sp.merge(shifts_for_merge[existing_pull_cols], ...)")
        return False
    
    print(f"Found: {file_path}")
    
    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and fix
    fixed = False
    for i, line in enumerate(lines):
        if 'shifts_for_merge[all_pull_cols]' in line and 'merge' in line.lower():
            if 'existing_pull_cols' in line:
                print("✓ Already fixed!")
                return True
            
            # Create backup
            backup = file_path.with_suffix('.py.backup')
            print(f"Creating backup: {backup}")
            with open(backup, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            # Fix
            indent = ' ' * (len(line) - len(line.lstrip()))
            fixed_line = line.replace('all_pull_cols', 'existing_pull_cols')
            
            lines[i] = f"{indent}# Filter all_pull_cols to only existing columns\n{indent}existing_pull_cols = [col for col in all_pull_cols if col in shifts_for_merge.columns]\n{fixed_line}"
            
            # Write
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"✓ Fixed line {i+1}!")
            print(f"Backup: {backup}")
            fixed = True
            break
    
    if not fixed:
        print("ERROR: Could not find the line to fix")
        return False
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("Fixing ETL Error: Rating Columns")
    print("=" * 60)
    print()
    
    if find_and_fix():
        print("\n" + "=" * 60)
        print("✓ SUCCESS! You can now run the ETL again.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ FAILED - Please apply fix manually")
        print("=" * 60)
        sys.exit(1)
