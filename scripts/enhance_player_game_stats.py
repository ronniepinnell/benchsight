#!/usr/bin/env python3
"""
Enhance fact_player_game_stats with rating columns from fact_shift_quality_logical.

This script adds:
- Raw plus/minus (gf_all, ga_all, pm_all)
- Rating-adjusted stats (gf_adj, ga_adj, pm_adj)
- Corsi adjustments (cf_adj, ca_adj, cf_pct_adj)
- Competition metrics (qoc_precise, avg_opp_rating, avg_rating_advantage)
- Expected performance (expected_pm, pm_vs_expected, performance_flag)
- Per-60 adjusted rates

Version: 6.5.19
Date: January 6, 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Configuration
BASELINE_RATING = 4.0
OUTPUT_DIR = Path('data/output')


def enhance_player_game_stats():
    """Add rating columns to fact_player_game_stats."""
    
    print("=" * 60)
    print("Enhancing fact_player_game_stats with rating columns")
    print("=" * 60)
    
    # Load source tables
    pgs_path = OUTPUT_DIR / 'fact_player_game_stats.csv'
    sql_path = OUTPUT_DIR / 'fact_shift_quality_logical.csv'
    
    pgs = pd.read_csv(pgs_path)
    sql = pd.read_csv(sql_path)
    
    orig_cols = len(pgs.columns)
    orig_rows = len(pgs)
    
    print(f"\nSource: fact_player_game_stats - {orig_rows} rows, {orig_cols} columns")
    print(f"Rating source: fact_shift_quality_logical - {len(sql)} rows, {len(sql.columns)} columns")
    
    # Columns to bring in from shift_quality_logical
    # (Rename some to avoid conflicts with existing columns)
    rating_cols_to_add = {
        'avg_opp_rating': 'avg_opp_rating_precise',  # Keep existing opp_avg_rating, add precise version
        'gf_all': 'gf_all_shift',          # Goals for (all situations) from shifts
        'ga_all': 'ga_all_shift',          # Goals against (all situations) from shifts
        'pm_all': 'pm_all_shift',          # Plus/minus (all) from shifts
        'gf_adj': 'gf_adj',                # Rating-adjusted goals for
        'ga_adj': 'ga_adj',                # Rating-adjusted goals against
        'pm_adj': 'pm_adj',                # Rating-adjusted plus/minus
        'cf': 'cf_shift',                  # Corsi for from shifts
        'ca': 'ca_shift',                  # Corsi against from shifts
        'avg_quality_score': 'avg_shift_quality_score',  # Average shift quality
        'qoc': 'qoc_precise',              # Quality of Competition (precise)
        'expected_pm': 'expected_pm',       # Expected plus/minus based on matchups
        'pm_vs_expected': 'pm_vs_expected', # Performance vs expected
        'performance': 'performance_flag',  # Over/Under/Expected
    }
    
    # Create mapping for merge
    sql_cols_to_merge = ['game_id', 'player_id'] + list(rating_cols_to_add.keys())
    sql_subset = sql[sql_cols_to_merge].copy()
    
    # Rename columns
    sql_subset = sql_subset.rename(columns=rating_cols_to_add)
    
    # Check which columns already exist (to avoid duplicates)
    existing_new_cols = [c for c in sql_subset.columns if c in pgs.columns and c not in ['game_id', 'player_id']]
    if existing_new_cols:
        print(f"\nWarning: These columns already exist and will be updated: {existing_new_cols}")
        # Drop existing columns that we're replacing
        pgs = pgs.drop(columns=existing_new_cols)
    
    # Merge rating columns
    pgs = pgs.merge(
        sql_subset,
        on=['game_id', 'player_id'],
        how='left'
    )
    
    new_cols_added = len(pgs.columns) - orig_cols
    print(f"\nMerged {new_cols_added} new columns from shift_quality_logical")
    
    # Calculate additional metrics
    print("\nCalculating additional metrics...")
    
    # Rating advantage
    pgs['avg_rating_advantage'] = np.where(
        pgs['player_rating'].notna() & pgs['avg_opp_rating_precise'].notna(),
        pgs['player_rating'] - pgs['avg_opp_rating_precise'],
        np.nan
    )
    
    # Adjusted Corsi (apply same formula as plus/minus)
    # opp_multiplier = avg_opp_rating / BASELINE_RATING
    # cf_adj = cf × opp_multiplier (bonus for Corsi vs good teams)
    # ca_adj = ca / opp_multiplier (less penalty vs good teams)
    pgs['opp_multiplier'] = pgs['avg_opp_rating_precise'] / BASELINE_RATING
    
    pgs['cf_adj'] = np.where(
        pgs['opp_multiplier'].notna() & pgs['corsi_for'].notna(),
        pgs['corsi_for'] * pgs['opp_multiplier'],
        pgs['corsi_for']  # Fall back to raw if no rating data
    )
    
    pgs['ca_adj'] = np.where(
        (pgs['opp_multiplier'].notna()) & (pgs['opp_multiplier'] > 0) & pgs['corsi_against'].notna(),
        pgs['corsi_against'] / pgs['opp_multiplier'],
        pgs['corsi_against']
    )
    
    # Adjusted Corsi percentage
    pgs['cf_pct_adj'] = np.where(
        (pgs['cf_adj'] + pgs['ca_adj']) > 0,
        pgs['cf_adj'] / (pgs['cf_adj'] + pgs['ca_adj']) * 100,
        50.0  # Default to 50% if no Corsi events
    )
    
    # Clean up intermediate column
    pgs = pgs.drop(columns=['opp_multiplier'])
    
    # Per-60 adjusted rates
    toi_hours = pgs['toi_seconds'] / 3600
    
    per_60_stats = {
        'gf_adj_per_60': 'gf_adj',
        'ga_adj_per_60': 'ga_adj',
        'pm_adj_per_60': 'pm_adj',
        'cf_adj_per_60': 'cf_adj',
        'ca_adj_per_60': 'ca_adj',
    }
    
    for new_col, source_col in per_60_stats.items():
        pgs[new_col] = np.where(
            (toi_hours > 0) & pgs[source_col].notna(),
            pgs[source_col] / toi_hours,
            0
        )
    
    # Summary stats
    final_cols = len(pgs.columns)
    new_total = final_cols - orig_cols
    
    print(f"\n{'=' * 60}")
    print("ENHANCEMENT SUMMARY")
    print(f"{'=' * 60}")
    print(f"Original columns: {orig_cols}")
    print(f"Final columns: {final_cols}")
    print(f"Net new columns: {new_total}")
    print(f"Rows: {len(pgs)}")
    
    # Verify new columns
    new_rating_cols = [c for c in pgs.columns if c not in pd.read_csv(pgs_path).columns]
    print(f"\nNew columns added ({len(new_rating_cols)}):")
    for col in new_rating_cols:
        non_null = pgs[col].notna().sum()
        print(f"  {col}: {non_null}/{len(pgs)} populated")
    
    # Save
    pgs.to_csv(pgs_path, index=False)
    print(f"\n✓ Saved enhanced fact_player_game_stats.csv")
    
    return pgs


def validate_enhancement():
    """Validate the enhancement was successful."""
    print("\n" + "=" * 60)
    print("VALIDATION")
    print("=" * 60)
    
    pgs = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv')
    sql = pd.read_csv(OUTPUT_DIR / 'fact_shift_quality_logical.csv')
    
    # Check a sample record
    sample_game = pgs['game_id'].iloc[0]
    sample_player = pgs['player_id'].iloc[0]
    
    pgs_row = pgs[(pgs['game_id'] == sample_game) & (pgs['player_id'] == sample_player)].iloc[0]
    sql_row = sql[(sql['game_id'] == sample_game) & (sql['player_id'] == sample_player)]
    
    if len(sql_row) > 0:
        sql_row = sql_row.iloc[0]
        print(f"\nSample comparison (game {sample_game}, player {pgs_row['player_name']}):")
        print(f"  player_rating: PGS={pgs_row.get('player_rating')}, SQL={sql_row.get('player_rating')}")
        print(f"  pm_adj: PGS={pgs_row.get('pm_adj'):.3f}, SQL={sql_row.get('pm_adj'):.3f}")
        print(f"  qoc_precise: PGS={pgs_row.get('qoc_precise'):.4f}, SQL={sql_row.get('qoc'):.4f}")
        print(f"  performance_flag: PGS={pgs_row.get('performance_flag')}, SQL={sql_row.get('performance')}")
        
        # Check values match
        if abs(pgs_row.get('pm_adj', 0) - sql_row.get('pm_adj', 0)) < 0.001:
            print("\n✓ Values match between tables")
        else:
            print("\n⚠ WARNING: Values don't match!")
    else:
        print(f"\n⚠ Could not find matching record in shift_quality_logical")
    
    # Summary statistics
    print("\n" + "-" * 40)
    print("Rating column statistics:")
    for col in ['gf_adj', 'ga_adj', 'pm_adj', 'cf_pct_adj', 'avg_rating_advantage']:
        if col in pgs.columns:
            stats = pgs[col].describe()
            print(f"  {col}: mean={stats['mean']:.2f}, min={stats['min']:.2f}, max={stats['max']:.2f}")


if __name__ == '__main__':
    enhance_player_game_stats()
    validate_enhancement()
    print("\n✓ Enhancement complete!")
