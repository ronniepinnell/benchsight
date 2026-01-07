#!/usr/bin/env python3
"""
BenchSight - Terminology Normalization Module

Maps old/variant terminology to current dimension values.
Used during ETL to ensure consistency with dimension tables.
"""

import pandas as pd
from pathlib import Path
from difflib import SequenceMatcher

# Default data directory
DATA_DIR = Path(__file__).parent.parent / "data/output"


def load_mappings(data_dir=DATA_DIR):
    """Load terminology mapping table."""
    mapping_file = data_dir / "dim_terminology_mapping.csv"
    if mapping_file.exists():
        return pd.read_csv(mapping_file, dtype=str)
    return pd.DataFrame(columns=['dimension', 'old_value', 'new_value', 'match_type'])


def load_dimension_values(data_dir=DATA_DIR):
    """Load all valid dimension values."""
    dims = {}
    
    # Event type
    df = pd.read_csv(data_dir / "dim_event_type.csv", dtype=str)
    dims['event_type'] = set(df['event_type_code'].str.lower())
    
    # Event detail
    df = pd.read_csv(data_dir / "dim_event_detail.csv", dtype=str)
    dims['event_detail'] = set(df['event_detail_code'].str.lower())
    
    # Event detail 2
    df = pd.read_csv(data_dir / "dim_event_detail_2.csv", dtype=str)
    dims['event_detail_2'] = set(df['event_detail_2_code'].str.lower())
    
    # Play detail
    df = pd.read_csv(data_dir / "dim_play_detail.csv", dtype=str)
    dims['play_detail'] = set(df['play_detail_code'].str.lower())
    
    return dims


def fuzzy_match(value, valid_values, threshold=0.8):
    """Find best fuzzy match for a value."""
    value_lower = str(value).lower()
    best_match = None
    best_score = 0
    
    for valid in valid_values:
        score = SequenceMatcher(None, value_lower, valid.lower()).ratio()
        if score > best_score and score >= threshold:
            best_score = score
            best_match = valid
    
    return best_match


def normalize_value(value, dimension, mappings=None, valid_values=None, data_dir=DATA_DIR):
    """
    Normalize a single value to its canonical form.
    
    Args:
        value: The value to normalize
        dimension: 'event_type', 'event_detail', 'event_detail_2', 'play_detail'
        mappings: Pre-loaded mappings DataFrame (optional)
        valid_values: Pre-loaded valid values dict (optional)
        data_dir: Path to data directory
        
    Returns:
        Normalized value string, or original if no match found
    """
    if pd.isna(value) or str(value).strip() == '':
        return None
    
    value_str = str(value).strip()
    value_lower = value_str.lower()
    
    # Load mappings if not provided
    if mappings is None:
        mappings = load_mappings(data_dir)
    
    # Load valid values if not provided
    if valid_values is None:
        valid_values = load_dimension_values(data_dir)
    
    # 1. Check if already a valid value (case-insensitive)
    if dimension in valid_values and value_lower in valid_values[dimension]:
        # Return with original casing from dimension table
        return value_str
    
    # 2. Check explicit mappings
    dim_mappings = mappings[mappings['dimension'] == dimension]
    for _, row in dim_mappings.iterrows():
        if str(row['old_value']).lower() == value_lower:
            return row['new_value']
    
    # 3. Try fuzzy matching
    if dimension in valid_values:
        match = fuzzy_match(value_str, valid_values[dimension])
        if match:
            return match
    
    # 4. Return original (will be flagged in validation)
    return value_str


def normalize_dataframe(df, column_mapping, data_dir=DATA_DIR):
    """
    Normalize multiple columns in a DataFrame.
    
    Args:
        df: DataFrame to normalize
        column_mapping: Dict mapping column names to dimension names
            e.g., {'Type': 'event_type', 'event_detail': 'event_detail'}
        data_dir: Path to data directory
        
    Returns:
        DataFrame with normalized values
    """
    # Pre-load mappings and valid values for efficiency
    mappings = load_mappings(data_dir)
    valid_values = load_dimension_values(data_dir)
    
    df_normalized = df.copy()
    
    for col, dimension in column_mapping.items():
        if col in df_normalized.columns:
            df_normalized[col] = df_normalized[col].apply(
                lambda x: normalize_value(x, dimension, mappings, valid_values, data_dir)
            )
    
    return df_normalized


def validate_normalized_data(df, column_mapping, data_dir=DATA_DIR):
    """
    Validate that all values in specified columns are valid dimension values.
    
    Returns:
        Dict with validation results per column
    """
    valid_values = load_dimension_values(data_dir)
    results = {}
    
    for col, dimension in column_mapping.items():
        if col not in df.columns:
            results[col] = {'status': 'missing', 'invalid': []}
            continue
        
        if dimension not in valid_values:
            results[col] = {'status': 'unknown_dimension', 'invalid': []}
            continue
        
        col_values = df[col].dropna().unique()
        invalid = [v for v in col_values if str(v).lower() not in valid_values[dimension]]
        
        results[col] = {
            'status': 'valid' if not invalid else 'has_invalid',
            'invalid': invalid[:10],  # Limit to first 10
            'total': len(col_values),
            'invalid_count': len(invalid)
        }
    
    return results


# Example usage
if __name__ == "__main__":
    # Test normalization
    test_values = [
        ('event_type', 'Turn'),
        ('event_type', 'FaceOff'),
        ('event_type', 'ZoneEntry'),
        ('event_detail', 'Giveaway'),
        ('event_detail_2', 'Wrist'),
        ('event_detail_2', 'BadPass'),
        ('play_detail', 'Deke'),
    ]
    
    print("Terminology Normalization Test")
    print("=" * 50)
    
    for dim, val in test_values:
        normalized = normalize_value(val, dim)
        print(f"{dim}: '{val}' -> '{normalized}'")
