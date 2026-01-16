#!/usr/bin/env python3
"""Quick script to examine tracking file structure."""
import pandas as pd
import sys
from pathlib import Path

file_path = Path('data/19038_tracking.xlsx')

if not file_path.exists():
    print(f"File not found: {file_path}")
    sys.exit(1)

xl = pd.ExcelFile(file_path)
print(f"File: {file_path}")
print(f"Sheets: {xl.sheet_names}")
print("\n" + "="*70)

for sheet in xl.sheet_names:
    print(f"\n=== SHEET: {sheet} ===")
    df = pd.read_excel(xl, sheet_name=sheet, nrows=5)
    print(f"Shape: {df.shape[0]} rows (showing first 5), {df.shape[1]} columns")
    print(f"\nColumns:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i:2d}. {col}")
    
    # Show sample XY-related columns
    xy_cols = [c for c in df.columns if 'xy' in c.lower() or 'x_' in c.lower() or 'y_' in c.lower() or 'puck' in c.lower() or 'player' in c.lower() or 'net' in c.lower()]
    if xy_cols:
        print(f"\n  XY-related columns: {xy_cols[:10]}")
    
    print()
