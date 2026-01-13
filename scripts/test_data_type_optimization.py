#!/usr/bin/env python3
"""
Data Type Optimization Test Script

Tests and measures the impact of data type optimization on ETL output tables.
Analyzes existing tables, shows optimization opportunities, and measures memory savings.

Usage:
    python scripts/test_data_type_optimization.py              # Analyze all tables
    python scripts/test_data_type_optimization.py --optimize   # Re-optimize all tables
    python scripts/test_data_type_optimization.py --table fact_events  # Analyze specific table
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from src.utils.data_type_optimizer import (
    optimize_dataframe_dtypes,
    get_optimization_suggestions,
    calculate_memory_savings
)

OUTPUT_DIR = PROJECT_ROOT / 'data' / 'output'
RESULTS_FILE = PROJECT_ROOT / 'data' / '.dtype_optimization_results.json'


def analyze_table(table_path: Path) -> Dict:
    """Analyze a single table for optimization opportunities."""
    table_name = table_path.stem
    
    try:
        # Load table
        df = pd.read_csv(table_path, low_memory=False)
        
        if len(df) == 0:
            return {
                'table_name': table_name,
                'status': 'empty',
                'rows': 0
            }
        
        # Get current memory usage
        original_memory = df.memory_usage(deep=True).sum()
        
        # Get optimization suggestions
        suggestions = get_optimization_suggestions(df)
        
        # Apply optimization
        df_optimized = optimize_dataframe_dtypes(df.copy())
        
        # Calculate savings
        savings = calculate_memory_savings(df, df_optimized)
        
        # Count optimizations
        optimization_count = len(suggestions)
        
        return {
            'table_name': table_name,
            'status': 'success',
            'rows': len(df),
            'columns': len(df.columns),
            'original_memory_mb': savings['original_memory_mb'],
            'optimized_memory_mb': savings['optimized_memory_mb'],
            'savings_mb': savings['savings_mb'],
            'savings_pct': savings['savings_pct'],
            'optimization_count': optimization_count,
            'suggestions': suggestions
        }
        
    except Exception as e:
        return {
            'table_name': table_name,
            'status': 'error',
            'error': str(e)
        }


def analyze_all_tables(optimize: bool = False) -> Dict:
    """Analyze all tables in output directory."""
    results = {
        'timestamp': datetime.now().isoformat(),
        'tables_analyzed': 0,
        'tables_optimized': 0,
        'tables_empty': 0,
        'tables_errors': 0,
        'total_original_memory_mb': 0,
        'total_optimized_memory_mb': 0,
        'total_savings_mb': 0,
        'table_results': []
    }
    
    csv_files = sorted(OUTPUT_DIR.glob('*.csv'))
    results['tables_analyzed'] = len(csv_files)
    
    print("=" * 80)
    print("DATA TYPE OPTIMIZATION ANALYSIS")
    print("=" * 80)
    print(f"Analyzing {len(csv_files)} tables...")
    print()
    
    for csv_path in csv_files:
        table_name = csv_path.stem
        print(f"  Analyzing {table_name}...", end=' ', flush=True)
        
        result = analyze_table(csv_path)
        results['table_results'].append(result)
        
        if result['status'] == 'success':
            results['total_original_memory_mb'] += result['original_memory_mb']
            results['total_optimized_memory_mb'] += result['optimized_memory_mb']
            results['total_savings_mb'] += result['savings_mb']
            
            if optimize:
                # Re-optimize and save
                try:
                    df = pd.read_csv(csv_path, low_memory=False)
                    df_optimized = optimize_dataframe_dtypes(df)
                    df_optimized.to_csv(csv_path, index=False)
                    results['tables_optimized'] += 1
                    print(f"✅ Optimized ({result['savings_pct']:.1f}% savings)")
                except Exception as e:
                    print(f"❌ Error optimizing: {e}")
            else:
                print(f"✅ {result['savings_pct']:.1f}% savings possible")
                
        elif result['status'] == 'empty':
            results['tables_empty'] += 1
            print("⏭️  Empty")
        else:
            results['tables_errors'] += 1
            print(f"❌ Error: {result.get('error', 'Unknown')}")
    
    # Calculate overall savings percentage
    if results['total_original_memory_mb'] > 0:
        results['total_savings_pct'] = (
            results['total_savings_mb'] / results['total_original_memory_mb'] * 100
        )
    else:
        results['total_savings_pct'] = 0
    
    return results


def print_summary(results: Dict):
    """Print analysis summary."""
    print()
    print("=" * 80)
    print("OPTIMIZATION SUMMARY")
    print("=" * 80)
    print(f"Tables Analyzed:     {results['tables_analyzed']}")
    print(f"Tables Optimized:    {results['tables_optimized']}")
    print(f"Empty Tables:        {results['tables_empty']}")
    print(f"Errors:              {results['tables_errors']}")
    print()
    print("Memory Usage:")
    print(f"  Original:          {results['total_original_memory_mb']:.2f} MB")
    print(f"  Optimized:         {results['total_optimized_memory_mb']:.2f} MB")
    print(f"  Savings:           {results['total_savings_mb']:.2f} MB")
    print(f"  Savings %:         {results['total_savings_pct']:.1f}%")
    print()
    
    # Top tables by savings
    successful = [r for r in results['table_results'] if r['status'] == 'success']
    if successful:
        top_tables = sorted(
            successful,
            key=lambda x: x['savings_mb'],
            reverse=True
        )[:10]
        
        print("Top 10 Tables by Memory Savings:")
        print("-" * 80)
        print(f"{'Table':<30} {'Original MB':<15} {'Savings MB':<15} {'Savings %':<10}")
        print("-" * 80)
        for r in top_tables:
            print(f"{r['table_name']:<30} {r['original_memory_mb']:>12.2f} MB "
                  f"{r['savings_mb']:>12.2f} MB {r['savings_pct']:>8.1f}%")
        print("=" * 80)


def analyze_single_table(table_name: str):
    """Analyze a single table in detail."""
    table_path = OUTPUT_DIR / f"{table_name}.csv"
    
    if not table_path.exists():
        print(f"❌ Table not found: {table_path}")
        return
    
    print("=" * 80)
    print(f"DETAILED ANALYSIS: {table_name}")
    print("=" * 80)
    
    result = analyze_table(table_path)
    
    if result['status'] != 'success':
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        return
    
    print(f"Rows:                {result['rows']:,}")
    print(f"Columns:             {result['columns']}")
    print(f"Original Memory:     {result['original_memory_mb']:.2f} MB")
    print(f"Optimized Memory:    {result['optimized_memory_mb']:.2f} MB")
    print(f"Savings:             {result['savings_mb']:.2f} MB ({result['savings_pct']:.1f}%)")
    print()
    
    if result['suggestions']:
        print("Optimization Opportunities:")
        print("-" * 80)
        for col, suggestion in result['suggestions'].items():
            print(f"\nColumn: {col}")
            print(f"  Current Type:     {suggestion['current_type']}")
            print(f"  Unique Values:    {suggestion['unique_count']}")
            print(f"  Null Values:      {suggestion['null_count']}")
            print(f"  Optimizations:")
            for opt in suggestion['optimizations']:
                print(f"    - {opt['type']}: {opt['reason']}")
                print(f"      Estimated Savings: {opt['estimated_savings']}")
    else:
        print("No optimization opportunities found.")
    
    print("=" * 80)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Test and measure data type optimization impact',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--optimize', action='store_true',
                        help='Re-optimize all tables (saves optimized versions)')
    parser.add_argument('--table', type=str,
                        help='Analyze a specific table (e.g., fact_events)')
    parser.add_argument('--save', action='store_true',
                        help='Save results to JSON file')
    
    args = parser.parse_args()
    
    # Analyze single table if specified
    if args.table:
        analyze_single_table(args.table)
    else:
        # Analyze all tables
        results = analyze_all_tables(optimize=args.optimize)
        print_summary(results)
        
        # Save results if requested
        if args.save:
            RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
            # Convert numpy types to native Python types for JSON serialization
            def convert_to_native(obj):
                if isinstance(obj, dict):
                    return {k: convert_to_native(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_to_native(item) for item in obj]
                elif isinstance(obj, (pd.np.integer, pd.np.int64, pd.np.int32)):
                    return int(obj)
                elif isinstance(obj, (pd.np.floating, pd.np.float64, pd.np.float32)):
                    return float(obj)
                elif pd.isna(obj):
                    return None
                else:
                    return obj
            
            results_serializable = convert_to_native(results)
            with open(RESULTS_FILE, 'w') as f:
                json.dump(results_serializable, f, indent=2)
            print(f"\n✅ Results saved to {RESULTS_FILE}")
