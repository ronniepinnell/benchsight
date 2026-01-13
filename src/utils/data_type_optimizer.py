"""
Data Type Optimizer

Optimizes pandas DataFrame data types for better memory usage and performance.
- Uses categorical types for repeated strings
- Uses int8/int16 for small integers
- Uses float32 where precision allows

Version: 29.6
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


def optimize_dataframe_dtypes(
    df: pd.DataFrame,
    categorical_threshold: int = 10,
    max_categories: int = 1000,
    optimize_floats: bool = True
) -> pd.DataFrame:
    """
    Optimize DataFrame data types for memory and performance.
    
    Args:
        df: DataFrame to optimize
        categorical_threshold: Minimum unique values to consider categorical (default: 10)
        max_categories: Maximum categories before skipping (default: 1000)
        optimize_floats: Whether to convert float64 to float32 (default: True)
        
    Returns:
        Optimized DataFrame
    """
    df = df.copy()
    
    for col in df.columns:
        dtype = df[col].dtype
        
        # Skip if already optimized
        if dtype.name.startswith('category'):
            continue
        
        # Object/string columns - convert to categorical if appropriate
        if dtype == 'object':
            unique_count = df[col].nunique()
            total_count = len(df[col].dropna())
            
            # Convert to categorical if:
            # - Has repeated values (unique < threshold)
            # - Not too many unique values (unique < max_categories)
            # - Has enough data to benefit
            if (unique_count < categorical_threshold or 
                (unique_count < max_categories and total_count > unique_count * 2)):
                try:
                    df[col] = df[col].astype('category')
                except (ValueError, TypeError):
                    # Can't convert to categorical (e.g., mixed types)
                    pass
        
        # Integer columns - downcast if possible
        elif dtype.name.startswith('int'):
            col_min = df[col].min() if len(df[col].dropna()) > 0 else 0
            col_max = df[col].max() if len(df[col].dropna()) > 0 else 0
            
            # Determine appropriate integer type
            if col_min >= -128 and col_max <= 127:
                df[col] = pd.to_numeric(df[col], downcast='integer')
            elif col_min >= -32768 and col_max <= 32767:
                df[col] = pd.to_numeric(df[col], downcast='integer')
            elif col_min >= 0 and col_max <= 255:
                df[col] = pd.to_numeric(df[col], downcast='unsigned')
            else:
                # Try downcast anyway (pandas will choose appropriate size)
                df[col] = pd.to_numeric(df[col], downcast='integer')
        
        # Float columns - convert to float32 if appropriate
        elif optimize_floats and dtype.name.startswith('float'):
            # Check if precision loss is acceptable
            # For most stats, float32 is sufficient (7 decimal digits)
            if dtype == 'float64':
                # Check if values fit in float32 range
                col_min = df[col].min() if len(df[col].dropna()) > 0 else 0
                col_max = df[col].max() if len(df[col].dropna()) > 0 else 0
                
                # float32 range: -3.4e38 to 3.4e38
                if (col_min >= -3.4e38 and col_max <= 3.4e38):
                    try:
                        df[col] = df[col].astype('float32')
                    except (ValueError, OverflowError):
                        # Can't convert (precision loss or overflow)
                        pass
    
    return df


def optimize_specific_columns(
    df: pd.DataFrame,
    column_config: Dict[str, str]
) -> pd.DataFrame:
    """
    Optimize specific columns with explicit type mappings.
    
    Args:
        df: DataFrame to optimize
        column_config: Dict mapping column names to target types
                      ('category', 'int8', 'int16', 'float32', etc.)
        
    Returns:
        Optimized DataFrame
    """
    df = df.copy()
    
    for col, target_type in column_config.items():
        if col not in df.columns:
            continue
        
        try:
            if target_type == 'category':
                df[col] = df[col].astype('category')
            elif target_type in ['int8', 'int16', 'int32', 'int64']:
                df[col] = pd.to_numeric(df[col], downcast='integer').astype(target_type)
            elif target_type in ['float32', 'float64']:
                df[col] = pd.to_numeric(df[col], downcast='float').astype(target_type)
            else:
                df[col] = df[col].astype(target_type)
        except (ValueError, TypeError, OverflowError):
            # Skip if conversion fails
            pass
    
    return df


def get_optimization_suggestions(df: pd.DataFrame) -> Dict[str, Dict]:
    """
    Analyze DataFrame and suggest optimizations.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Dict with column names as keys and optimization suggestions as values
    """
    suggestions = {}
    
    for col in df.columns:
        dtype = df[col].dtype
        unique_count = df[col].nunique()
        null_count = df[col].isna().sum()
        total_count = len(df[col])
        
        col_suggestions = {
            'current_type': str(dtype),
            'unique_count': unique_count,
            'null_count': null_count,
            'optimizations': []
        }
        
        # String/object columns
        if dtype == 'object':
            if unique_count < 50 and total_count > unique_count * 2:
                col_suggestions['optimizations'].append({
                    'type': 'category',
                    'reason': f'Only {unique_count} unique values in {total_count} rows',
                    'estimated_savings': '50-80% memory'
                })
        
        # Integer columns
        elif dtype.name.startswith('int'):
            col_min = df[col].min() if len(df[col].dropna()) > 0 else 0
            col_max = df[col].max() if len(df[col].dropna()) > 0 else 0
            
            if col_min >= -128 and col_max <= 127:
                col_suggestions['optimizations'].append({
                    'type': 'int8',
                    'reason': f'Values in range [{col_min}, {col_max}]',
                    'estimated_savings': '75% memory'
                })
            elif col_min >= -32768 and col_max <= 32767:
                col_suggestions['optimizations'].append({
                    'type': 'int16',
                    'reason': f'Values in range [{col_min}, {col_max}]',
                    'estimated_savings': '50% memory'
                })
        
        # Float columns
        elif dtype.name.startswith('float') and dtype == 'float64':
            col_suggestions['optimizations'].append({
                'type': 'float32',
                'reason': 'Most stats don\'t need float64 precision',
                'estimated_savings': '50% memory'
            })
        
        if col_suggestions['optimizations']:
            suggestions[col] = col_suggestions
    
    return suggestions


def calculate_memory_savings(original_df: pd.DataFrame, optimized_df: pd.DataFrame) -> Dict:
    """
    Calculate memory savings from optimization.
    
    Args:
        original_df: Original DataFrame
        optimized_df: Optimized DataFrame
        
    Returns:
        Dict with memory usage and savings information
    """
    original_memory = original_df.memory_usage(deep=True).sum()
    optimized_memory = optimized_df.memory_usage(deep=True).sum()
    
    savings = original_memory - optimized_memory
    savings_pct = (savings / original_memory * 100) if original_memory > 0 else 0
    
    return {
        'original_memory_mb': original_memory / 1024 / 1024,
        'optimized_memory_mb': optimized_memory / 1024 / 1024,
        'savings_mb': savings / 1024 / 1024,
        'savings_pct': savings_pct
    }
