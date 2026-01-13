"""
Formula Applier

Applies formulas from the registry to player game stats.
"""

import pandas as pd
from typing import Dict, List, Optional
from src.formulas.registry import FormulaRegistry
from src.formulas.player_stats_formulas import PLAYER_STATS_FORMULAS, FORMULA_GROUPS


def register_player_stats_formulas(registry: FormulaRegistry):
    """
    Register all player stats formulas with the registry.
    
    Args:
        registry: FormulaRegistry instance to register formulas with
    """
    for name, formula_def in PLAYER_STATS_FORMULAS.items():
        registry.register(
            name=name,
            formula_type=formula_def['type'],
            function=formula_def['function'],
            description=formula_def['description'],
            dependencies=formula_def['dependencies']
        )


def apply_player_stats_formulas(
    df: pd.DataFrame,
    formula_groups: Optional[List[str]] = None,
    formula_names: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Apply player stats formulas to a DataFrame.
    
    Args:
        df: DataFrame with player game stats
        formula_groups: Optional list of formula group names to apply
        formula_names: Optional list of specific formula names to apply
        
    Returns:
        DataFrame with formulas applied
    """
    # Create registry and register formulas
    registry = FormulaRegistry()
    register_player_stats_formulas(registry)
    
    # Determine which formulas to apply
    formulas_to_apply = []
    
    if formula_groups:
        for group_name in formula_groups:
            if group_name in FORMULA_GROUPS:
                formulas_to_apply.extend(FORMULA_GROUPS[group_name])
    
    if formula_names:
        formulas_to_apply.extend(formula_names)
    
    # Remove duplicates
    formulas_to_apply = list(set(formulas_to_apply))
    
    # Apply formulas
    if formulas_to_apply:
        df = registry.apply_to_dataframe(df, formulas_to_apply)
    else:
        # Apply all formulas if none specified
        df = registry.apply_to_dataframe(df)
    
    return df


def update_formula(
    formula_name: str,
    new_function: callable,
    description: Optional[str] = None
):
    """
    Update an existing formula definition.
    
    This allows formulas to be updated without modifying the source file.
    
    Args:
        formula_name: Name of formula to update
        new_function: New function to use for calculation
        description: Optional new description
    """
    if formula_name not in PLAYER_STATS_FORMULAS:
        raise ValueError(f"Formula '{formula_name}' not found")
    
    PLAYER_STATS_FORMULAS[formula_name]['function'] = new_function
    if description:
        PLAYER_STATS_FORMULAS[formula_name]['description'] = description
