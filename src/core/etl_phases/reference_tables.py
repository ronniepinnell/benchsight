"""
Reference Tables Module
=======================

Contains functions for creating reference/dimension tables.

Functions:
- create_reference_tables: Create all dimension tables for the ETL
"""

import pandas as pd
from pathlib import Path

# Import table writer for saving
from src.core.table_writer import save_output_table


def create_reference_tables(output_dir: Path, log, save_table_func=None):
    """Create all reference/dimension tables.

    Args:
        output_dir: Path to output directory
        log: ETLLogger instance
        save_table_func: Function to save tables (optional)
    """
    log.section("PHASE 5: CREATE REFERENCE TABLES")

    if save_table_func is None:
        save_table_func = lambda df, name: save_output_table(df, name, output_dir)

    # dim_player_role - 14 roles
    roles = []
    for i in range(1, 7):
        roles.append({
            'role_id': f'PR{i:02d}',
            'role_code': f'event_player_{i}',
            'role_name': f'Event Player {i}',
            'role_type': 'event_team',
            'sort_order': i
        })
    roles.append({
        'role_id': 'PR07',
        'role_code': 'event_goalie',
        'role_name': 'Event Team Goalie',
        'role_type': 'event_team',
        'sort_order': 7
    })
    for i in range(1, 7):
        roles.append({
            'role_id': f'PR{7+i:02d}',
            'role_code': f'opp_player_{i}',
            'role_name': f'Opponent Player {i}',
            'role_type': 'opp_team',
            'sort_order': 7 + i
        })
    roles.append({
        'role_id': 'PR14',
        'role_code': 'opp_goalie',
        'role_name': 'Opponent Goalie',
        'role_type': 'opp_team',
        'sort_order': 14
    })
    save_table_func(pd.DataFrame(roles), 'dim_player_role')
    log.info("dim_player_role: 14 rows")

    # dim_position
    positions = [
        {'position_id': 'POS01', 'position_code': 'C', 'position_name': 'Center', 'position_type': 'forward'},
        {'position_id': 'POS02', 'position_code': 'LW', 'position_name': 'Left Wing', 'position_type': 'forward'},
        {'position_id': 'POS03', 'position_code': 'RW', 'position_name': 'Right Wing', 'position_type': 'forward'},
        {'position_id': 'POS04', 'position_code': 'F', 'position_name': 'Forward', 'position_type': 'forward'},
        {'position_id': 'POS05', 'position_code': 'D', 'position_name': 'Defense', 'position_type': 'defense'},
        {'position_id': 'POS06', 'position_code': 'G', 'position_name': 'Goalie', 'position_type': 'goalie'},
    ]
    save_table_func(pd.DataFrame(positions), 'dim_position')
    log.info("dim_position: 6 rows")

    # dim_zone
    zones = [
        {'zone_id': 'ZN01', 'zone_code': 'O', 'zone_name': 'Offensive Zone', 'zone_abbrev': 'OZ'},
        {'zone_id': 'ZN02', 'zone_code': 'D', 'zone_name': 'Defensive Zone', 'zone_abbrev': 'DZ'},
        {'zone_id': 'ZN03', 'zone_code': 'N', 'zone_name': 'Neutral Zone', 'zone_abbrev': 'NZ'},
    ]
    save_table_func(pd.DataFrame(zones), 'dim_zone')
    log.info("dim_zone: 3 rows")

    # dim_period
    periods = [
        {'period_id': 'P01', 'period_number': 1, 'period_name': '1st Period', 'period_type': 'regulation', 'period_minutes': 18},
        {'period_id': 'P02', 'period_number': 2, 'period_name': '2nd Period', 'period_type': 'regulation', 'period_minutes': 18},
        {'period_id': 'P03', 'period_number': 3, 'period_name': '3rd Period', 'period_type': 'regulation', 'period_minutes': 18},
        {'period_id': 'P04', 'period_number': 4, 'period_name': 'Overtime', 'period_type': 'overtime', 'period_minutes': 5},
        {'period_id': 'P05', 'period_number': 5, 'period_name': 'Shootout', 'period_type': 'shootout', 'period_minutes': 0},
    ]
    save_table_func(pd.DataFrame(periods), 'dim_period')
    log.info("dim_period: 5 rows")

    # dim_venue
    venues = [
        {'venue_id': 'VN01', 'venue_code': 'home', 'venue_name': 'Home', 'venue_abbrev': 'H'},
        {'venue_id': 'VN02', 'venue_code': 'away', 'venue_name': 'Away', 'venue_abbrev': 'A'},
    ]
    save_table_func(pd.DataFrame(venues), 'dim_venue')
    log.info("dim_venue: 2 rows")

    # dim_event_type - LOADED FROM BLB_Tables.xlsx (not generated!)
    if not Path(output_dir / 'dim_event_type.csv').exists():
        log.warn("dim_event_type not loaded from BLB - generating from hardcoded...")
        from src.models.dimensions import EVENT_TYPES
        event_types = []
        for et in EVENT_TYPES:
            event_types.append({
                'event_type_id': f"ET{et['event_type_id']:04d}",
                'event_type_code': et['event_type'],
                'event_type_name': et['event_type'].replace('_', ' '),
                'event_category': et.get('event_category', 'other'),
                'description': et.get('description', ''),
                'is_corsi': et.get('is_corsi', False),
                'is_fenwick': et.get('is_fenwick', False),
            })
        save_table_func(pd.DataFrame(event_types), 'dim_event_type')
        log.info(f"dim_event_type: {len(event_types)} rows (generated)")
    else:
        log.info("dim_event_type: using BLB_Tables data")

    # dim_event_detail - LOADED FROM BLB_Tables.xlsx (not generated!)
    if not Path(output_dir / 'dim_event_detail.csv').exists():
        log.warn("dim_event_detail not loaded from BLB - generating from hardcoded...")
        from src.models.dimensions import EVENT_DETAILS
        event_details = []
        for ed in EVENT_DETAILS:
            event_details.append({
                'event_detail_id': f"ED{ed['event_detail_id']:04d}",
                'event_detail_code': ed['event_detail'],
                'event_detail_name': ed['event_detail'].replace('_', ' '),
                'event_type': ed.get('event_type', ''),
                'category': ed.get('category', 'other'),
                'is_shot_on_goal': ed.get('is_shot_on_goal', False),
                'is_goal': ed.get('is_goal', False),
                'is_miss': ed.get('is_miss', False),
                'is_block': ed.get('is_block', False),
                'danger_potential': ed.get('danger_potential', 'low'),
            })
        save_table_func(pd.DataFrame(event_details), 'dim_event_detail')
        log.info(f"dim_event_detail: {len(event_details)} rows (generated)")
    else:
        log.info("dim_event_detail: using BLB_Tables data")

    # dim_event_detail_2 - LOADED FROM BLB_Tables.xlsx (not generated!)
    if not Path(output_dir / 'dim_event_detail_2.csv').exists():
        log.warn("dim_event_detail_2 not loaded from BLB - generating from tracking...")
        _create_dim_event_detail_2(output_dir, log, save_table_func)
    else:
        log.info("dim_event_detail_2: using BLB_Tables data")

    # dim_success - success codes
    success_codes = [
        {'success_id': 'SC01', 'success_code': 's', 'success_name': 'Successful', 'is_successful': True},
        {'success_id': 'SC02', 'success_code': 'u', 'success_name': 'Unsuccessful', 'is_successful': False},
        {'success_id': 'SC03', 'success_code': 'n', 'success_name': 'Not Applicable', 'is_successful': None},
    ]
    save_table_func(pd.DataFrame(success_codes), 'dim_success')
    log.info("dim_success: 3 rows")

    # dim_shot_type - from models/dimensions.py
    from src.models.dimensions import SHOT_TYPES
    shot_types = []
    for st in SHOT_TYPES:
        shot_types.append({
            'shot_type_id': f"ST{st['shot_type_id']:04d}",
            'shot_type_code': st['shot_type'],
            'shot_type_name': st.get('shot_type_full', st['shot_type']),
            'description': st.get('description', ''),
        })
    save_table_func(pd.DataFrame(shot_types), 'dim_shot_type')
    log.info(f"dim_shot_type: {len(shot_types)} rows")

    # dim_pass_type - from models/dimensions.py
    from src.models.dimensions import PASS_TYPES
    pass_types = []
    for pt in PASS_TYPES:
        pass_types.append({
            'pass_type_id': f"PT{pt['pass_type_id']:04d}",
            'pass_type_code': pt['pass_type'],
            'pass_type_name': pt['pass_type'],
            'description': pt.get('description', ''),
        })
    save_table_func(pd.DataFrame(pass_types), 'dim_pass_type')
    log.info(f"dim_pass_type: {len(pass_types)} rows")

    # dim_zone_entry_type - dynamically from tracking data
    _create_dim_zone_entry_type(output_dir, log, save_table_func)

    # dim_zone_exit_type - dynamically from tracking data
    _create_dim_zone_exit_type(output_dir, log, save_table_func)

    # dim_stoppage_type - dynamically from tracking data
    _create_dim_stoppage_type(output_dir, log, save_table_func)

    # dim_giveaway_type - dynamically from tracking data
    _create_dim_giveaway_type(output_dir, log, save_table_func)

    # dim_takeaway_type - dynamically from tracking data
    _create_dim_takeaway_type(output_dir, log, save_table_func)

    # dim_play_detail - LOADED FROM BLB_Tables.xlsx (not generated!)
    if not Path(output_dir / 'dim_play_detail.csv').exists():
        log.warn("dim_play_detail not loaded from BLB - generating from hardcoded...")
        _create_dim_play_detail(output_dir, log, save_table_func)
    else:
        log.info("dim_play_detail: using BLB_Tables data")

    # dim_play_detail_2 - LOADED FROM BLB_Tables.xlsx (not generated!)
    if not Path(output_dir / 'dim_play_detail_2.csv').exists():
        log.warn("dim_play_detail_2 not loaded from BLB - generating from tracking...")
        _create_dim_play_detail_2(output_dir, log, save_table_func)
    else:
        log.info("dim_play_detail_2: using BLB_Tables data")


def _create_dim_event_detail_2(output_dir, log, save_table_func):
    """Create dim_event_detail_2 from tracking data."""
    records = []

    tracking_path = output_dir / 'fact_event_players.csv'
    if tracking_path.exists():
        tracking = pd.read_csv(tracking_path, low_memory=False)

        if 'event_detail_2' in tracking.columns:
            raw_codes = tracking['event_detail_2'].dropna().unique()
            codes = sorted(set(str(c).replace('-', '_').replace('/', '_') for c in raw_codes))

            for i, code in enumerate(codes, 1):
                records.append({
                    'event_detail_2_id': f'ED2{i:02d}',
                    'event_detail_2_code': code,
                    'event_detail_2_name': code.replace('_', ' '),
                    'category': 'other',
                })

    if records:
        df = pd.DataFrame(records)
        save_table_func(df, 'dim_event_detail_2')
        log.info(f"dim_event_detail_2: {len(df)} rows")
    else:
        df = pd.DataFrame(columns=['event_detail_2_id', 'event_detail_2_code', 'event_detail_2_name', 'category'])
        save_table_func(df, 'dim_event_detail_2')
        log.info("dim_event_detail_2: 0 rows (no data)")


def _create_dim_zone_entry_type(output_dir, log, save_table_func):
    """Create dim_zone_entry_type from dim_event_detail_2."""
    records = []
    ed2_path = output_dir / 'dim_event_detail_2.csv'
    if ed2_path.exists():
        ed2 = pd.read_csv(ed2_path, low_memory=False)
        ze_codes = ed2[ed2['event_detail_2_code'].astype(str).str.startswith('ZoneEntry', na=False)]['event_detail_2_code'].unique()
        codes = sorted(set(str(c) for c in ze_codes))
        for i, code in enumerate(codes, 1):
            entry_type = code.replace('ZoneEntry_', '').replace('_', ' ').replace('/', ' ')
            entry_type = entry_type.replace('Rush', 'Carried')
            is_controlled = any(x in code for x in ['_Rush', '_Carried', '_Pass']) and 'Miss' not in code and 'Misplay' not in code
            records.append({
                'zone_entry_type_id': f'ZE{i:04d}',
                'zone_entry_type_code': code,
                'zone_entry_type_name': entry_type,
                'is_controlled': is_controlled,
            })
    df = pd.DataFrame(records) if records else pd.DataFrame(columns=['zone_entry_type_id', 'zone_entry_type_code', 'zone_entry_type_name', 'is_controlled'])
    save_table_func(df, 'dim_zone_entry_type')
    log.info(f"dim_zone_entry_type: {len(df)} rows")


def _create_dim_zone_exit_type(output_dir, log, save_table_func):
    """Create dim_zone_exit_type from dim_event_detail_2."""
    records = []
    ed2_path = output_dir / 'dim_event_detail_2.csv'
    if ed2_path.exists():
        ed2 = pd.read_csv(ed2_path, low_memory=False)
        zx_codes = ed2[ed2['event_detail_2_code'].astype(str).str.startswith('ZoneExit', na=False)]['event_detail_2_code'].unique()
        codes = sorted(set(str(c) for c in zx_codes))
        for i, code in enumerate(codes, 1):
            exit_type = code.replace('ZoneExit_', '').replace('_', ' ').replace('/', ' ')
            exit_type = exit_type.replace('Rush', 'Carried')
            is_controlled = any(x in code for x in ['_Rush', '_Carried', '_Pass']) and 'Miss' not in code and 'Misplay' not in code
            records.append({
                'zone_exit_type_id': f'ZX{i:04d}',
                'zone_exit_type_code': code,
                'zone_exit_type_name': exit_type,
                'is_controlled': is_controlled,
            })
    df = pd.DataFrame(records) if records else pd.DataFrame(columns=['zone_exit_type_id', 'zone_exit_type_code', 'zone_exit_type_name', 'is_controlled'])
    save_table_func(df, 'dim_zone_exit_type')
    log.info(f"dim_zone_exit_type: {len(df)} rows")


def _create_dim_stoppage_type(output_dir, log, save_table_func):
    """Create dim_stoppage_type from tracking data."""
    records = []
    tracking_path = output_dir / 'fact_event_players.csv'
    if tracking_path.exists():
        tracking = pd.read_csv(tracking_path, low_memory=False)
        if 'event_detail' in tracking.columns:
            stoppage_rows = tracking[tracking['event_type'] == 'Stoppage']
            if len(stoppage_rows) > 0:
                codes = sorted(stoppage_rows['event_detail'].dropna().unique())
                for i, code in enumerate(codes, 1):
                    records.append({
                        'stoppage_type_id': f'SP{i:04d}',
                        'stoppage_type_code': str(code).replace('-', '_'),
                        'stoppage_type_name': str(code).replace('_', ' '),
                    })
    df = pd.DataFrame(records) if records else pd.DataFrame(columns=['stoppage_type_id', 'stoppage_type_code', 'stoppage_type_name'])
    save_table_func(df, 'dim_stoppage_type')
    log.info(f"dim_stoppage_type: {len(df)} rows")


def _create_dim_giveaway_type(output_dir, log, save_table_func):
    """Create dim_giveaway_type from dim_event_detail_2."""
    neutral_patterns = [
        'AttemptedZoneClear', 'DumpInZone', 'ZoneClear',
        'BattleLost', 'Other', 'ShotBlocked', 'ShotMissed',
    ]

    records = []
    dim_path = output_dir / 'dim_event_detail_2.csv'
    if dim_path.exists():
        dim_ed2 = pd.read_csv(dim_path)
        giveaway_rows = dim_ed2[dim_ed2['event_detail_2_code'].str.contains('Giveaway', case=False, na=False)]
        giveaway_codes = sorted(giveaway_rows['event_detail_2_code'].tolist())
        for i, code in enumerate(giveaway_codes, 1):
            code_str = str(code)
            is_bad = not any(pattern in code_str for pattern in neutral_patterns)
            records.append({
                'giveaway_type_id': f'GA{i:04d}',
                'giveaway_type_code': code_str.replace('-', '_'),
                'giveaway_type_name': code_str.replace('_', ' ').replace('/', ' '),
                'is_bad': is_bad,
            })
    df = pd.DataFrame(records) if records else pd.DataFrame(columns=['giveaway_type_id', 'giveaway_type_code', 'giveaway_type_name', 'is_bad'])
    save_table_func(df, 'dim_giveaway_type')
    bad_count = sum(r['is_bad'] for r in records) if records else 0
    neutral_count = len(records) - bad_count if records else 0
    log.info(f"dim_giveaway_type: {len(df)} rows ({bad_count} bad, {neutral_count} neutral)")


def _create_dim_takeaway_type(output_dir, log, save_table_func):
    """Create dim_takeaway_type from dim_event_detail_2."""
    records = []
    dim_path = output_dir / 'dim_event_detail_2.csv'
    if dim_path.exists():
        dim_ed2 = pd.read_csv(dim_path)
        takeaway_rows = dim_ed2[dim_ed2['event_detail_2_code'].str.contains('Takeaway', case=False, na=False)]
        takeaway_codes = sorted(takeaway_rows['event_detail_2_code'].tolist())
        for i, code in enumerate(takeaway_codes, 1):
            code_str = str(code)
            records.append({
                'takeaway_type_id': f'TA{i:04d}',
                'takeaway_type_code': code_str.replace('-', '_'),
                'takeaway_type_name': code_str.replace('_', ' ').replace('/', ' '),
            })
    df = pd.DataFrame(records) if records else pd.DataFrame(columns=['takeaway_type_id', 'takeaway_type_code', 'takeaway_type_name'])
    save_table_func(df, 'dim_takeaway_type')
    log.info(f"dim_takeaway_type: {len(df)} rows")


def _standardize_code(code):
    """Standardize code: replace hyphens/slashes with underscores, fix typos."""
    if not code or pd.isna(code):
        return code
    code = str(code).replace('-', '_').replace('/', '_')
    code = code.replace('Seperate', 'Separate')
    return code


def _create_dim_play_detail(output_dir, log, save_table_func):
    """Create dim_play_detail from PLAY_DETAILS constants and tracking data."""
    from src.models.dimensions import PLAY_DETAILS

    records = []
    for i, p in enumerate(PLAY_DETAILS, 1):
        records.append({
            'play_detail_id': f'PD{i:04d}',
            'play_detail_code': p['play_detail'],
            'play_detail_name': p['play_detail'],
            'play_category': p.get('play_category', 'other').lower(),
            'skill_level': 'Standard',
            'description': p.get('description', 'Micro-play action')
        })

    constant_codes = {p['play_detail'] for p in PLAY_DETAILS}

    tracking_path = output_dir / 'fact_event_players.csv'
    if tracking_path.exists():
        tracking = pd.read_csv(tracking_path, low_memory=False)

        if 'play_detail1' in tracking.columns:
            tracking_codes = set(tracking['play_detail1'].dropna().unique())
            new_codes = tracking_codes - constant_codes

            filtered_new = set()
            for code in new_codes:
                std_code = _standardize_code(code)
                if '_' in std_code:
                    base = std_code.split('_')[-1]
                    if base not in constant_codes and base not in filtered_new:
                        filtered_new.add(std_code)
                else:
                    filtered_new.add(std_code)

            next_id = len(records) + 1
            for code in sorted(filtered_new):
                if code.startswith('Offensive'):
                    category = 'offensive'
                elif code.startswith('Defensive'):
                    category = 'defensive'
                elif 'Recovery' in code or 'Retrieval' in code or 'Retreival' in code:
                    category = 'recovery'
                else:
                    category = 'other'

                records.append({
                    'play_detail_id': f'PD{next_id:04d}',
                    'play_detail_code': code,
                    'play_detail_name': code,
                    'play_category': category,
                    'skill_level': 'Standard',
                    'description': 'Micro-play action from tracking data'
                })
                next_id += 1

    df = pd.DataFrame(records)
    save_table_func(df, 'dim_play_detail')
    log.info(f"dim_play_detail: {len(df)} rows")


def _create_dim_play_detail_2(output_dir, log, save_table_func):
    """Create dim_play_detail_2 from tracking data."""
    records = []

    tracking_path = output_dir / 'fact_event_players.csv'
    if tracking_path.exists():
        tracking = pd.read_csv(tracking_path, low_memory=False)

        if 'play_detail_2' in tracking.columns:
            raw_codes = tracking['play_detail_2'].dropna().unique()
            codes = sorted(set(_standardize_code(c) for c in raw_codes))

            for i, code in enumerate(codes, 1):
                if 'Goal' in code or 'Assist' in code:
                    category = 'scoring'
                elif 'Defensive' in code or 'Block' in code or 'Check' in code:
                    category = 'defensive'
                elif 'Offensive' in code or 'Shot' in code or 'Pass' in code:
                    category = 'offensive'
                else:
                    category = 'other'

                records.append({
                    'play_detail_2_id': f'PD2{i:02d}',
                    'play_detail_2_code': code,
                    'play_detail_2_name': code,
                    'play_category': category,
                    'skill_level': 'Standard',
                    'description': 'Secondary play detail from tracking'
                })

    if records:
        df = pd.DataFrame(records)
        save_table_func(df, 'dim_play_detail_2')
        log.info(f"dim_play_detail_2: {len(df)} rows")
    else:
        df = pd.DataFrame(columns=['play_detail_2_id', 'play_detail_2_code', 'play_detail_2_name',
                                   'play_category', 'skill_level', 'description'])
        save_table_func(df, 'dim_play_detail_2')
        log.info("dim_play_detail_2: 0 rows (no data)")
