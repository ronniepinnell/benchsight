#!/usr/bin/env python3
"""
Examine 19038_tracking.xlsx file structure.

Run this from project root with project's Python environment:
    python scripts/examine_19038_tracking.py
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas not available. Please run with project's Python environment.")
    print("Try: python scripts/examine_19038_tracking.py")
    sys.exit(1)

file_path = PROJECT_ROOT / 'data/19038_tracking.xlsx'

if not file_path.exists():
    print(f"ERROR: File not found: {file_path}")
    sys.exit(1)

print("="*80)
print(f"EXAMINING: {file_path.name}")
print("="*80)

try:
    xl = pd.ExcelFile(file_path)
    print(f"\nSheets found ({len(xl.sheet_names)}): {xl.sheet_names}\n")
    
    for sheet_name in xl.sheet_names:
        print("="*80)
        print(f"SHEET: '{sheet_name}'")
        print("="*80)
        
        df = pd.read_excel(xl, sheet_name=sheet_name, nrows=5)
        print(f"Shape: {df.shape[0]} rows (showing first 5), {df.shape[1]} columns\n")
        
        print(f"All columns ({len(df.columns)}):")
        for i, col in enumerate(df.columns, 1):
            markers = []
            if 'xy' in col.lower(): markers.append('XY')
            if 'puck' in col.lower(): markers.append('PUCK')
            if 'player' in col.lower(): markers.append('PLAYER')
            if 'net' in col.lower(): markers.append('NET')
            if 'video' in col.lower(): markers.append('VIDEO')
            if 'highlight' in col.lower(): markers.append('HIGHLIGHT')
            if 'adjusted' in col.lower(): markers.append('ADJ')
            if 'stop' in col.lower(): markers.append('STOP')
            marker = ' [' + ', '.join(markers) + ']' if markers else ''
            print(f"  {i:3d}. {col}{marker}")
        
        # Show sample data for XY/Video columns
        xy_cols = [c for c in df.columns if any(m in c.lower() for m in ['xy', 'puck', 'net', 'video', 'highlight', 'stop'])]
        if xy_cols:
            print(f"\nSample XY/Video data (first 3 non-null rows):")
            sample = df[xy_cols].dropna(how='all').head(3)
            if len(sample) > 0:
                for idx, row in sample.iterrows():
                    print(f"\n  Row {idx}:")
                    for col in xy_cols:
                        val = row.get(col)
                        if pd.notna(val) and str(val).strip():
                            print(f"    {col}: {val}")
        print()
    
    print("="*80)
    print("EXAMINATION COMPLETE")
    print("="*80)
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
