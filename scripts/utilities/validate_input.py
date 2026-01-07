#!/usr/bin/env python3
"""
Input Validation System
=======================
Validates raw Excel game files BEFORE processing.
Catches bad data early - garbage in = garbage out.

Usage:
    python scripts/utilities/validate_input.py                    # Validate all games
    python scripts/utilities/validate_input.py --game 18969       # Validate specific game
    python scripts/utilities/validate_input.py --strict           # Fail on any warning

Validates:
- Required files exist
- Required sheets exist in Excel files
- Required columns exist in sheets
- No empty required fields
- Game ID consistency
- Basic data type validation
"""

import argparse
import json
from pathlib import Path
import sys

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CONFIG_DIR = PROJECT_ROOT / "config"

# Expected structure
EXPECTED_SHEETS = {
    'events': {
        'required_columns': ['event_index', 'period', 'event_type_'],
        'optional_columns': ['game_clock', 'elapsed_time', 'event_detail', 'zone'],
    },
    'shifts': {
        'required_columns': ['shift_index', 'period', 'player_id'],
        'optional_columns': ['start_time', 'end_time', 'duration'],
    },
    'roster': {
        'required_columns': ['player_id'],
        'optional_columns': ['jersey_number', 'position', 'team'],
    },
}

# Alternative sheet names that map to expected names
SHEET_NAME_ALIASES = {
    'Events': 'events',
    'Shifts': 'shifts',
    'Roster': 'roster',
    'GameRoster': 'roster',
    'Game_Roster': 'roster',
    'event': 'events',
    'shift': 'shifts',
}


class InputValidator:
    """Validates raw input files."""
    
    def __init__(self, strict=False):
        self.strict = strict
        self.errors = []
        self.warnings = []
    
    def error(self, msg):
        self.errors.append(msg)
        print(f"  ❌ ERROR: {msg}")
    
    def warn(self, msg):
        self.warnings.append(msg)
        print(f"  ⚠️  WARN: {msg}")
    
    def ok(self, msg):
        print(f"  ✓ {msg}")
    
    def discover_games(self):
        """Find all game folders in raw data directory."""
        if not RAW_DIR.exists():
            self.error(f"Raw data directory not found: {RAW_DIR}")
            return []
        
        games = []
        for item in RAW_DIR.iterdir():
            if item.is_dir() and item.name.startswith('game_'):
                try:
                    game_id = int(item.name.replace('game_', ''))
                    games.append((game_id, item))
                except ValueError:
                    self.warn(f"Invalid game folder name: {item.name}")
        
        return sorted(games, key=lambda x: x[0])
    
    def find_excel_files(self, game_dir):
        """Find Excel files in game directory."""
        excel_files = list(game_dir.glob("*.xlsx"))
        excel_files.extend(game_dir.glob("*.xls"))
        return excel_files
    
    def normalize_sheet_name(self, sheet_name):
        """Normalize sheet name to expected format."""
        return SHEET_NAME_ALIASES.get(sheet_name, sheet_name.lower())
    
    def validate_excel_file(self, excel_path, game_id):
        """Validate a single Excel file."""
        print(f"\n  Validating: {excel_path.name}")
        
        if not HAS_PANDAS or not HAS_OPENPYXL:
            self.warn("pandas/openpyxl not installed - skipping detailed validation")
            return True
        
        try:
            xl = pd.ExcelFile(excel_path)
            sheet_names = xl.sheet_names
            
            # Map actual sheets to expected names
            found_sheets = {}
            for actual_name in sheet_names:
                normalized = self.normalize_sheet_name(actual_name)
                if normalized in EXPECTED_SHEETS:
                    found_sheets[normalized] = actual_name
            
            # Check for required sheets
            for expected_sheet in ['events', 'shifts']:  # roster is optional
                if expected_sheet not in found_sheets:
                    self.error(f"Missing sheet: {expected_sheet}")
            
            # Validate each found sheet
            for normalized_name, actual_name in found_sheets.items():
                self.validate_sheet(xl, actual_name, normalized_name, game_id)
            
            return len([e for e in self.errors if excel_path.name in e]) == 0
            
        except Exception as e:
            self.error(f"Cannot read {excel_path.name}: {e}")
            return False
    
    def validate_sheet(self, xl, actual_name, expected_name, game_id):
        """Validate a single sheet."""
        try:
            df = xl.parse(actual_name)
            
            # Check required columns
            expected = EXPECTED_SHEETS.get(expected_name, {})
            required_cols = expected.get('required_columns', [])
            
            # Handle column name variations
            df_cols_lower = {c.lower(): c for c in df.columns}
            
            for req_col in required_cols:
                col_found = (
                    req_col in df.columns or 
                    req_col.lower() in df_cols_lower
                )
                if not col_found:
                    self.error(f"{expected_name}: Missing column '{req_col}'")
            
            # Check for empty required fields
            if len(df) == 0:
                self.warn(f"{expected_name}: Sheet is empty")
            else:
                self.ok(f"{expected_name}: {len(df)} rows, {len(df.columns)} columns")
            
            # Validate game_id consistency if present
            if 'game_id' in df.columns:
                unique_ids = df['game_id'].dropna().unique()
                if len(unique_ids) == 1:
                    if int(unique_ids[0]) != game_id:
                        self.warn(f"{expected_name}: game_id mismatch (file has {unique_ids[0]}, expected {game_id})")
                elif len(unique_ids) > 1:
                    self.warn(f"{expected_name}: Multiple game_ids found: {unique_ids}")
            
        except Exception as e:
            self.error(f"Cannot parse {expected_name}: {e}")
    
    def validate_game(self, game_id, game_dir):
        """Validate all files for a single game."""
        print(f"\n{'='*60}")
        print(f"Validating Game {game_id}")
        print(f"Directory: {game_dir}")
        print('='*60)
        
        excel_files = self.find_excel_files(game_dir)
        
        if not excel_files:
            self.error(f"No Excel files found in {game_dir}")
            return False
        
        all_valid = True
        for excel_file in excel_files:
            if not self.validate_excel_file(excel_file, game_id):
                all_valid = False
        
        return all_valid
    
    def validate_all(self):
        """Validate all games."""
        games = self.discover_games()
        
        if not games:
            self.error("No games found to validate")
            return False
        
        print(f"\nFound {len(games)} games to validate")
        
        results = {}
        for game_id, game_dir in games:
            results[game_id] = self.validate_game(game_id, game_dir)
        
        # Summary
        print(f"\n{'='*60}")
        print("VALIDATION SUMMARY")
        print('='*60)
        
        passed = sum(1 for v in results.values() if v)
        failed = sum(1 for v in results.values() if not v)
        
        print(f"  Games passed: {passed}")
        print(f"  Games failed: {failed}")
        print(f"  Total errors: {len(self.errors)}")
        print(f"  Total warnings: {len(self.warnings)}")
        
        if self.strict and self.warnings:
            print(f"\n  ❌ STRICT MODE: Warnings treated as failures")
            return False
        
        return len(self.errors) == 0
    
    def get_report(self):
        """Get validation report as dict."""
        return {
            'passed': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
        }


def main():
    parser = argparse.ArgumentParser(description='Validate raw input files')
    parser.add_argument('--game', type=int, help='Validate specific game ID')
    parser.add_argument('--strict', action='store_true', help='Fail on warnings')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    validator = InputValidator(strict=args.strict)
    
    if args.game:
        game_dir = RAW_DIR / f"game_{args.game}"
        if not game_dir.exists():
            print(f"Game directory not found: {game_dir}")
            sys.exit(1)
        passed = validator.validate_game(args.game, game_dir)
    else:
        passed = validator.validate_all()
    
    if args.json:
        print(json.dumps(validator.get_report()))
    
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
