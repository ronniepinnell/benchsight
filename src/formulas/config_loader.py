"""
Formula Configuration Loader

Loads formulas from JSON configuration files for easy updates.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
from src.formulas.registry import FormulaRegistry


def load_formulas_from_config(config_path: Path) -> FormulaRegistry:
    """
    Load formulas from JSON configuration file.
    
    Args:
        config_path: Path to formulas.json configuration file
        
    Returns:
        FormulaRegistry with formulas loaded
    """
    registry = FormulaRegistry()
    
    if not config_path.exists():
        return registry
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    formulas = config.get('formulas', {})
    
    for name, formula_def in formulas.items():
        # Convert expression to function
        expression = formula_def.get('expression')
        dependencies = formula_def.get('dependencies', [])
        default_value = formula_def.get('default_value')
        condition = formula_def.get('condition')
        
        if expression:
            # Create function from expression
            func = _create_function_from_expression(
                expression,
                dependencies,
                default_value,
                condition
            )
            
            registry.register(
                name=name,
                formula_type=formula_def.get('type', 'custom'),
                function=func,
                description=formula_def.get('description', ''),
                dependencies=dependencies
            )
    
    return registry


def _create_function_from_expression(
    expression: str,
    dependencies: list,
    default_value: Optional[Any] = None,
    condition: Optional[str] = None
):
    """
    Create a pandas function from an expression string.
    
    Args:
        expression: Formula expression (e.g., 'goals / sog * 100')
        dependencies: List of column names needed
        default_value: Default value if condition fails
        condition: Optional condition string (e.g., 'sog > 0')
        
    Returns:
        Function that can be applied to a DataFrame
    """
    def formula_func(df: pd.DataFrame) -> pd.Series:
        # Check all dependencies exist
        missing = [dep for dep in dependencies if dep not in df.columns]
        if missing:
            return pd.Series([default_value] * len(df), index=df.index)
        
        try:
            # Evaluate expression
            # Replace column names with df[col] references
            eval_expr = expression
            for dep in dependencies:
                eval_expr = eval_expr.replace(dep, f"df['{dep}']")
            
            # Evaluate with safe namespace
            namespace = {'df': df, 'np': np, 'pd': pd}
            result = eval(eval_expr, {"__builtins__": {}}, namespace)
            
            # Apply condition if provided
            if condition:
                # Replace column names in condition
                cond_expr = condition
                for dep in dependencies:
                    cond_expr = cond_expr.replace(dep, f"df['{dep}']")
                
                cond_result = eval(cond_expr, {"__builtins__": {}}, namespace)
                
                # Where condition is False, use default
                if isinstance(result, pd.Series):
                    result = result.where(cond_result, default_value)
            
            # Handle default value
            if default_value is not None and isinstance(result, pd.Series):
                result = result.fillna(default_value)
            
            return result
            
        except Exception as e:
            # Return default on error
            return pd.Series([default_value] * len(df), index=df.index)
    
    return formula_func


def get_formula_config_path() -> Path:
    """Get path to formula configuration file."""
    return Path(__file__).parent.parent.parent / 'config' / 'formulas.json'


def reload_formulas(registry: Optional[FormulaRegistry] = None) -> FormulaRegistry:
    """
    Reload formulas from configuration file.
    
    Useful for updating formulas without restarting the application.
    
    Args:
        registry: Optional existing registry to update
        
    Returns:
        Updated FormulaRegistry
    """
    config_path = get_formula_config_path()
    
    if registry is None:
        return load_formulas_from_config(config_path)
    else:
        # Clear and reload
        new_registry = load_formulas_from_config(config_path)
        registry.formulas = new_registry.formulas
        registry.formula_functions = new_registry.formula_functions
        return registry
