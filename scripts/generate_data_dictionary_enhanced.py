#!/usr/bin/env python3
"""
Enhanced Data Dictionary Generator

Extracts table metadata from:
1. Function docstrings
2. Table creation functions (create_fact_*, create_dim_*)
3. Data sources (load_table calls)
4. Filter contexts (WHERE clauses in code)
5. Column calculations (formulas in code)

Outputs:
- docs/DATA_DICTIONARY_FULL.md - Complete documentation with extracted metadata
- docs/validation_tracker.csv - Column-by-column validation status
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import re
import ast
from typing import Dict, List, Optional

# Import existing metadata
from generate_data_dictionary import TABLE_METADATA, COLUMN_DEFINITIONS

# =============================================================================
# CODE PARSING FUNCTIONS
# =============================================================================

def find_table_creation_function(table_name: str, src_dir: Path) -> Optional[Dict]:
    """
    Find the function that creates a table and extract metadata.
    
    Returns dict with:
    - source_module: Path to file
    - function_name: Name of function
    - docstring: Function docstring
    - data_sources: Tables loaded (from load_table calls)
    - filter_context: Filter conditions (from WHERE clauses)
    """
    # Convert table name to function name pattern
    # fact_player_game_stats -> create_fact_player_game_stats
    # dim_player -> create_dim_player
    if table_name.startswith('fact_'):
        func_pattern = f"create_{table_name}"
    elif table_name.startswith('dim_'):
        func_pattern = f"create_{table_name}"
    else:
        func_pattern = f"create_{table_name}"
    
    result = {
        'source_module': None,
        'function_name': None,
        'docstring': None,
        'data_sources': [],
        'filter_context': [],
        'calculations': []
    }
    
    # Search all Python files in src/
    for py_file in src_dir.rglob('*.py'):
        try:
            content = py_file.read_text(encoding='utf-8')
            
            # Check if function exists in this file
            if func_pattern in content:
                # Try to parse AST
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            if func_pattern in node.name or node.name == func_pattern:
                                result['function_name'] = node.name
                                result['source_module'] = str(py_file.relative_to(src_dir.parent))
                                
                                # Extract docstring
                                if ast.get_docstring(node):
                                    result['docstring'] = ast.get_docstring(node)
                                
                                # Extract data sources (load_table calls)
                                for child in ast.walk(node):
                                    if isinstance(child, ast.Call):
                                        if isinstance(child.func, ast.Name):
                                            if child.func.id == 'load_table':
                                                if child.args:
                                                    arg = child.args[0]
                                                    if isinstance(arg, ast.Constant):
                                                        result['data_sources'].append(arg.value)
                                        
                                        # Also check for attribute calls like load_table('fact_events')
                                        if isinstance(child.func, ast.Attribute):
                                            if child.func.attr == 'load_table':
                                                if child.args:
                                                    arg = child.args[0]
                                                    if isinstance(arg, ast.Constant):
                                                        result['data_sources'].append(arg.value)
                                
                                # Extract filter contexts (WHERE-like conditions)
                                # Look for comparisons in if statements or filters
                                for child in ast.walk(node):
                                    if isinstance(child, ast.Compare):
                                        # Try to extract meaningful comparisons
                                        left = ast.unparse(child.left) if hasattr(ast, 'unparse') else str(child.left)
                                        ops = [ast.unparse(op) if hasattr(ast, 'unparse') else str(op) for op in child.comparators]
                                        if left and ops:
                                            result['filter_context'].append(f"{left} {ops[0]}")
                                
                                break
                except SyntaxError:
                    # Fallback to regex if AST parsing fails
                    pass
                
                # Regex fallback for docstring
                if not result['docstring']:
                    docstring_match = re.search(
                        rf'def\s+{re.escape(func_pattern)}[^:]*:\s*"""(.*?)"""',
                        content,
                        re.DOTALL
                    )
                    if docstring_match:
                        result['docstring'] = docstring_match.group(1).strip()
                
                # Regex for load_table calls
                load_table_matches = re.findall(r"load_table\(['\"]([^'\"]+)['\"]\)", content)
                result['data_sources'].extend(load_table_matches)
                
                if result['source_module']:
                    break
        except Exception as e:
            # Skip files that can't be read
            continue
    
    return result if result['source_module'] else None


def extract_formula_from_code(column_name: str, src_dir: Path) -> Optional[str]:
    """
    Try to find formula/calculation for a column in the code.
    Looks for assignments like: stats['column_name'] = ...
    """
    # This is a simplified version - could be enhanced with AST parsing
    return None  # Placeholder for now


def enhance_table_metadata(table_name: str, src_dir: Path) -> Dict:
    """
    Enhance table metadata by extracting from code.
    """
    # Start with existing metadata
    meta = TABLE_METADATA.get(table_name, {}).copy()
    
    # Try to find creation function
    func_info = find_table_creation_function(table_name, src_dir)
    
    if func_info:
        # Update source module if found
        if not meta.get('source_module') or meta.get('source_module') == 'Unknown':
            meta['source_module'] = func_info['source_module']
        
        # Add docstring info to description if available
        if func_info['docstring'] and not meta.get('description'):
            # Extract first line of docstring as description
            first_line = func_info['docstring'].split('\n')[0].strip()
            if first_line:
                meta['description'] = first_line
        
        # Add data sources
        if func_info['data_sources']:
            meta['data_sources'] = func_info['data_sources']
            if not meta.get('logic'):
                meta['logic'] = f"Built from: {', '.join(func_info['data_sources'])}"
        
        # Add filter context
        if func_info['filter_context']:
            meta['filter_context'] = func_info['filter_context']
    
    return meta


# =============================================================================
# ENHANCED GENERATOR
# =============================================================================

def generate_enhanced_table_doc(table_name: str, df: pd.DataFrame, src_dir: Path) -> str:
    """Generate enhanced markdown documentation for a table."""
    meta = enhance_table_metadata(table_name, src_dir)
    
    doc = f"""
## {table_name}

| Property | Value |
|----------|-------|
| **Description** | {meta.get('description', 'No description')} |
| **Purpose** | {meta.get('purpose', '-')} |
| **Source Module** | `{meta.get('source_module', 'Unknown')}` |
| **Logic** | {meta.get('logic', '-')} |
| **Grain** | {meta.get('grain', '-')} |
| **Rows** | {len(df):,} |
| **Columns** | {len(df.columns)} |
"""
    
    # Add data sources if available
    if meta.get('data_sources'):
        doc += f"| **Data Sources** | {', '.join(meta['data_sources'])} |\n"
    
    # Add filter context if available
    if meta.get('filter_context'):
        doc += f"| **Filter Context** | {'; '.join(meta['filter_context'][:5])} |\n"  # Limit to 5
    
    doc += """
### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
"""
    
    # Import analyze_column from original script
    from generate_data_dictionary import analyze_column
    
    for col in df.columns:
        col_info = analyze_column(df[col], col)
        doc += f"| {col_info['column']} | {col_info['data_type']} | {col_info['description']} | {col_info['context_mapping']} | {col_info['calculation_formula']} | {col_info['column_type']} | {col_info['non_null']:,} | {col_info['null_pct']}% | {col_info['validated']} |\n"
    
    doc += "\n---\n"
    return doc


def main():
    """Generate enhanced documentation."""
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / 'data' / 'output'
    docs_dir = base_dir / 'docs'
    src_dir = base_dir / 'src'
    
    print("=" * 60)
    print("GENERATING ENHANCED DATA DICTIONARY")
    print("=" * 60)
    print("Extracting metadata from source code...")
    
    # Generate enhanced data dictionary
    full_doc = f"""# BenchSight Data Dictionary (Full - Enhanced)

**Auto-generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Tables:** 139
**Version:** 29.0
**Enhanced:** Extracts metadata from source code

---

## Quick Links

### Core Tables
- [fact_events](#fact_events)
- [fact_gameroster](#fact_gameroster)
- [fact_player_game_stats](#fact_player_game_stats)
- [fact_goalie_game_stats](#fact_goalie_game_stats)
- [dim_player](#dim_player)
- [dim_team](#dim_team)
- [dim_game](#dim_game)

---

## Column Type Legend

| Type | Meaning | Example |
|------|---------|---------|
| **Explicit** | Direct from raw/source data | event_type, period |
| **Calculated** | Formula-based derivation | points = goals + assists |
| **Derived** | Generated keys/aggregates | player_game_key |
| **FK** | Foreign key lookup | player_id → dim_player |
| **Unknown** | Needs investigation | - |

---

## Critical Business Rules

### Goal Counting (CANONICAL)
```sql
-- THE ONLY WAY TO COUNT GOALS:
WHERE event_type = 'Goal' AND event_detail = 'Goal_Scored'

-- Shot_Goal is the SHOT, not the goal!
```

### Player Attribution
```
event_player_1 = Primary player (scorer, shooter)
event_player_2 = Primary assist / secondary player
event_player_3 = Secondary assist
```

---

## Metadata Extraction Notes

This dictionary is enhanced by extracting metadata from:
- Function docstrings
- Table creation functions (create_fact_*, create_dim_*)
- Data source dependencies (load_table calls)
- Filter contexts (WHERE-like conditions)

For complete module documentation, see [SRC_MODULES_GUIDE.md](SRC_MODULES_GUIDE.md)

---

"""
    
    # Process each table
    tables_processed = 0
    for csv_file in sorted(data_dir.glob('*.csv')):
        table_name = csv_file.stem
        try:
            df = pd.read_csv(csv_file, low_memory=False)
            full_doc += generate_enhanced_table_doc(table_name, df, src_dir)
            tables_processed += 1
            print(f"  ✓ {table_name}: {len(df):,} rows, {len(df.columns)} cols")
        except Exception as e:
            print(f"  ✗ {table_name}: Error - {e}")
    
    # Write markdown
    output_file = docs_dir / 'DATA_DICTIONARY_FULL.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_doc)
    print(f"\n✓ Generated {output_file} ({tables_processed} tables)")
    
    # Generate validation tracker (reuse from original)
    print("\nGenerating validation tracker...")
    from generate_data_dictionary import generate_validation_tracker
    tracker_df = generate_validation_tracker(data_dir)
    tracker_df.to_csv(docs_dir / 'validation_tracker.csv', index=False)
    print(f"✓ Generated validation_tracker.csv ({len(tracker_df)} columns)")
    
    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print(f"\nEnhanced dictionary includes:")
    print(f"  - Source module extraction from code")
    print(f"  - Data source dependencies")
    print(f"  - Filter context information")
    print(f"\nFor module details, see: docs/SRC_MODULES_GUIDE.md")


if __name__ == '__main__':
    main()
