"""
=============================================================================
MASTER DIMENSIONS MODULE - SINGLE SOURCE OF TRUTH
=============================================================================
File: src/models/master_dims.py
Version: 20.7
Updated: 2026-01-09

PURPOSE:
    Load master dimension tables from BLB_Tables.xlsx and auto-generate
    all derived dimension tables. This is the ONLY place dim propagation
    logic lives - no patchwork code elsewhere.

ARCHITECTURE:
    BLB_Tables.xlsx (User maintains)
        ├── M_event_type (23 rows)
        ├── M_event_detail (49 rows)
        ├── M_event_detail_2 (176 rows) ← SOURCE for derived dims
        ├── M_play_detail (111 rows)
        ├── M_play_detail_2 (111 rows)
        ├── M_shift_start_type (9 rows)
        └── M_shift_stop_type (18 rows)
        
    DERIVED DIMS (auto-generated from M_event_detail_2):
        ├── D_shot_type ← from Shot_* codes
        ├── D_goal_type ← from Goal_* codes
        ├── D_pass_type ← from Pass_* codes
        ├── D_save_type ← from Save_* codes
        ├── D_giveaway_type ← from Giveaway_* codes (with quality)
        ├── D_takeaway_type ← from Takeaway_* codes (with quality)
        ├── D_zone_entry_type ← from ZoneEntry_* codes (with controlled)
        ├── D_zone_exit_type ← from ZoneExit_* codes (with controlled)
        ├── D_stoppage_type ← from Stoppage_* codes
        ├── D_penalty_type ← from Penalty_* codes (with severity)
        └── D_zone_play_type ← from Zone_* codes

USAGE:
    from src.models.master_dims import MasterDims
    
    # Load from BLB_Tables.xlsx
    dims = MasterDims('/path/to/BLB_Tables.xlsx')
    
    # Access master dims
    event_types = dims.event_type
    event_details = dims.event_detail
    
    # Access derived dims (auto-generated)
    shot_types = dims.shot_type
    zone_entry_types = dims.zone_entry_type
    
    # Get all dims as dict for ETL
    all_dims = dims.get_all_dims()
    
    # Export all dims to CSV folder
    dims.export_to_csv('/path/to/output/')
=============================================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MasterDims:
    """
    Load and propagate all dimension tables from BLB_Tables.xlsx.
    
    This class is the SINGLE SOURCE OF TRUTH for dimension management.
    All derived dims are auto-generated from the master dims.
    """
    
    # xG modifiers for shot types (based on NHL data)
    XG_MODIFIERS = {
        'Wrist': 1.0, 'Slap': 0.85, 'Snap': 1.1, 'Backhand': 0.75,
        'Tip': 1.3, 'Deflection': 1.25, 'WrapAround': 0.6, 'OneTime': 1.4,
        'Poke': 0.5, 'Bat': 1.2, 'BetweenLegs': 0.4, 'Cradle': 0.5,
        'Dumpin': 0.1, 'Other': 0.8
    }
    
    # High danger shot types
    HIGH_DANGER_SHOTS = ['Tip', 'Deflection', 'OneTime', 'Bat', 'BetweenLegs', 'Cradle']
    
    # Controlled zone movement patterns
    CONTROLLED_PATTERNS = ['Rush', 'Carry', 'Pass', 'Skate']
    UNCONTROLLED_PATTERNS = ['Dump', 'Chip', 'Clear', 'Lob', 'PenaltyKill']
    
    # Bad giveaway patterns
    BAD_GIVEAWAY_PATTERNS = ['PassIntercepted', 'PassMissed', 'PassBlocked', 'ShotBlocked',
                             'ShotMissed', 'BattleLost', 'Misplayed', 'ReceiverMissed']
    
    # Good takeaway patterns
    GOOD_TAKEAWAY_PATTERNS = ['PassIntercepted', 'PokeCheck', 'StickCheck', 'BattleWon']
    
    # Major penalty patterns
    MAJOR_PENALTY_PATTERNS = ['Fighting', 'Misconduct', 'GameMisconduct', 'MatchPenalty',
                              'Spearing', 'Boarding', 'Kneeing', 'Elbowing', 'Checking']
    
    def __init__(self, blb_tables_path: str):
        """
        Initialize MasterDims from BLB_Tables.xlsx.
        
        Args:
            blb_tables_path: Path to BLB_Tables.xlsx
        """
        self.source_path = Path(blb_tables_path)
        if not self.source_path.exists():
            raise FileNotFoundError(f"BLB_Tables.xlsx not found: {blb_tables_path}")
        
        # Load masters
        self._load_masters()
        
        # Generate derived dims
        self._generate_derived_dims()
        
        logger.info(f"MasterDims loaded from {blb_tables_path}")
    
    def _load_masters(self):
        """Load master dim tables from Excel."""
        xlsx = pd.ExcelFile(self.source_path)
        
        # Master dims (sheet names match table names in BLB_TABLES.xlsx)
        self.event_type = pd.read_excel(xlsx, sheet_name='dim_event_type')
        self.event_detail = pd.read_excel(xlsx, sheet_name='dim_event_detail')
        self.event_detail_2 = pd.read_excel(xlsx, sheet_name='dim_event_detail_2')
        self.play_detail = pd.read_excel(xlsx, sheet_name='dim_play_detail')
        self.play_detail_2 = pd.read_excel(xlsx, sheet_name='dim_play_detail_2')
        self.shift_start_type = pd.read_excel(xlsx, sheet_name='dim_shift_start_type')
        self.shift_stop_type = pd.read_excel(xlsx, sheet_name='dim_shift_stop_type')
        
        # Load other reference dims from same file
        self._reference_dims = {}
        reference_sheets = ['dim_league', 'dim_rinkboxcoord', 'dim_rinkcoordzones', 'dim_randomnames']
        for sheet in reference_sheets:
            if sheet in xlsx.sheet_names:
                name = sheet.replace('dim_', '')
                self._reference_dims[name] = pd.read_excel(xlsx, sheet_name=sheet)
        
        logger.info(f"Loaded {len(xlsx.sheet_names)} sheets from BLB_TABLES.xlsx")
    
    def _generate_derived_dims(self):
        """Generate all derived dims from event_detail_2."""
        ed2 = self.event_detail_2
        
        # Generate each derived dim
        self.shot_type = self._derive_shot_type(ed2)
        self.goal_type = self._derive_goal_type(ed2)
        self.pass_type = self._derive_pass_type(ed2)
        self.save_type = self._derive_save_type(ed2)
        self.giveaway_type = self._derive_giveaway_type(ed2)
        self.takeaway_type = self._derive_takeaway_type(ed2)
        self.zone_entry_type = self._derive_zone_entry_type(ed2)
        self.zone_exit_type = self._derive_zone_exit_type(ed2)
        self.stoppage_type = self._derive_stoppage_type(ed2)
        self.penalty_type = self._derive_penalty_type(ed2)
        self.zone_play_type = self._derive_zone_play_type(ed2)
        
        logger.info("Generated all derived dims from event_detail_2")
    
    def _derive_shot_type(self, ed2: pd.DataFrame) -> pd.DataFrame:
        """Derive shot types from Shot_* codes."""
        rows = ed2[ed2['event_detail_2_code'].str.startswith('Shot_', na=False)]
        if len(rows) == 0:
            return pd.DataFrame()
        
        result = []
        for i, row in enumerate(rows.itertuples(), 1):
            code = row.event_detail_2_code
            short = code.replace('Shot_', '')
            result.append({
                'shot_type_id': f'ST{i:04d}',
                'shot_type_code': short,
                'shot_type_name': short.replace('_', ' '),
                'source_event_detail_2': code,
                'xg_modifier': self.XG_MODIFIERS.get(short, 0.8),
                'is_high_danger': short in self.HIGH_DANGER_SHOTS
            })
        return pd.DataFrame(result)
    
    def _derive_goal_type(self, ed2: pd.DataFrame) -> pd.DataFrame:
        """Derive goal types from Goal_* codes."""
        rows = ed2[ed2['event_detail_2_code'].str.startswith('Goal_', na=False)]
        if len(rows) == 0:
            return pd.DataFrame()
        
        result = []
        for i, row in enumerate(rows.itertuples(), 1):
            code = row.event_detail_2_code
            short = code.replace('Goal_', '')
            result.append({
                'goal_type_id': f'GT{i:04d}',
                'goal_type_code': short,
                'goal_type_name': short.replace('_', ' '),
                'source_event_detail_2': code
            })
        return pd.DataFrame(result)
    
    def _derive_pass_type(self, ed2: pd.DataFrame) -> pd.DataFrame:
        """Derive pass types from Pass_* codes."""
        rows = ed2[ed2['event_detail_2_code'].str.startswith('Pass_', na=False)]
        if len(rows) == 0:
            return pd.DataFrame()
        
        result = []
        for i, row in enumerate(rows.itertuples(), 1):
            code = row.event_detail_2_code
            short = code.replace('Pass_', '').replace('/', ' ')
            result.append({
                'pass_type_id': f'PT{i:04d}',
                'pass_type_code': short,
                'pass_type_name': short.replace('_', ' '),
                'source_event_detail_2': code
            })
        return pd.DataFrame(result)
    
    def _derive_save_type(self, ed2: pd.DataFrame) -> pd.DataFrame:
        """Derive save types from Save_* codes."""
        rows = ed2[ed2['event_detail_2_code'].str.startswith('Save_', na=False)]
        if len(rows) == 0:
            return pd.DataFrame()
        
        result = []
        for i, row in enumerate(rows.itertuples(), 1):
            code = row.event_detail_2_code
            short = code.replace('Save_', '')
            result.append({
                'save_type_id': f'SV{i:04d}',
                'save_type_code': short,
                'save_type_name': short.replace('_', ' '),
                'source_event_detail_2': code
            })
        return pd.DataFrame(result)
    
    def _derive_giveaway_type(self, ed2: pd.DataFrame) -> pd.DataFrame:
        """Derive giveaway types with quality flags."""
        rows = ed2[ed2['event_detail_2_code'].str.startswith('Giveaway_', na=False)]
        if len(rows) == 0:
            return pd.DataFrame()
        
        result = []
        for i, row in enumerate(rows.itertuples(), 1):
            code = row.event_detail_2_code
            short = code.replace('Giveaway_', '').replace('/', ' ')
            is_bad = any(x in code for x in self.BAD_GIVEAWAY_PATTERNS)
            result.append({
                'giveaway_type_id': f'GA{i:04d}',
                'giveaway_type_code': code,
                'giveaway_type_name': short.replace('_', ' '),
                'quality': 'bad' if is_bad else 'neutral',
                'turnover_weight': 1.2 if is_bad else 0.8
            })
        return pd.DataFrame(result)
    
    def _derive_takeaway_type(self, ed2: pd.DataFrame) -> pd.DataFrame:
        """Derive takeaway types with quality flags."""
        rows = ed2[ed2['event_detail_2_code'].str.startswith('Takeaway_', na=False)]
        if len(rows) == 0:
            return pd.DataFrame()
        
        result = []
        for i, row in enumerate(rows.itertuples(), 1):
            code = row.event_detail_2_code
            short = code.replace('Takeaway_', '')
            is_good = any(x in code for x in self.GOOD_TAKEAWAY_PATTERNS)
            result.append({
                'takeaway_type_id': f'TA{i:04d}',
                'takeaway_type_code': code,
                'takeaway_type_name': short.replace('_', ' '),
                'quality': 'good' if is_good else 'neutral',
                'turnover_weight': 1.2 if is_good else 0.8
            })
        return pd.DataFrame(result)
    
    def _derive_zone_entry_type(self, ed2: pd.DataFrame) -> pd.DataFrame:
        """Derive zone entry types with controlled flag."""
        rows = ed2[ed2['event_detail_2_code'].str.startswith('ZoneEntry_', na=False)]
        if len(rows) == 0:
            return pd.DataFrame()
        
        result = []
        for i, row in enumerate(rows.itertuples(), 1):
            code = row.event_detail_2_code
            short = code.replace('ZoneEntry_', '')
            is_ctrl = any(x in short for x in self.CONTROLLED_PATTERNS)
            is_unctrl = any(x in short for x in self.UNCONTROLLED_PATTERNS)
            
            if is_ctrl and not is_unctrl:
                control = 'controlled'
            elif is_unctrl:
                control = 'uncontrolled'
            else:
                control = 'other'
            
            result.append({
                'zone_entry_type_id': f'ZE{i:04d}',
                'zone_entry_type_code': code,
                'zone_entry_type_name': short.replace('_', ' ').replace('/', ' '),
                'control_type': control,
                'is_controlled': is_ctrl and not is_unctrl,
                'xg_multiplier': 1.2 if is_ctrl else 0.7
            })
        return pd.DataFrame(result)
    
    def _derive_zone_exit_type(self, ed2: pd.DataFrame) -> pd.DataFrame:
        """Derive zone exit types with controlled flag."""
        rows = ed2[ed2['event_detail_2_code'].str.startswith('ZoneExit_', na=False)]
        if len(rows) == 0:
            return pd.DataFrame()
        
        result = []
        for i, row in enumerate(rows.itertuples(), 1):
            code = row.event_detail_2_code
            short = code.replace('ZoneExit_', '')
            is_ctrl = any(x in short for x in self.CONTROLLED_PATTERNS) and not any(x in short for x in self.UNCONTROLLED_PATTERNS)
            is_unctrl = any(x in short for x in self.UNCONTROLLED_PATTERNS)
            
            result.append({
                'zone_exit_type_id': f'ZX{i:04d}',
                'zone_exit_type_code': code,
                'zone_exit_type_name': short.replace('_', ' ').replace('/', ' '),
                'control_type': 'controlled' if is_ctrl else ('uncontrolled' if is_unctrl else 'other'),
                'is_controlled': is_ctrl
            })
        return pd.DataFrame(result)
    
    def _derive_stoppage_type(self, ed2: pd.DataFrame) -> pd.DataFrame:
        """Derive stoppage types."""
        rows = ed2[ed2['event_detail_2_code'].str.startswith('Stoppage_', na=False)]
        if len(rows) == 0:
            return pd.DataFrame()
        
        result = []
        for i, row in enumerate(rows.itertuples(), 1):
            code = row.event_detail_2_code
            short = code.replace('Stoppage_', '').replace('/', ' ')
            result.append({
                'stoppage_type_id': f'SP{i:04d}',
                'stoppage_type_code': code,
                'stoppage_type_name': short.replace('_', ' ')
            })
        return pd.DataFrame(result)
    
    def _derive_penalty_type(self, ed2: pd.DataFrame) -> pd.DataFrame:
        """Derive penalty types with severity."""
        rows = ed2[ed2['event_detail_2_code'].str.startswith('Penalty_', na=False)]
        if len(rows) == 0:
            return pd.DataFrame()
        
        result = []
        for i, row in enumerate(rows.itertuples(), 1):
            code = row.event_detail_2_code
            short = code.replace('Penalty_', '')
            is_major = any(x in short for x in self.MAJOR_PENALTY_PATTERNS)
            result.append({
                'penalty_type_id': f'PN{i:04d}',
                'penalty_type_code': code,
                'penalty_type_name': short.replace('_', ' '),
                'severity': 'major' if is_major else 'minor',
                'pim': 5 if is_major else 2
            })
        return pd.DataFrame(result)
    
    def _derive_zone_play_type(self, ed2: pd.DataFrame) -> pd.DataFrame:
        """Derive zone play types."""
        rows = ed2[ed2['event_detail_2_code'].str.startswith('Zone_', na=False)]
        if len(rows) == 0:
            return pd.DataFrame()
        
        result = []
        for i, row in enumerate(rows.itertuples(), 1):
            code = row.event_detail_2_code
            short = code.replace('Zone_', '')
            result.append({
                'zone_play_type_id': f'ZP{i:04d}',
                'zone_play_type_code': code,
                'zone_play_type_name': short.replace('_', ' ')
            })
        return pd.DataFrame(result)
    
    def get_master_dims(self) -> Dict[str, pd.DataFrame]:
        """Get all master dims as dict."""
        return {
            'dim_event_type': self.event_type,
            'dim_event_detail': self.event_detail,
            'dim_event_detail_2': self.event_detail_2,
            'dim_play_detail': self.play_detail,
            'dim_play_detail_2': self.play_detail_2,
            'dim_shift_start_type': self.shift_start_type,
            'dim_shift_stop_type': self.shift_stop_type,
        }
    
    def get_derived_dims(self) -> Dict[str, pd.DataFrame]:
        """Get all derived dims as dict."""
        return {
            'dim_shot_type': self.shot_type,
            'dim_goal_type': self.goal_type,
            'dim_pass_type': self.pass_type,
            'dim_save_type': self.save_type,
            'dim_giveaway_type': self.giveaway_type,
            'dim_takeaway_type': self.takeaway_type,
            'dim_zone_entry_type': self.zone_entry_type,
            'dim_zone_exit_type': self.zone_exit_type,
            'dim_stoppage_type': self.stoppage_type,
            'dim_penalty_type': self.penalty_type,
            'dim_zone_play_type': self.zone_play_type,
        }
    
    def get_reference_dims(self) -> Dict[str, pd.DataFrame]:
        """Get all reference dims as dict."""
        return {f'dim_{k}': v for k, v in self._reference_dims.items()}
    
    def get_all_dims(self) -> Dict[str, pd.DataFrame]:
        """Get all dims (master + derived + reference) as dict."""
        all_dims = {}
        all_dims.update(self.get_master_dims())
        all_dims.update(self.get_derived_dims())
        all_dims.update(self.get_reference_dims())
        return all_dims
    
    def export_to_csv(self, output_dir: str):
        """Export all dims to CSV files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        all_dims = self.get_all_dims()
        for name, df in all_dims.items():
            if len(df) > 0:
                df.to_csv(output_path / f'{name}.csv', index=False)
                logger.debug(f"Exported {name}: {len(df)} rows")
        
        logger.info(f"Exported {len(all_dims)} dim tables to {output_dir}")
    
    def get_valid_codes(self, dim_name: str) -> list:
        """Get list of valid codes for a dimension."""
        dim_map = {
            'event_type': ('event_type', 'event_type_code'),
            'event_detail': ('event_detail', 'event_detail_code'),
            'event_detail_2': ('event_detail_2', 'event_detail_2_code'),
            'play_detail': ('play_detail', 'play_detail_code'),
            'play_detail_2': ('play_detail_2', 'play_detail_code'),
            'shot_type': ('shot_type', 'shot_type_code'),
            'pass_type': ('pass_type', 'pass_type_code'),
            'save_type': ('save_type', 'save_type_code'),
        }
        
        if dim_name in dim_map:
            attr, col = dim_map[dim_name]
            df = getattr(self, attr, pd.DataFrame())
            if len(df) > 0 and col in df.columns:
                return df[col].dropna().unique().tolist()
        
        return []


# Convenience function for ETL
def load_dims_from_blb_tables(blb_path: str) -> Dict[str, pd.DataFrame]:
    """
    Load all dims from BLB_Tables.xlsx.
    
    This is the recommended way for ETL to load dims.
    """
    dims = MasterDims(blb_path)
    return dims.get_all_dims()


if __name__ == '__main__':
    # Test loading
    import sys
    if len(sys.argv) > 1:
        dims = MasterDims(sys.argv[1])
        print(f"Loaded {len(dims.get_all_dims())} dims")
        for name, df in dims.get_all_dims().items():
            print(f"  {name}: {len(df)} rows")
