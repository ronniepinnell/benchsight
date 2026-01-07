#!/usr/bin/env python3
"""
Create consolidated dim_rink_zone table.

Combines three granularity levels into one table:
- coarse (19 zones): General zone analytics (OZ/NZ/DZ areas)
- medium (50 boxes): Shot location and danger zone analysis
- fine (198 zones): Detailed XY coordinate tracking

Source tables (archived in data/output/archive/rink_coord_tables/):
- dim_rink_coord.csv -> coarse granularity
- dim_rinkboxcoord.csv -> medium granularity
- dim_rinkcoordzones.csv -> fine granularity (cleaned of empty rows)

Output: data/output/dim_rink_zone.csv (267 rows)
"""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
OUTPUT_DIR = Path('data/output')
ARCHIVE_DIR = OUTPUT_DIR / 'archive' / 'rink_coord_tables'


def create_dim_rink_zone():
    """Create consolidated rink zone dimension table."""
    logger.info("Creating consolidated dim_rink_zone...")
    
    # Check for archived source files first, fall back to output dir
    if ARCHIVE_DIR.exists():
        rink_coord_path = ARCHIVE_DIR / 'dim_rink_coord.csv'
        rinkbox_path = ARCHIVE_DIR / 'dim_rinkboxcoord.csv'
        rinkzones_path = ARCHIVE_DIR / 'dim_rinkcoordzones.csv'
    else:
        rink_coord_path = OUTPUT_DIR / 'dim_rink_coord.csv'
        rinkbox_path = OUTPUT_DIR / 'dim_rinkboxcoord.csv'
        rinkzones_path = OUTPUT_DIR / 'dim_rinkcoordzones.csv'
    
    rows = []
    
    # 1. COARSE granularity (19 zones) - from dim_rink_coord
    if rink_coord_path.exists():
        rink_coord = pd.read_csv(rink_coord_path)
        logger.info(f"  Loading coarse: {len(rink_coord)} rows from {rink_coord_path.name}")
        
        for _, row in rink_coord.iterrows():
            # Determine zone from code prefix
            code = row['rink_coord_code']
            if code.startswith('OZ'):
                zone = 'offensive'
            elif code.startswith('DZ'):
                zone = 'defensive'
            else:
                zone = 'neutral'
            
            rows.append({
                'rink_zone_id': row['rink_coord_id'],
                'zone_code': row['rink_coord_code'],
                'zone_name': row['rink_coord_name'],
                'granularity': 'coarse',
                'x_min': row['x_min'],
                'x_max': row['x_max'],
                'y_min': row['y_min'],
                'y_max': row['y_max'],
                'zone': zone,
                'danger': None,
                'side': None,
                'x_description': None,
                'y_description': None,
            })
    else:
        # Generate coarse zones from scratch
        logger.info("  Generating coarse zones from definition...")
        coarse_zones = [
            {'id': 'RC0001', 'code': 'OZ_SLOT', 'name': 'Offensive Zone - Slot', 'x_min': 54, 'x_max': 89, 'y_min': -22, 'y_max': 22, 'zone': 'offensive'},
            {'id': 'RC0002', 'code': 'OZ_HIGH', 'name': 'Offensive Zone - High', 'x_min': 25, 'x_max': 54, 'y_min': -42, 'y_max': 42, 'zone': 'offensive'},
            {'id': 'RC0003', 'code': 'OZ_LEFT', 'name': 'Offensive Zone - Left Wing', 'x_min': 54, 'x_max': 89, 'y_min': 22, 'y_max': 42, 'zone': 'offensive'},
            {'id': 'RC0004', 'code': 'OZ_RIGHT', 'name': 'Offensive Zone - Right Wing', 'x_min': 54, 'x_max': 89, 'y_min': -42, 'y_max': -22, 'zone': 'offensive'},
            {'id': 'RC0005', 'code': 'OZ_CREASE', 'name': 'Offensive Zone - Crease', 'x_min': 84, 'x_max': 100, 'y_min': -4, 'y_max': 4, 'zone': 'offensive'},
            {'id': 'RC0006', 'code': 'OZ_CORNER_L', 'name': 'Offensive Zone - Left Corner', 'x_min': 72, 'x_max': 100, 'y_min': 26, 'y_max': 42, 'zone': 'offensive'},
            {'id': 'RC0007', 'code': 'OZ_CORNER_R', 'name': 'Offensive Zone - Right Corner', 'x_min': 72, 'x_max': 100, 'y_min': -42, 'y_max': -26, 'zone': 'offensive'},
            {'id': 'RC0008', 'code': 'NZ_CENTER', 'name': 'Neutral Zone - Center', 'x_min': -25, 'x_max': 25, 'y_min': -22, 'y_max': 22, 'zone': 'neutral'},
            {'id': 'RC0009', 'code': 'NZ_LEFT', 'name': 'Neutral Zone - Left', 'x_min': -25, 'x_max': 25, 'y_min': 22, 'y_max': 42, 'zone': 'neutral'},
            {'id': 'RC0010', 'code': 'NZ_RIGHT', 'name': 'Neutral Zone - Right', 'x_min': -25, 'x_max': 25, 'y_min': -42, 'y_max': -22, 'zone': 'neutral'},
            {'id': 'RC0011', 'code': 'DZ_SLOT', 'name': 'Defensive Zone - Slot', 'x_min': -89, 'x_max': -54, 'y_min': -22, 'y_max': 22, 'zone': 'defensive'},
            {'id': 'RC0012', 'code': 'DZ_HIGH', 'name': 'Defensive Zone - High', 'x_min': -54, 'x_max': -25, 'y_min': -42, 'y_max': 42, 'zone': 'defensive'},
            {'id': 'RC0013', 'code': 'DZ_LEFT', 'name': 'Defensive Zone - Left Wing', 'x_min': -89, 'x_max': -54, 'y_min': 22, 'y_max': 42, 'zone': 'defensive'},
            {'id': 'RC0014', 'code': 'DZ_RIGHT', 'name': 'Defensive Zone - Right Wing', 'x_min': -89, 'x_max': -54, 'y_min': -42, 'y_max': -22, 'zone': 'defensive'},
            {'id': 'RC0015', 'code': 'DZ_CREASE', 'name': 'Defensive Zone - Crease', 'x_min': -100, 'x_max': -84, 'y_min': -4, 'y_max': 4, 'zone': 'defensive'},
            {'id': 'RC0016', 'code': 'DZ_CORNER_L', 'name': 'Defensive Zone - Left Corner', 'x_min': -100, 'x_max': -72, 'y_min': 26, 'y_max': 42, 'zone': 'defensive'},
            {'id': 'RC0017', 'code': 'DZ_CORNER_R', 'name': 'Defensive Zone - Right Corner', 'x_min': -100, 'x_max': -72, 'y_min': -42, 'y_max': -26, 'zone': 'defensive'},
            {'id': 'RC0018', 'code': 'OZ_BEHIND', 'name': 'Behind Offensive Net', 'x_min': 89, 'x_max': 100, 'y_min': -11, 'y_max': 11, 'zone': 'offensive'},
            {'id': 'RC0019', 'code': 'DZ_BEHIND', 'name': 'Behind Defensive Net', 'x_min': -100, 'x_max': -89, 'y_min': -11, 'y_max': 11, 'zone': 'defensive'},
        ]
        for z in coarse_zones:
            rows.append({
                'rink_zone_id': z['id'],
                'zone_code': z['code'],
                'zone_name': z['name'],
                'granularity': 'coarse',
                'x_min': z['x_min'],
                'x_max': z['x_max'],
                'y_min': z['y_min'],
                'y_max': z['y_max'],
                'zone': z['zone'],
                'danger': None,
                'side': None,
                'x_description': None,
                'y_description': None,
            })
    
    # 2. MEDIUM granularity (50 boxes) - from dim_rinkboxcoord
    if rinkbox_path.exists():
        rinkbox = pd.read_csv(rinkbox_path)
        logger.info(f"  Loading medium: {len(rinkbox)} rows from {rinkbox_path.name}")
        
        for _, row in rinkbox.iterrows():
            rows.append({
                'rink_zone_id': 'RB' + str(row['box_id']).zfill(3),
                'zone_code': row['box_id'],
                'zone_name': f"{row['x_description']} - {row['y_description']}",
                'granularity': 'medium',
                'x_min': row['x_min'],
                'x_max': row['x_max'],
                'y_min': row['y_min'],
                'y_max': row['y_max'],
                'zone': row['zone'],
                'danger': row['danger'],
                'side': row['side'],
                'x_description': row['x_description'],
                'y_description': row['y_description'],
            })
    else:
        logger.warning("  No medium granularity source found - skipping")
    
    # 3. FINE granularity (198 zones) - from dim_rinkcoordzones (cleaned)
    if rinkzones_path.exists():
        rinkzones = pd.read_csv(rinkzones_path)
        # Drop empty rows (junk data)
        rinkzones = rinkzones.dropna(subset=['box_id'])
        logger.info(f"  Loading fine: {len(rinkzones)} rows from {rinkzones_path.name} (after cleaning)")
        
        for _, row in rinkzones.iterrows():
            # Fix zone based on X coordinates (source data had bugs)
            x_min = row['x_min']
            x_max = row['x_max']
            
            if x_max < 0:
                zone = 'defensive'
            elif x_min > 0:
                zone = 'offensive'
            elif x_min >= -25 and x_max <= 25:
                zone = 'neutral'
            elif x_min < 0 and x_max > 0:
                zone = 'neutral'
            else:
                zone = row.get('zone', 'neutral')
            
            rows.append({
                'rink_zone_id': 'RZ' + str(row['box_id']).zfill(4),
                'zone_code': row['box_id'],
                'zone_name': f"{row['x_description']} - {row['y_description']}",
                'granularity': 'fine',
                'x_min': row['x_min'],
                'x_max': row['x_max'],
                'y_min': row['y_min'],
                'y_max': row['y_max'],
                'zone': zone,
                'danger': row.get('danger'),
                'side': row.get('side'),
                'x_description': row['x_description'],
                'y_description': row['y_description'],
            })
    else:
        logger.warning("  No fine granularity source found - skipping")
    
    # Create DataFrame and save
    df = pd.DataFrame(rows)
    
    # Summary by granularity
    logger.info("  Zone distribution:")
    for g in ['coarse', 'medium', 'fine']:
        subset = df[df['granularity'] == g]
        if len(subset) > 0:
            zone_counts = subset['zone'].value_counts().to_dict()
            logger.info(f"    {g}: {len(subset)} rows - {zone_counts}")
    
    # Save
    output_path = OUTPUT_DIR / 'dim_rink_zone.csv'
    df.to_csv(output_path, index=False)
    logger.info(f"  ✓ Saved dim_rink_zone.csv: {len(df)} rows")
    
    return df


def main():
    print("=" * 70)
    print("CONSOLIDATED RINK ZONE TABLE BUILDER")
    print("=" * 70)
    
    df = create_dim_rink_zone()
    
    print("\n" + "=" * 70)
    print(f"COMPLETE - dim_rink_zone.csv created with {len(df)} rows")
    print("Granularity levels:")
    print("  - coarse (19): General zone analytics")
    print("  - medium (50): Shot location, danger zones")
    print("  - fine (198): Detailed XY tracking")
    print("=" * 70)


if __name__ == '__main__':
    main()
