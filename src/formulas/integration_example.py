"""
Example: Integrating Formula System into fact_player_game_stats

This shows how to use the formula system in create_fact_player_game_stats()
"""

import pandas as pd
from src.formulas.formula_applier import apply_player_stats_formulas


def create_fact_player_game_stats_with_formulas() -> pd.DataFrame:
    """
    Example of how to integrate formula system into player stats creation.
    
    This replaces hardcoded formulas with the formula registry system.
    """
    # ... existing code to calculate base stats ...
    # (goals, assists, shots, toi_seconds, etc.)
    
    all_stats = []  # List of stat dicts
    
    # ... calculate base stats for each player ...
    # stats = {
    #     'goals': 5,
    #     'assists': 3,
    #     'sog': 10,
    #     'toi_seconds': 1200,
    #     ...
    # }
    # all_stats.append(stats)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_stats)
    
    # Calculate base derived stats (that formulas depend on)
    df['toi_minutes'] = df['toi_seconds'] / 60.0
    df['points'] = df['goals'] + df['assists']  # Or use formula system
    
    # Apply formulas from registry
    # This replaces all the hardcoded formulas like:
    #   stats['shooting_pct'] = round(stats['goals'] / stats['sog'] * 100, 1) if stats['sog'] > 0 else 0.0
    #   stats['goals_per_60'] = round(stats['goals'] / stats['toi_minutes'] * 60, 2) if stats['toi_minutes'] > 0 else 0.0
    
    df = apply_player_stats_formulas(
        df,
        formula_groups=['core_formulas']  # Apply core formulas
    )
    
    # Or apply all formulas
    # df = apply_player_stats_formulas(df)
    
    # Or apply specific formulas
    # df = apply_player_stats_formulas(
    #     df,
    #     formula_names=['shooting_pct', 'cf_pct', 'goals_per_60']
    # )
    
    return df


# Example: Update a formula at runtime
def update_shooting_percentage_formula():
    """
    Example of updating a formula programmatically.
    """
    from src.formulas.formula_applier import update_formula
    
    def new_shooting_pct(df):
        """New formula: include missed shots in denominator."""
        return (df['goals'] / (df['sog'] + df['shots_missed']) * 100).where(
            (df['sog'] + df['shots_missed']) > 0, 0.0
        )
    
    update_formula(
        'shooting_pct',
        new_shooting_pct,
        'Shooting percentage including missed shots'
    )


# Example: Test a formula
def test_formula():
    """
    Example of testing a formula with sample data.
    """
    import pandas as pd
    from src.formulas.formula_applier import apply_player_stats_formulas
    
    # Test data
    test_df = pd.DataFrame({
        'goals': [5, 3, 0],
        'sog': [10, 8, 5],
        'toi_minutes': [20.0, 15.0, 10.0]
    })
    
    # Apply formulas
    result = apply_player_stats_formulas(
        test_df,
        formula_names=['shooting_pct', 'goals_per_60']
    )
    
    print("Shooting %:", result['shooting_pct'].tolist())  # [50.0, 37.5, 0.0]
    print("Goals/60:", result['goals_per_60'].tolist())    # [15.0, 12.0, 0.0]
    
    return result
