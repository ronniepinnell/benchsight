#!/usr/bin/env python3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import pandas (will fail if not available, but try project imports first)
try:
    import pandas as pd
except ImportError:
    try:
        # Try importing from existing ETL which has pandas
        from src.core.base_etl import pd
    except:
        print("ERROR: pandas not available")
        sys.exit(1)

file_path = PROJECT_ROOT / 'data/19038_tracking.xlsx'

if not file_path.exists():
    print(f"ERROR: File not found: {file_path}")
    sys.exit(1)

print("="*80)
print(f"EXAMINING: {file_path.name}")
print("="*80)

xl = pd.ExcelFile(file_path)
print(f"\nSheets: {xl.sheet_names}\n")

for sheet_name in xl.sheet_names:
    print("="*80)
    print(f"SHEET: '{sheet_name}'")
    print("="*80)
    
    df = pd.read_excel(xl, sheet_name=sheet_name, nrows=3)
    print(f"Rows: {df.shape[0]} (showing 3), Columns: {df.shape[1]}\n")
    
    print("All columns:")
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
        marker = ' [' + ','.join(markers) + ']' if markers else ''
        print(f"  {i:3d}. {col}{marker}")
    
    # Show XY/Video sample data
    xy_cols = [c for c in df.columns if any(m in c.lower() for m in ['xy', 'puck', 'net', 'video', 'highlight', 'stop'])]
    if xy_cols and len(df) > 0:
        print(f"\nSample XY/Video data:")
        for idx in range(min(3, len(df))):
            row = df.iloc[idx]
            has_data = False
            for col in xy_cols:
                val = row.get(col)
                if pd.notna(val) and str(val).strip() and str(val) != 'nan':
                    if not has_data:
                        print(f"  Row {idx}:")
                        has_data = True
                    print(f"    {col}: {val}")
    print()

print("="*80)
