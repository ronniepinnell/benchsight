#!/usr/bin/env python3
"""Detailed examination of tracking file structure."""
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas not available")
    sys.exit(1)

file_path = Path('data/19038_tracking.xlsx')

if not file_path.exists():
    print(f"ERROR: File not found: {file_path}")
    sys.exit(1)

print("="*80)
print(f"EXAMINING: {file_path}")
print("="*80)

try:
    xl = pd.ExcelFile(file_path)
    print(f"\nSheets found: {xl.sheet_names}")
    print(f"Total sheets: {len(xl.sheet_names)}")
    
    for sheet_name in xl.sheet_names:
        print("\n" + "="*80)
        print(f"SHEET: '{sheet_name}'")
        print("="*80)
        
        # Read first few rows
        df = pd.read_excel(xl, sheet_name=sheet_name, nrows=10)
        
        print(f"Shape: {df.shape[0]} rows (showing first 10), {df.shape[1]} columns")
        print(f"\nColumn names ({len(df.columns)} total):")
        
        for i, col in enumerate(df.columns, 1):
            # Check for XY-related columns
            xy_markers = []
            if 'xy' in col.lower():
                xy_markers.append('XY')
            if 'puck' in col.lower():
                xy_markers.append('PUCK')
            if 'player' in col.lower():
                xy_markers.append('PLAYER')
            if 'net' in col.lower():
                xy_markers.append('NET')
            if 'video' in col.lower():
                xy_markers.append('VIDEO')
            if 'highlight' in col.lower():
                xy_markers.append('HIGHLIGHT')
            if 'adjusted' in col.lower():
                xy_markers.append('ADJUSTED')
            if 'stop' in col.lower():
                xy_markers.append('STOP')
            
            marker_str = ' [' + ', '.join(xy_markers) + ']' if xy_markers else ''
            print(f"  {i:3d}. {col}{marker_str}")
        
        # Show sample data for XY-related columns
        xy_cols = [c for c in df.columns if any(marker in c.lower() for marker in ['xy', 'puck', 'player', 'net', 'video', 'highlight', 'stop', 'adjusted'])]
        if xy_cols:
            print(f"\nSample data for XY/Video-related columns (first 3 non-null rows):")
            sample_df = df[xy_cols].dropna(how='all').head(3)
            if len(sample_df) > 0:
                for idx, row in sample_df.iterrows():
                    print(f"\n  Row {idx}:")
                    for col in xy_cols:
                        val = row.get(col)
                        if pd.notna(val) and str(val).strip():
                            print(f"    {col}: {val}")
        
        # Check for is_stop column or point_number patterns
        if 'point' in str(df.columns).lower() or 'stop' in str(df.columns).lower():
            print(f"\nPoint/Stop related columns found:")
            point_cols = [c for c in df.columns if 'point' in c.lower() or 'stop' in c.lower()]
            for col in point_cols:
                non_null = df[col].notna().sum()
                print(f"  {col}: {non_null} non-null values")
                if non_null > 0:
                    print(f"    Sample values: {df[col].dropna().head(3).tolist()}")
    
    print("\n" + "="*80)
    print("EXAMINATION COMPLETE")
    print("="*80)
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
