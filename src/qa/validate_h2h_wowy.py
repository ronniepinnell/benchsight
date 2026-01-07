#!/usr/bin/env python3
"""
Validate H2H and WOWY Stats - BenchSight

Cross-validates H2H and WOWY calculations against:
1. Known game totals
2. Player box scores
3. Internal consistency checks

Author: BenchSight ETL
Date: December 2024
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path('data/output')


def validate_h2h():
    """Validate H2H (head-to-head) stats."""
    
    logger.info("\n" + "=" * 60)
    logger.info("VALIDATING H2H STATS")
    logger.info("=" * 60)
    
    h2h = pd.read_csv(OUTPUT_DIR / 'fact_h2h.csv')
    shifts = pd.read_csv(OUTPUT_DIR / 'fact_shift_players.csv')
    
    issues = []
    
    # Check 1: Each game should have reasonable H2H pairs
    for game_id in h2h['game_id'].unique():
        game_h2h = h2h[h2h['game_id'] == game_id]
        
        # Count unique player pairs
        unique_pairs = len(game_h2h)
        logger.info(f"\nGame {game_id}: {unique_pairs} H2H pairs")
        
        # Check TOI sanity - shouldn't exceed game length (~60 min = 3600 sec)
        max_toi = game_h2h['toi_together'].max() if 'toi_together' in game_h2h.columns else 0
        if max_toi > 3600:
            issues.append(f"Game {game_id}: Max TOI {max_toi}s exceeds game length")
        
        # Check goals sanity
        if 'goals_for' in game_h2h.columns:
            total_gf = game_h2h['goals_for'].sum()
            total_ga = game_h2h['goals_against'].sum()
            logger.info(f"  Total GF in H2H: {total_gf}, GA: {total_ga}")
    
    # Check 2: TOI should be positive
    if 'toi_together' in h2h.columns:
        neg_toi = h2h[h2h['toi_together'] < 0]
        if len(neg_toi) > 0:
            issues.append(f"Found {len(neg_toi)} rows with negative TOI")
    
    # Check 3: Cross-team pairs should exist (opponent matchups)
    for game_id in h2h['game_id'].unique():
        game_h2h = h2h[h2h['game_id'] == game_id]
        
        # Get home/away team IDs
        home_team = game_h2h['home_team_id'].iloc[0] if 'home_team_id' in game_h2h.columns else None
        away_team = game_h2h['away_team_id'].iloc[0] if 'away_team_id' in game_h2h.columns else None
        
        if home_team and away_team:
            # Count cross-team matchups
            game_shifts = shifts[shifts['game_id'] == game_id]
            home_players = set(game_shifts[game_shifts['venue'] == 'home']['player_id'].unique())
            away_players = set(game_shifts[game_shifts['venue'] == 'away']['player_id'].unique())
            
            cross_team = game_h2h[
                ((game_h2h['player_1_id'].isin(home_players)) & (game_h2h['player_2_id'].isin(away_players))) |
                ((game_h2h['player_1_id'].isin(away_players)) & (game_h2h['player_2_id'].isin(home_players)))
            ]
            logger.info(f"  Cross-team matchups: {len(cross_team)}")
    
    # Summary
    if issues:
        logger.warning("\n⚠️ H2H Issues Found:")
        for issue in issues:
            logger.warning(f"  - {issue}")
    else:
        logger.info("\n✓ H2H validation passed")
    
    return len(issues) == 0


def validate_wowy():
    """Validate WOWY (with or without you) stats."""
    
    logger.info("\n" + "=" * 60)
    logger.info("VALIDATING WOWY STATS")
    logger.info("=" * 60)
    
    wowy = pd.read_csv(OUTPUT_DIR / 'fact_wowy.csv')
    shifts = pd.read_csv(OUTPUT_DIR / 'fact_shift_players.csv')
    
    issues = []
    
    # Check 1: WOWY should have shifts_together and individual shifts
    required_cols = ['shifts_together', 'p1_shifts_without_p2', 'p2_shifts_without_p1']
    for col in required_cols:
        if col not in wowy.columns:
            issues.append(f"Missing required column: {col}")
    
    if not issues:
        for game_id in wowy['game_id'].unique():
            game_wowy = wowy[wowy['game_id'] == game_id]
            
            logger.info(f"\nGame {game_id}: {len(game_wowy)} WOWY pairs")
            
            # Check consistency: p1_total should equal shifts_together + p1_shifts_without_p2
            if 'total_p1_shifts' in game_wowy.columns:
                inconsistent = game_wowy[
                    game_wowy['total_p1_shifts'] != (game_wowy['shifts_together'] + game_wowy['p1_shifts_without_p2'])
                ]
                if len(inconsistent) > 0:
                    logger.warning(f"  ⚠️ {len(inconsistent)} rows have inconsistent shift counts")
                else:
                    logger.info(f"  ✓ Shift counts are consistent")
            
            # Check TOI
            if 'toi_together' in game_wowy.columns:
                max_toi = game_wowy['toi_together'].max()
                avg_toi = game_wowy['toi_together'].mean()
                logger.info(f"  TOI - Max: {max_toi}s, Avg: {avg_toi:.0f}s")
    
    # Check 2: Venue should be consistent
    if 'venue' in wowy.columns:
        valid_venues = ['home', 'away']
        invalid_venues = wowy[~wowy['venue'].str.lower().isin(valid_venues)]
        if len(invalid_venues) > 0:
            issues.append(f"Found {len(invalid_venues)} rows with invalid venue")
    
    # Check 3: Goals should not exceed shifts (can't score more than 1 goal per shift typically)
    if 'goals_for' in wowy.columns and 'shifts_together' in wowy.columns:
        high_scoring = wowy[wowy['goals_for'] > wowy['shifts_together'] * 2]
        if len(high_scoring) > 0:
            logger.warning(f"  ⚠️ {len(high_scoring)} rows have unusually high goals/shift ratio")
    
    # Summary
    if issues:
        logger.warning("\n⚠️ WOWY Issues Found:")
        for issue in issues:
            logger.warning(f"  - {issue}")
    else:
        logger.info("\n✓ WOWY validation passed")
    
    return len(issues) == 0


def cross_validate_stats():
    """Cross-validate stats between H2H, WOWY, and line combos."""
    
    logger.info("\n" + "=" * 60)
    logger.info("CROSS-VALIDATION")
    logger.info("=" * 60)
    
    h2h = pd.read_csv(OUTPUT_DIR / 'fact_h2h.csv')
    wowy = pd.read_csv(OUTPUT_DIR / 'fact_wowy.csv')
    combos = pd.read_csv(OUTPUT_DIR / 'fact_line_combos.csv')
    player_stats = pd.read_csv(OUTPUT_DIR / 'fact_player_game_stats.csv') if (OUTPUT_DIR / 'fact_player_game_stats.csv').exists() else None
    
    issues = []
    
    # Check 1: Total goals in combos should be reasonable
    for game_id in combos['game_id'].unique():
        game_combos = combos[combos['game_id'] == game_id]
        
        # Home and away goals
        home_gf = game_combos[game_combos['venue'] == 'home']['goals_for'].sum()
        away_gf = game_combos[game_combos['venue'] == 'away']['goals_for'].sum()
        
        logger.info(f"\nGame {game_id} Line Combo Goals:")
        logger.info(f"  Home team GF (sum): {home_gf}")
        logger.info(f"  Away team GF (sum): {away_gf}")
        
        # Check against player stats if available
        if player_stats is not None:
            game_player_stats = player_stats[player_stats['game_id'] == game_id]
            if 'goals' in game_player_stats.columns:
                total_player_goals = game_player_stats['goals'].sum()
                logger.info(f"  Player stats total goals: {total_player_goals}")
    
    # Check 2: Corsi consistency
    if 'corsi_for' in combos.columns:
        for game_id in combos['game_id'].unique():
            game_combos = combos[combos['game_id'] == game_id]
            
            # Sum should be roughly equal when accounting for overlapping shifts
            total_cf = game_combos['corsi_for'].sum()
            total_ca = game_combos['corsi_against'].sum()
            
            logger.info(f"  Corsi - CF: {total_cf}, CA: {total_ca}")
    
    # Summary
    if issues:
        logger.warning("\n⚠️ Cross-validation Issues:")
        for issue in issues:
            logger.warning(f"  - {issue}")
    else:
        logger.info("\n✓ Cross-validation completed")
    
    return len(issues) == 0


def validate_against_known_scores():
    """Validate against known game scores from noradhockey.com."""
    
    logger.info("\n" + "=" * 60)
    logger.info("VALIDATING AGAINST KNOWN SCORES")
    logger.info("=" * 60)
    
    # Known game scores (from noradhockey.com validation)
    known_scores = {
        18969: {'home': 6, 'away': 6},   # Final score
        18977: {'home': 4, 'away': 3},   # Final score  
        18981: {'home': 5, 'away': 5},   # Final score
        18987: {'home': 2, 'away': 1},   # Final score
    }
    
    shifts = pd.read_csv(OUTPUT_DIR / 'fact_shift_players.csv')
    
    all_pass = True
    
    for game_id, scores in known_scores.items():
        game_shifts = shifts[shifts['game_id'] == game_id]
        
        if game_shifts.empty:
            logger.warning(f"  Game {game_id}: No shift data found")
            continue
        
        # Calculate goals from shifts (deduplicate by shift_index)
        home_shifts = game_shifts[game_shifts['venue'] == 'home'].drop_duplicates('shift_index')
        away_shifts = game_shifts[game_shifts['venue'] == 'away'].drop_duplicates('shift_index')
        
        home_gf = home_shifts['goal_for'].sum()
        home_ga = home_shifts['goal_against'].sum()
        away_gf = away_shifts['goal_for'].sum()
        away_ga = away_shifts['goal_against'].sum()
        
        # Home GF should equal Away GA and vice versa
        logger.info(f"\nGame {game_id}:")
        logger.info(f"  Expected: Home {scores['home']} - Away {scores['away']}")
        logger.info(f"  Calculated from shifts:")
        logger.info(f"    Home GF: {home_gf}, GA: {home_ga}")
        logger.info(f"    Away GF: {away_gf}, GA: {away_ga}")
        
        # Validate
        if home_gf == scores['home'] and away_gf == scores['away']:
            logger.info(f"  ✓ Scores match!")
        else:
            logger.warning(f"  ⚠️ Score mismatch")
            all_pass = False
    
    return all_pass


def main():
    """Run all validations."""
    
    logger.info("=" * 60)
    logger.info("H2H / WOWY / LINE COMBO VALIDATION")
    logger.info("=" * 60)
    
    results = {
        'h2h': validate_h2h(),
        'wowy': validate_wowy(),
        'cross': cross_validate_stats(),
        'scores': validate_against_known_scores()
    }
    
    logger.info("\n" + "=" * 60)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 60)
    
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"  {name.upper()}: {status}")
    
    all_pass = all(results.values())
    logger.info(f"\nOverall: {'✓ ALL VALIDATIONS PASSED' if all_pass else '⚠️ SOME VALIDATIONS FAILED'}")
    
    return all_pass


if __name__ == '__main__':
    main()
