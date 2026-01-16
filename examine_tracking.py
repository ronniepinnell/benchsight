#!/usr/bin/env python3
"""Examine tracking file structure using project imports."""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Now import pandas (should work if project has it)
try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas not available. Trying to install...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pandas", "openpyxl"], check=False)
    import pandas as pd

file_path = PROJECT_ROOT / 'data/19038_tracking.xlsx'

if not file_path.exists():
    print(f"ERROR: File not found: {file_path}")
    sys.exit(1)

print("="*80)
print(f"EXAMINING: {file_path.name}")
print("="*80)

try:
    xl = pd.ExcelFile(file_path)
    print(f"\nSheets found ({len(xl.sheet_names)}): {xl.sheet_names}")
    
    for sheet_name in xl.sheet_names:
        print("\n" + "="*80)
        print(f"SHEET: '{sheet_name}'")
        print("="*80)
        
        df = pd.read_excel(xl, sheet_name=sheet_name, nrows=5)
        print(f"Shape: {df.shape[0]} rows (showing first 5), {df.shape[1]} columns")
        
        print(f"\nAll columns ({len(df.columns)}):")
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
        
        # Show non-null sample data
        xy_cols = [c for c in df.columns if any(m in c.lower() for m in ['xy', 'puck', 'net', 'video', 'highlight', 'stop'])]
        if xy_cols:
            print(f"\nSample XY/Video data (first non-null rows):")
            sample = df[xy_cols].dropna(how='all').head(3)
            if len(sample) > 0:
                print(sample.to_string())
    
    print("\n" + "="*80)
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
