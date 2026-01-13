"""
Formula Registry System

Provides a centralized way to define, manage, and apply formulas.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Callable, Optional, Any
from pathlib import Path
import json


class FormulaRegistry:
    """
    Centralized registry for statistical formulas.
    
    Allows formulas to be defined in configuration files or code,
    making updates easier without code changes.
    """
    
    def __init__(self):
        self.formulas: Dict[str, Dict[str, Any]] = {}
        self.formula_functions: Dict[str, Callable] = {}
    
    def register(
        self,
        name: str,
        formula_type: str,
        expression: Optional[str] = None,
        function: Optional[Callable] = None,
        description: str = "",
        dependencies: Optional[List[str]] = None,
        validation: Optional[Callable] = None
    ):
        """
        Register a formula.
        
        Args:
            name: Column name for the formula result
            formula_type: Type of formula ('percentage', 'rate', 'ratio', 'sum', 'custom')
            expression: String expression (e.g., 'numerator / denominator * 100')
            function: Python function to calculate the value
            description: Human-readable description
            dependencies: List of column names this formula depends on
            validation: Optional validation function
        """
        if expression and function:
            raise ValueError("Cannot specify both expression and function")
        
        if not expression and not function:
            raise ValueError("Must specify either expression or function")
        
        self.formulas[name] = {
            'type': formula_type,
            'expression': expression,
            'function': function,
            'description': description,
            'dependencies': dependencies or [],
            'validation': validation,
        }
        
        if function:
            self.formula_functions[name] = function
    
    def apply_to_dataframe(
        self,
        df: pd.DataFrame,
        formula_names: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Apply registered formulas to a DataFrame.
        
        Args:
            df: DataFrame to apply formulas to
            formula_names: Optional list of formula names to apply (all if None)
            
        Returns:
            DataFrame with formula columns added
        """
        df = df.copy()
        
        formulas_to_apply = formula_names or list(self.formulas.keys())
        
        for name in formulas_to_apply:
            if name not in self.formulas:
                continue
            
            formula = self.formulas[name]
            
            # Check dependencies
            missing_deps = [dep for dep in formula['dependencies'] if dep not in df.columns]
            if missing_deps:
                continue  # Skip if dependencies missing
            
            # Apply formula
            if formula['function']:
                # Use function
                df[name] = formula['function'](df)
            elif formula['expression']:
                # Evaluate expression
                df[name] = self._evaluate_expression(df, formula['expression'], formula['type'])
            
            # Validate if validation function provided
            if formula.get('validation'):
                df[name] = formula['validation'](df[name])
        
        return df
    
    def _evaluate_expression(
        self,
        df: pd.DataFrame,
        expression: str,
        formula_type: str
    ) -> pd.Series:
        """
        Evaluate a formula expression on a DataFrame.
        
        Supports common patterns:
        - 'numerator / denominator * 100' for percentages
        - 'value / toi_minutes * 60' for per-60 rates
        - 'col1 + col2' for sums
        - 'col1 - col2' for differences
        """
        # Replace column names in expression with df[col]
        # Simple implementation - can be enhanced
        try:
            # For now, use eval with safe namespace
            namespace = {col: df[col] for col in df.columns if col in expression}
            namespace.update({'np': np, 'pd': pd})
            
            # Parse expression (simplified - assumes column names are valid Python identifiers)
            result = eval(expression, {"__builtins__": {}}, namespace)
            
            if isinstance(result, pd.Series):
                return result
            else:
                # Scalar result - broadcast
                return pd.Series([result] * len(df), index=df.index)
        except Exception as e:
            # Return NaN if evaluation fails
            return pd.Series([np.nan] * len(df), index=df.index)
    
    def get_formula(self, name: str) -> Optional[Dict[str, Any]]:
        """Get formula definition by name."""
        return self.formulas.get(name)
    
    def list_formulas(self) -> List[str]:
        """List all registered formula names."""
        return list(self.formulas.keys())
    
    def export_to_json(self, path: Path):
        """Export formulas to JSON file."""
        export_data = {}
        for name, formula in self.formulas.items():
            export_data[name] = {
                'type': formula['type'],
                'expression': formula['expression'],
                'description': formula['description'],
                'dependencies': formula['dependencies'],
            }
            # Functions can't be serialized, so skip them
        
        with open(path, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    def load_from_json(self, path: Path):
        """Load formulas from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)
        
        for name, formula_data in data.items():
            self.register(
                name=name,
                formula_type=formula_data['type'],
                expression=formula_data.get('expression'),
                description=formula_data.get('description', ''),
                dependencies=formula_data.get('dependencies', [])
            )


# Global registry instance
_registry = FormulaRegistry()


def get_registry() -> FormulaRegistry:
    """Get the global formula registry."""
    return _registry


def apply_formulas(df: pd.DataFrame, formula_names: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Convenience function to apply formulas from global registry.
    
    Args:
        df: DataFrame to apply formulas to
        formula_names: Optional list of formula names to apply
        
    Returns:
        DataFrame with formulas applied
    """
    return _registry.apply_to_dataframe(df, formula_names)
