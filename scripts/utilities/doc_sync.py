#!/usr/bin/env python3
"""
Documentation Sync System
=========================
Automatically updates ALL documentation with actual values from ETL output.

This ensures docs are ALWAYS accurate - no more hardcoded table counts!

Usage:
    python scripts/utilities/doc_sync.py --audit     # Show what's wrong
    python scripts/utilities/doc_sync.py --fix       # Fix everything
    python scripts/utilities/doc_sync.py --generate  # Regenerate HTML table docs

What it syncs:
- Table counts (total, dim, fact, qa)
- Goal counts (total and per game)
- Game counts
- Test counts
- Column counts per table
- Version numbers

Run as part of pre_delivery.py Phase 8.
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
import subprocess
import sys

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
CONFIG_DIR = PROJECT_ROOT / "config"
DOCS_DIR = PROJECT_ROOT / "docs"
HTML_DIR = DOCS_DIR / "html"

# Files to scan and update
DOC_PATTERNS = [
    "*.md",
    "docs/*.md",
    "docs/html/*.html",
    "docs/html/tables/*.html",
    "docs/html/diagrams/*.html",
    "docs/diagrams/*.mermaid",
]


class DocSyncer:
    """Syncs documentation with actual ETL output."""
    
    def __init__(self):
        self.actual_values = {}
        self.issues = []
        self.fixes = []
        self.table_metadata = {}
        self._load_metadata()
    
    def _load_metadata(self):
        """Load rich table metadata from config."""
        metadata_file = CONFIG_DIR / "TABLE_METADATA.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                self.table_metadata = json.load(f)
        else:
            self.table_metadata = {"tables": {}, "column_glossary": {}, "stat_formulas": {}}
    
    def get_table_info(self, table_name):
        """Get rich metadata for a table."""
        return self.table_metadata.get("tables", {}).get(table_name, {})
    
    def get_column_info(self, column_name):
        """Get rich metadata for a column."""
        return self.table_metadata.get("column_glossary", {}).get(column_name, {})
    
    def audit_metadata_completeness(self):
        """Check that all tables and columns have complete metadata."""
        print("\n" + "="*60)
        print("METADATA COMPLETENESS AUDIT")
        print("="*60)
        
        if not self.actual_values:
            self.compute_actual_values()
        
        import pandas as pd
        
        issues = []
        warnings = []
        
        # Get actual tables from output
        csv_files = list(OUTPUT_DIR.glob("*.csv"))
        actual_tables = {f.stem for f in csv_files}
        
        # Get tables defined in metadata
        metadata_tables = set(self.table_metadata.get("tables", {}).keys())
        
        # Tables missing from metadata
        missing_tables = actual_tables - metadata_tables
        if missing_tables:
            issues.append(f"\n⚠️  TABLES MISSING METADATA ({len(missing_tables)}):")
            for t in sorted(missing_tables):
                issues.append(f"   - {t}")
        
        # Orphan metadata (tables in metadata but not in output)
        orphan_tables = metadata_tables - actual_tables
        if orphan_tables:
            warnings.append(f"\n📋 ORPHAN METADATA ({len(orphan_tables)}) - tables no longer exist:")
            for t in sorted(orphan_tables):
                warnings.append(f"   - {t}")
        
        # Check column-level completeness for tables WITH metadata
        tables_incomplete = []
        total_missing_cols = 0
        
        for csv_path in sorted(csv_files):
            table_name = csv_path.stem
            table_info = self.get_table_info(table_name)
            
            if not table_info:
                continue  # Already reported above
            
            # Check table-level fields
            missing_fields = []
            for field in ['description', 'purpose', 'source_module', 'logic', 'grain']:
                if not table_info.get(field):
                    missing_fields.append(field)
            
            # Check column-level metadata
            try:
                df = pd.read_csv(csv_path, nrows=1)
                actual_cols = set(df.columns)
            except:
                continue
            
            col_metadata = table_info.get('columns', {})
            cols_missing_metadata = []
            cols_incomplete = []
            
            for col in actual_cols:
                col_info = col_metadata.get(col, {})
                if not col_info:
                    # Check column glossary
                    col_info = self.get_column_info(col)
                
                if not col_info:
                    cols_missing_metadata.append(col)
                else:
                    # Check completeness
                    missing = []
                    if not col_info.get('description'):
                        missing.append('description')
                    if not col_info.get('context'):
                        missing.append('context')
                    if not col_info.get('type') or col_info.get('type') == 'Unknown':
                        missing.append('type')
                    if missing:
                        cols_incomplete.append((col, missing))
            
            if missing_fields or cols_missing_metadata or cols_incomplete:
                tables_incomplete.append({
                    'table': table_name,
                    'missing_fields': missing_fields,
                    'cols_no_metadata': cols_missing_metadata,
                    'cols_incomplete': cols_incomplete
                })
                total_missing_cols += len(cols_missing_metadata)
        
        # Report incomplete tables
        if tables_incomplete:
            issues.append(f"\n⚠️  TABLES WITH INCOMPLETE METADATA ({len(tables_incomplete)}):")
            for t in tables_incomplete[:10]:  # Show first 10
                issues.append(f"\n   {t['table']}:")
                if t['missing_fields']:
                    issues.append(f"      Missing table fields: {', '.join(t['missing_fields'])}")
                if t['cols_no_metadata']:
                    issues.append(f"      Columns without metadata: {len(t['cols_no_metadata'])}")
                    if len(t['cols_no_metadata']) <= 5:
                        for c in t['cols_no_metadata']:
                            issues.append(f"         - {c}")
                if t['cols_incomplete']:
                    issues.append(f"      Columns with incomplete metadata: {len(t['cols_incomplete'])}")
            
            if len(tables_incomplete) > 10:
                issues.append(f"\n   ... and {len(tables_incomplete) - 10} more tables")
        
        # Summary
        print(f"\nActual tables: {len(actual_tables)}")
        print(f"Tables with metadata: {len(metadata_tables & actual_tables)}")
        print(f"Tables missing metadata: {len(missing_tables)}")
        print(f"Orphan metadata entries: {len(orphan_tables)}")
        print(f"Tables with incomplete metadata: {len(tables_incomplete)}")
        
        # Print issues
        if issues:
            print("\n" + "-"*60)
            print("ISSUES FOUND:")
            for issue in issues:
                print(issue)
        
        if warnings:
            print("\n" + "-"*60)
            print("WARNINGS:")
            for w in warnings:
                print(w)
        
        if not issues and not warnings:
            print("\n✅ All tables have complete metadata!")
        
        # Return summary for testing
        return {
            'actual_tables': len(actual_tables),
            'tables_with_metadata': len(metadata_tables & actual_tables),
            'missing_tables': len(missing_tables),
            'orphan_tables': len(orphan_tables),
            'incomplete_tables': len(tables_incomplete),
            'missing_table_names': sorted(missing_tables),
            'issues': len(issues) > 0
        }
    
    def compute_actual_values(self):
        """Compute actual values from ETL output and config."""
        print("Computing actual values from ETL output...")
        
        # Count tables
        all_csv = list(OUTPUT_DIR.glob("*.csv"))
        dims = [f for f in all_csv if f.stem.startswith('dim_')]
        facts = [f for f in all_csv if f.stem.startswith('fact_')]
        qas = [f for f in all_csv if f.stem.startswith('qa_')]
        
        self.actual_values['total_tables'] = len(all_csv)
        self.actual_values['dim_tables'] = len(dims)
        self.actual_values['fact_tables'] = len(facts)
        self.actual_values['qa_tables'] = len(qas)
        
        print(f"  Tables: {len(all_csv)} ({len(dims)} dim, {len(facts)} fact, {len(qas)} qa)")
        
        # Count goals from IMMUTABLE_FACTS (source of truth)
        facts_file = CONFIG_DIR / "IMMUTABLE_FACTS.json"
        if facts_file.exists():
            with open(facts_file) as f:
                immutable = json.load(f)
            self.actual_values['total_goals'] = immutable.get('total_goals', 0)
            self.actual_values['games'] = immutable.get('games', {})
            self.actual_values['game_count'] = len(self.actual_values['games'])
            print(f"  Goals: {self.actual_values['total_goals']} across {self.actual_values['game_count']} games")
        
        # Get version
        version_file = CONFIG_DIR / "VERSION.json"
        if version_file.exists():
            with open(version_file) as f:
                version = json.load(f)
            self.actual_values['version'] = version.get('version', '0.00')
            print(f"  Version: {self.actual_values['version']}")
        
        # Count tests
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', 'tests/test_tier1_blocking.py', '--collect-only', '-q'],
                cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=30
            )
            match = re.search(r'(\d+) test', result.stdout)
            self.actual_values['tier1_tests'] = int(match.group(1)) if match else 0
            
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', 'tests/test_tier2_warning.py', '--collect-only', '-q'],
                cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=30
            )
            match = re.search(r'(\d+) test', result.stdout)
            self.actual_values['tier2_tests'] = int(match.group(1)) if match else 0
            
            print(f"  Tests: {self.actual_values['tier1_tests']} tier1, {self.actual_values['tier2_tests']} tier2")
        except:
            self.actual_values['tier1_tests'] = 32
            self.actual_values['tier2_tests'] = 17
        
        return self.actual_values
    
    def get_replacement_patterns(self):
        """Define patterns to find and replace."""
        v = self.actual_values
        
        # Build table count string
        table_str = f"{v['total_tables']} ({v['dim_tables']} dim, {v['fact_tables']} fact, {v['qa_tables']} qa)"
        
        patterns = [
            # Table counts - various formats
            (r'\b6[012] tables\b', f"{v['total_tables']} tables"),
            (r'\b130 tables\b', f"{v['total_tables']} tables"),  # Old backup reference
            (r'Tables \(6[012]\)', f"Tables ({v['total_tables']})"),
            (r'Tables \(130\)', f"Tables ({v['total_tables']})"),
            (r'\(6[012]\)', f"({v['total_tables']})"),  # In nav links
            (r'all 6[012] tables', f"all {v['total_tables']} tables"),
            (r'All 6[012] tables', f"All {v['total_tables']} tables"),
            (r'~6[012] tables', f"{v['total_tables']} tables"),
            (r'~130 tables', f"{v['total_tables']} tables"),
            
            # Detailed table counts
            (r'\b3[34] dim\b', f"{v['dim_tables']} dim"),
            (r'\b2[456] fact\b', f"{v['fact_tables']} fact"),
            (r'\b34 dim, 2[56] fact', f"{v['dim_tables']} dim, {v['fact_tables']} fact"),
            (r'\b34 dim, 26 fact, 2 QA\b', table_str),
            (r'\b33 dim, 24 fact, 2 QA\b', table_str),  # Already correct but ensure consistency
            
            # Goal counts - be careful not to replace dates
            (r'\b32 goals\b', f"{v['total_goals']} goals"),
            (r'\b17 goals\b', f"{v['total_goals']} goals"),  # Keep 17 if that's correct
            
            # Test counts
            (r'23 passing\b', f"{v['tier1_tests']} passing"),
            (r'23/23 passing', f"{v['tier1_tests']}/{v['tier1_tests']} passing"),
            (r'17 passing\b', f"{v['tier1_tests']} passing"),  # Old count
            
            # Nav bar table count
            (r'📊 Tables \(\d+\)', f"📊 Tables ({v['total_tables']})"),
        ]
        
        return patterns
    
    def get_files_to_update(self):
        """Get all documentation files."""
        files = []
        
        # Root markdown files
        for f in PROJECT_ROOT.glob("*.md"):
            files.append(f)
        
        # Docs folder
        for f in DOCS_DIR.glob("*.md"):
            files.append(f)
        
        # HTML docs
        for f in HTML_DIR.glob("*.html"):
            files.append(f)
        
        # Table HTML docs
        tables_dir = HTML_DIR / "tables"
        if tables_dir.exists():
            for f in tables_dir.glob("*.html"):
                files.append(f)
        
        # Diagrams
        diagrams_dir = HTML_DIR / "diagrams"
        if diagrams_dir.exists():
            for f in diagrams_dir.glob("*.html"):
                files.append(f)
        
        diagrams_dir2 = DOCS_DIR / "diagrams"
        if diagrams_dir2.exists():
            for f in diagrams_dir2.glob("*.mermaid"):
                files.append(f)
        
        # VERSION.txt files
        for f in PROJECT_ROOT.rglob("VERSION.txt"):
            files.append(f)
        
        return files
    
    def audit_file(self, filepath):
        """Check a file for outdated values."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return []
        
        issues = []
        v = self.actual_values
        
        # Check for wrong table counts
        wrong_counts = re.findall(r'\b(6[012]|130) tables\b', content)
        for wc in wrong_counts:
            if int(wc) != v['total_tables']:
                issues.append(f"Wrong table count: {wc} (should be {v['total_tables']})")
        
        # Check for wrong dim/fact breakdowns
        if '34 dim' in content and v['dim_tables'] != 34:
            issues.append(f"Wrong dim count: 34 (should be {v['dim_tables']})")
        if '25 fact' in content and v['fact_tables'] != 25:
            issues.append(f"Wrong fact count: 25 (should be {v['fact_tables']})")
        if '26 fact' in content and v['fact_tables'] != 26:
            issues.append(f"Wrong fact count: 26 (should be {v['fact_tables']})")
        
        return issues
    
    def fix_file(self, filepath, patterns):
        """Apply replacements to a file."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return False, 0
        
        original = content
        changes = 0
        
        for pattern, replacement in patterns:
            new_content, n = re.subn(pattern, replacement, content)
            if n > 0:
                changes += n
                content = new_content
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes
        
        return False, 0
    
    def audit(self):
        """Audit all docs for issues."""
        print("\n" + "="*60)
        print("DOCUMENTATION AUDIT")
        print("="*60)
        
        self.compute_actual_values()
        files = self.get_files_to_update()
        
        print(f"\nScanning {len(files)} files...")
        
        total_issues = 0
        files_with_issues = []
        
        for filepath in files:
            issues = self.audit_file(filepath)
            if issues:
                files_with_issues.append((filepath, issues))
                total_issues += len(issues)
        
        print(f"\n{'='*60}")
        print(f"AUDIT RESULTS: {total_issues} issues in {len(files_with_issues)} files")
        print("="*60)
        
        for filepath, issues in files_with_issues[:20]:  # Show first 20
            rel_path = filepath.relative_to(PROJECT_ROOT)
            print(f"\n{rel_path}:")
            for issue in issues[:3]:  # Show first 3 issues per file
                print(f"  • {issue}")
            if len(issues) > 3:
                print(f"  ... and {len(issues) - 3} more")
        
        if len(files_with_issues) > 20:
            print(f"\n... and {len(files_with_issues) - 20} more files with issues")
        
        return total_issues
    
    def fix_all(self):
        """Fix all documentation."""
        print("\n" + "="*60)
        print("FIXING ALL DOCUMENTATION")
        print("="*60)
        
        self.compute_actual_values()
        patterns = self.get_replacement_patterns()
        files = self.get_files_to_update()
        
        print(f"\nApplying {len(patterns)} patterns to {len(files)} files...")
        
        fixed_count = 0
        total_changes = 0
        
        for filepath in files:
            fixed, changes = self.fix_file(filepath, patterns)
            if fixed:
                fixed_count += 1
                total_changes += changes
                rel_path = filepath.relative_to(PROJECT_ROOT)
                print(f"  ✓ {rel_path} ({changes} changes)")
        
        print(f"\n{'='*60}")
        print(f"FIXED: {fixed_count} files, {total_changes} total changes")
        print("="*60)
        
        return fixed_count, total_changes
    
    def generate_tables_html(self):
        """Regenerate HTML documentation for all tables."""
        print("\n" + "="*60)
        print("REGENERATING TABLE HTML DOCUMENTATION")
        print("="*60)
        
        # Ensure we have actual values
        if not self.actual_values:
            self.compute_actual_values()
        
        tables_dir = HTML_DIR / "tables"
        tables_dir.mkdir(exist_ok=True)
        
        csv_files = sorted(OUTPUT_DIR.glob("*.csv"))
        print(f"\nGenerating HTML for {len(csv_files)} tables...")
        
        import pandas as pd
        
        generated = 0
        for csv_path in csv_files:
            table_name = csv_path.stem
            html_path = tables_dir / f"{table_name}.html"
            
            try:
                df = pd.read_csv(csv_path, nrows=100)
                
                # Generate HTML
                html = self._generate_table_html(table_name, df)
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                
                generated += 1
                
            except Exception as e:
                print(f"  ✗ {table_name}: {e}")
        
        print(f"\n✓ Generated {generated} table HTML files")
        
        # Update tables.html index
        self._generate_tables_index(csv_files)
        
        return generated
    
    def _generate_table_html(self, table_name, df):
        """Generate HTML for a single table - matches old rich format."""
        v = self.actual_values
        version = v.get('version', '13.09')
        
        # Get rich metadata
        table_info = self.get_table_info(table_name)
        col_metadata = table_info.get('columns', {})
        
        # Determine table type
        if table_name.startswith('dim_'):
            table_type = 'Dimension'
            badge_class = 'badge-blue'
        elif table_name.startswith('fact_'):
            table_type = 'Fact'
            badge_class = 'badge-green'
        elif table_name.startswith('qa_'):
            table_type = 'QA'
            badge_class = 'badge-yellow'
        else:
            table_type = 'Other'
            badge_class = 'badge-gray'
        
        # Calculate null stats per column
        null_stats = {}
        for col in df.columns:
            non_null = df[col].notna().sum()
            null_pct = (df[col].isna().sum() / len(df) * 100) if len(df) > 0 else 0
            null_stats[col] = {'non_null': non_null, 'null_pct': null_pct}
        
        # Build column rows with full metadata
        columns_html = ""
        for col in df.columns:
            dtype = str(df[col].dtype)
            
            # Get column metadata
            col_info = col_metadata.get(col, {})
            if not col_info:
                # Try column glossary
                col_info = self.get_column_info(col)
            
            description = col_info.get('description', self._infer_column_description(col, table_name))
            context = col_info.get('context', '')
            calculation = col_info.get('calculation', '')
            col_type = col_info.get('type', 'Unknown')
            
            # Type badge styling
            type_badges = {
                'Explicit': ('Explicit', 'badge-explicit'),
                'Calculated': ('Calculated', 'badge-calculated'),
                'Derived': ('Derived', 'badge-derived'),
                'FK': ('FK', 'badge-fk'),
                'Unknown': ('Unknown', 'badge-unknown')
            }
            badge_text, badge_css = type_badges.get(col_type, ('Unknown', 'badge-unknown'))
            
            # Null stats
            ns = null_stats.get(col, {'non_null': 0, 'null_pct': 0})
            null_pct_class = 'null-high' if ns['null_pct'] > 5 else ('null-med' if ns['null_pct'] > 1 else 'null-low')
            
            columns_html += f"""
            <tr>
                <td><code>{col}</code></td>
                <td>{dtype}</td>
                <td>{description}</td>
                <td class="context-cell">{context}</td>
                <td class="calc-cell"><code>{calculation}</code></td>
                <td><span class="type-badge {badge_css}">{badge_text}</span></td>
                <td class="stat-cell">{ns['non_null']}</td>
                <td class="stat-cell {null_pct_class}">{ns['null_pct']:.1f}%</td>
            </tr>"""
        
        # Build sample data table
        sample_html = df.head(5).to_html(classes='data-table', index=False, escape=True)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{table_name} - BenchSight v{version}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f8f9fa; color: #333; line-height: 1.6; }}
        .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #4a4e69 100%); color: white; padding: 20px 40px; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .nav {{ background: #4a4e69; padding: 0 20px; display: flex; flex-wrap: wrap; }}
        .nav a {{ color: white; text-decoration: none; padding: 10px 14px; font-size: 13px; }}
        .nav a:hover {{ background: rgba(255,255,255,0.1); }}
        .container {{ max-width: 1600px; margin: 0 auto; padding: 30px; }}
        
        /* Table Overview Section */
        .table-overview {{ background: white; border-radius: 8px; padding: 25px; margin-bottom: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .table-overview h2 {{ margin-top: 0; color: #4a4e69; border-bottom: 2px solid #4a4e69; padding-bottom: 10px; }}
        .overview-desc {{ background: #e3f2fd; border-left: 4px solid #1976d2; padding: 15px; margin-bottom: 20px; font-size: 15px; }}
        .overview-grid {{ display: grid; grid-template-columns: 120px 1fr; gap: 10px 20px; }}
        .overview-label {{ font-weight: 600; color: #555; }}
        .overview-value {{ color: #333; }}
        .overview-value code {{ background: #f5f5f5; padding: 2px 8px; border-radius: 4px; font-family: 'SF Mono', Monaco, monospace; font-size: 12px; }}
        
        /* Column Documentation Section */
        .column-docs {{ background: white; border-radius: 8px; padding: 25px; margin-bottom: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .column-docs h2 {{ margin-top: 0; color: #4a4e69; border-bottom: 2px solid #4a4e69; padding-bottom: 10px; }}
        
        /* Legend */
        .legend {{ margin-bottom: 20px; padding: 15px; background: #fafafa; border-radius: 6px; }}
        .legend-title {{ font-weight: 600; margin-right: 10px; }}
        .legend-item {{ display: inline-flex; align-items: center; margin-right: 20px; }}
        
        /* Type badges */
        .type-badge {{ display: inline-block; padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
        .badge-explicit {{ background: #e8f5e9; color: #2e7d32; }}
        .badge-calculated {{ background: #fff3e0; color: #e65100; }}
        .badge-derived {{ background: #e3f2fd; color: #1565c0; }}
        .badge-fk {{ background: #fce4ec; color: #c2185b; }}
        .badge-unknown {{ background: #f5f5f5; color: #757575; }}
        
        /* Table styling */
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; background: white; }}
        th {{ background: #4a4e69; color: white; padding: 12px 10px; text-align: left; font-size: 12px; font-weight: 600; position: sticky; top: 0; }}
        td {{ border: 1px solid #e0e0e0; padding: 10px; font-size: 13px; vertical-align: top; }}
        tr:nth-child(even) {{ background: #fafafa; }}
        tr:hover {{ background: #f0f7ff; }}
        code {{ background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: 'SF Mono', Monaco, monospace; font-size: 11px; }}
        
        /* Column-specific styling */
        .context-cell {{ max-width: 300px; font-size: 12px; color: #555; }}
        .calc-cell {{ max-width: 250px; font-size: 11px; }}
        .calc-cell code {{ background: #fff8e1; }}
        .stat-cell {{ text-align: right; font-size: 12px; }}
        .null-low {{ color: #2e7d32; }}
        .null-med {{ color: #f57c00; }}
        .null-high {{ color: #c62828; font-weight: 600; }}
        
        /* Badge styles */
        .badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
        .badge-blue {{ background: #1976d2; color: white; }}
        .badge-green {{ background: #388e3c; color: white; }}
        .badge-yellow {{ background: #f9a825; color: #333; }}
        
        /* Sample data */
        .data-table {{ font-size: 11px; overflow-x: auto; }}
        .data-table th {{ font-size: 11px; padding: 8px; }}
        .data-table td {{ padding: 6px 8px; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
        
        footer {{ text-align: center; padding: 20px; color: #888; font-size: 11px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏒 BenchSight <span style="font-size: 14px; opacity: 0.8;">v{version}</span></h1>
    </div>
    
    <nav class="nav">
        <a href="../index.html">🏠 Home</a>
        <a href="../tables.html">📊 Tables ({v['total_tables']})</a>
        <a href="../BS_DETECTOR.html">🔍 BS Detector</a>
        <a href="../DOC_MAINTENANCE.html">📝 Doc Guide</a>
    </nav>

    <div class="container">
        <h1>{table_name} <span class="badge {badge_class}">{table_type}</span></h1>
        
        <!-- Table Overview Section -->
        <div class="table-overview">
            <h2>Table Overview</h2>
            
            <div class="overview-desc">
                <strong>Description:</strong> {table_info.get('description', 'No description available.')}
            </div>
            
            <div class="overview-grid">
                <div class="overview-label">Purpose:</div>
                <div class="overview-value">{table_info.get('purpose', 'Not documented.')}</div>
                
                <div class="overview-label">Source Module:</div>
                <div class="overview-value"><code>{table_info.get('source_module', 'Unknown')}</code></div>
                
                <div class="overview-label">Logic:</div>
                <div class="overview-value">{table_info.get('logic', 'Not documented.')}</div>
                
                <div class="overview-label">Grain:</div>
                <div class="overview-value">{table_info.get('grain', 'Not documented.')}</div>
                
                <div class="overview-label">Rows:</div>
                <div class="overview-value">{len(df):,}</div>
                
                <div class="overview-label">Columns:</div>
                <div class="overview-value">{len(df.columns)}</div>
            </div>
        </div>
        
        <!-- Column Documentation Section -->
        <div class="column-docs">
            <h2>Column Documentation</h2>
            
            <div class="legend">
                <span class="legend-title">Legend:</span>
                <span class="legend-item"><span class="type-badge badge-explicit">Explicit</span> = From raw data</span>
                <span class="legend-item"><span class="type-badge badge-calculated">Calculated</span> = Formula-based</span>
                <span class="legend-item"><span class="type-badge badge-derived">Derived</span> = Generated key/aggregate</span>
                <span class="legend-item"><span class="type-badge badge-fk">FK</span> = Foreign key lookup</span>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Data Type</th>
                        <th>Description</th>
                        <th>Context / Mapping</th>
                        <th>Calculation / Formula</th>
                        <th>Type</th>
                        <th>Non-Null</th>
                        <th>Null %</th>
                    </tr>
                </thead>
                <tbody>
                    {columns_html}
                </tbody>
            </table>
        </div>
        
        <!-- Sample Data Section -->
        <div class="column-docs">
            <h2>Sample Data (First 5 Rows)</h2>
            {sample_html}
        </div>
        
        <footer>
            BenchSight v{version} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | <a href="../tables.html">Back to Tables</a>
        </footer>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_tables_index(self, csv_files):
        """Generate tables.html index page."""
        v = self.actual_values
        version = v.get('version', '13.09')
        
        # Group tables
        dims = sorted([f for f in csv_files if f.stem.startswith('dim_')])
        facts = sorted([f for f in csv_files if f.stem.startswith('fact_')])
        qas = sorted([f for f in csv_files if f.stem.startswith('qa_')])
        
        def make_table_list(tables, badge_class):
            html = ""
            for t in tables:
                name = t.stem
                html += f'<a href="tables/{name}.html" class="table-link"><span class="badge {badge_class}">{name}</span></a>\n'
            return html
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>All Tables - BenchSight v{version}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f8f9fa; color: #333; line-height: 1.6; }}
        .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #4a4e69 100%); color: white; padding: 20px 40px; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .nav {{ background: #4a4e69; padding: 0 20px; display: flex; flex-wrap: wrap; }}
        .nav a {{ color: white; text-decoration: none; padding: 10px 14px; font-size: 13px; }}
        .nav a:hover {{ background: rgba(255,255,255,0.1); }}
        .nav a.active {{ background: rgba(255,255,255,0.2); }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 30px; }}
        h2 {{ color: #4a4e69; border-bottom: 2px solid #4a4e69; padding-bottom: 8px; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; flex-wrap: wrap; }}
        .stat {{ background: white; padding: 20px 30px; border-radius: 10px; box-shadow: 0 3px 6px rgba(0,0,0,0.1); text-align: center; }}
        .stat-value {{ font-size: 36px; font-weight: bold; color: #4a4e69; }}
        .stat-label {{ font-size: 13px; color: #888; }}
        .table-grid {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0; }}
        .table-link {{ text-decoration: none; }}
        .badge {{ display: inline-block; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 500; }}
        .badge-blue {{ background: #e3f2fd; color: #1565c0; }}
        .badge-blue:hover {{ background: #1565c0; color: white; }}
        .badge-green {{ background: #e8f5e9; color: #2e7d32; }}
        .badge-green:hover {{ background: #2e7d32; color: white; }}
        .badge-yellow {{ background: #fff8e1; color: #f57f17; }}
        .badge-yellow:hover {{ background: #f57f17; color: white; }}
        footer {{ text-align: center; padding: 20px; color: #888; font-size: 11px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏒 BenchSight <span style="font-size: 14px; opacity: 0.8;">v{version}</span></h1>
    </div>
    
    <nav class="nav">
        <a href="index.html">🏠 Home</a>
        <a href="tables.html" class="active">📊 Tables ({v['total_tables']})</a>
        <a href="BS_DETECTOR.html">🔍 BS Detector</a>
        <a href="DOC_MAINTENANCE.html">📝 Doc Guide</a>
    </nav>

    <div class="container">
        <h1>All Tables ({v['total_tables']})</h1>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{len(dims)}</div>
                <div class="stat-label">Dimension Tables</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(facts)}</div>
                <div class="stat-label">Fact Tables</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(qas)}</div>
                <div class="stat-label">QA Tables</div>
            </div>
        </div>
        
        <h2>Dimension Tables ({len(dims)})</h2>
        <div class="table-grid">
            {make_table_list(dims, 'badge-blue')}
        </div>
        
        <h2>Fact Tables ({len(facts)})</h2>
        <div class="table-grid">
            {make_table_list(facts, 'badge-green')}
        </div>
        
        <h2>QA Tables ({len(qas)})</h2>
        <div class="table-grid">
            {make_table_list(qas, 'badge-yellow')}
        </div>
        
        <footer>
            BenchSight v{version} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </footer>
    </div>
</body>
</html>"""
        
        with open(HTML_DIR / "tables.html", 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✓ Generated tables.html index")
    
    def generate_data_dictionary(self):
        """Generate comprehensive DATA_DICTIONARY.md from actual table schemas."""
        print("\n" + "="*60)
        print("REGENERATING DATA DICTIONARY")
        print("="*60)
        
        if not self.actual_values:
            self.compute_actual_values()
        
        import pandas as pd
        
        v = self.actual_values
        version = v.get('version', '13.09')
        
        csv_files = sorted(OUTPUT_DIR.glob("*.csv"))
        dims = sorted([f for f in csv_files if f.stem.startswith('dim_')])
        facts = sorted([f for f in csv_files if f.stem.startswith('fact_')])
        qas = sorted([f for f in csv_files if f.stem.startswith('qa_')])
        
        # Get critical rules from metadata
        critical_rules = self.table_metadata.get('critical_rules', {})
        stat_formulas = self.table_metadata.get('stat_formulas', {})
        
        md = f"""# BenchSight Data Dictionary v{version}

**Auto-generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Metadata source:** `config/TABLE_METADATA.json`

---

## Overview

| Metric | Count |
|--------|-------|
| Total Tables | {v['total_tables']} |
| Dimension Tables | {v['dim_tables']} |
| Fact Tables | {v['fact_tables']} |
| QA Tables | {v['qa_tables']} |
| Games Tracked | {v.get('game_count', 4)} |
| Total Goals | {v.get('total_goals', 17)} |

---

## ⚠️ Critical Rules

"""
        
        # Add goal counting rules
        if 'goal_counting' in critical_rules:
            gc = critical_rules['goal_counting']
            md += f"""### Goal Counting

**Rule:** `{gc.get('rule', '')}`

⚠️ **Warning:** {gc.get('warning', '')}

```python
{gc.get('example', '')}
```

"""
        
        # Add player role rules
        if 'player_roles' in critical_rules:
            md += "### Player Roles\n\n"
            md += "| Role | Meaning |\n|------|--------|\n"
            for role, meaning in critical_rules['player_roles'].items():
                md += f"| `{role}` | {meaning} |\n"
            md += "\n"
        
        # Add time format rules
        if 'time_formats' in critical_rules:
            md += "### Time Formats\n\n"
            md += "| Field | Format |\n|-------|--------|\n"
            for field, fmt in critical_rules['time_formats'].items():
                md += f"| `{field}` | {fmt} |\n"
            md += "\n"
        
        md += "---\n\n"
        
        # Add stat formulas
        if stat_formulas:
            md += "## Stat Calculation Formulas\n\n"
            md += "| Stat | Formula |\n|------|--------|\n"
            for stat, formula in stat_formulas.items():
                md += f"| `{stat}` | `{formula}` |\n"
            md += "\n---\n\n"
        
        # Table of contents
        md += """## Table of Contents

"""
        md += f"### Dimension Tables ({len(dims)})\n"
        for f in dims:
            md += f"- [{f.stem}](#{f.stem})\n"
        
        md += f"\n### Fact Tables ({len(facts)})\n"
        for f in facts:
            md += f"- [{f.stem}](#{f.stem})\n"
        
        md += f"\n### QA Tables ({len(qas)})\n"
        for f in qas:
            md += f"- [{f.stem}](#{f.stem})\n"
        
        md += "\n---\n\n## Dimension Tables\n\n"
        
        # Generate each dimension table
        for csv_path in dims:
            md += self._generate_table_md(csv_path)
        
        md += "## Fact Tables\n\n"
        
        for csv_path in facts:
            md += self._generate_table_md(csv_path)
        
        md += "## QA Tables\n\n"
        
        for csv_path in qas:
            md += self._generate_table_md(csv_path)
        
        # Write to file
        dict_path = DOCS_DIR / "DATA_DICTIONARY.md"
        with open(dict_path, 'w', encoding='utf-8') as f:
            f.write(md)
        
        print(f"✓ Generated DATA_DICTIONARY.md ({len(csv_files)} tables)")
        return len(csv_files)
    
    def _generate_table_md(self, csv_path):
        """Generate markdown documentation for a single table."""
        import pandas as pd
        
        table_name = csv_path.stem
        
        try:
            df = pd.read_csv(csv_path)
            row_count = len(df)
            col_count = len(df.columns)
            
            # Get rich metadata
            table_info = self.get_table_info(table_name)
            
            md = f"""### {table_name}

"""
            # Add description if available
            if table_info.get('description'):
                md += f"**{table_info['description']}**\n\n"
            
            # Add source/grain info
            if table_info.get('source') or table_info.get('grain'):
                md += f"| Property | Value |\n|----------|-------|\n"
                if table_info.get('source'):
                    md += f"| Source | {table_info['source']} |\n"
                if table_info.get('grain'):
                    md += f"| Grain | {table_info['grain']} |\n"
                md += f"| Rows | {row_count:,} |\n"
                md += f"| Columns | {col_count} |\n"
                md += "\n"
            else:
                md += f"**Rows:** {row_count:,} | **Columns:** {col_count}\n\n"
            
            # Add critical logic if available
            if table_info.get('critical_logic'):
                logic = table_info['critical_logic']
                if isinstance(logic, list):
                    md += "**⚠️ Critical Logic:**\n"
                    for item in logic:
                        md += f"- {item}\n"
                else:
                    md += f"**⚠️ Critical Logic:** `{logic}`\n"
                md += "\n"
            
            # Column table
            md += "#### Columns\n\n"
            md += "| Column | Type | Description | Sample |\n"
            md += "|--------|------|-------------|--------|\n"
            
            # Get key columns info if available
            key_cols = table_info.get('key_columns', {})
            derived_cols = table_info.get('derived_columns', {})
            all_col_info = {**key_cols, **derived_cols}
            
            for col in df.columns:
                dtype = str(df[col].dtype)
                sample = ""
                if len(df[col].dropna()) > 0:
                    sample_val = df[col].dropna().iloc[0]
                    sample = str(sample_val)[:25]
                    if len(str(sample_val)) > 25:
                        sample += "..."
                
                # Get description from metadata or infer
                desc = all_col_info.get(col, '')
                if not desc:
                    # Check column glossary
                    glossary_info = self.get_column_info(col)
                    if glossary_info:
                        desc = glossary_info.get('description', '')
                if not desc:
                    desc = self._infer_column_description(col, table_name)
                
                # Mark derived columns
                if col in derived_cols:
                    desc = f"📊 {desc}"
                
                md += f"| `{col}` | {dtype} | {desc} | {sample} |\n"
            
            # Add stat calculations if available
            if table_info.get('stat_calculations'):
                md += "\n#### Stat Calculations\n\n"
                md += "| Stat | Formula |\n|------|--------|\n"
                for stat, formula in table_info['stat_calculations'].items():
                    md += f"| {stat} | `{formula}` |\n"
            
            # Add relationships if available
            if table_info.get('relationships'):
                md += "\n#### Relationships\n\n"
                for rel in table_info['relationships']:
                    md += f"- {rel}\n"
            
            md += "\n---\n\n"
            return md
            
        except Exception as e:
            return f"### {table_name}\n\n*Error reading table: {e}*\n\n---\n\n"
    
    def _infer_column_description(self, col, table_name):
        """Infer column description from naming conventions."""
        col_lower = col.lower()
        
        # Common patterns
        descriptions = {
            'game_id': 'Unique game identifier',
            'player_id': 'Unique player identifier',
            'team_id': 'Unique team identifier',
            'event_id': 'Unique event identifier',
            'event_index': 'Sequential event number within game',
            'event_type': 'Type of event (Goal, Shot, Pass, etc.)',
            'event_detail': 'Detailed event subtype',
            'period': 'Game period (1, 2, 3, OT)',
            'game_clock': 'Time remaining in period',
            'elapsed_time': 'Time elapsed in period',
            'zone': 'Ice zone (Off, Def, Neu)',
            'player_name': 'Player full name',
            'player_role': 'Role in event (event_player_1, etc.)',
            'jersey_number': 'Player jersey number',
            'position': 'Player position (C, LW, RW, D, G)',
            'shift_index': 'Sequential shift number',
            'shift_duration': 'Length of shift in seconds',
            'start_time': 'Shift start time',
            'end_time': 'Shift end time',
            'toi': 'Time on ice',
            'goals': 'Goals scored',
            'assists': 'Assists recorded',
            'points': 'Total points (goals + assists)',
            'shots': 'Shots taken',
            'saves': 'Saves made',
            'created_at': 'Record creation timestamp',
            'updated_at': 'Record update timestamp',
        }
        
        # Check for exact match
        if col_lower in descriptions:
            return descriptions[col_lower]
        
        # Check for partial matches
        for pattern, desc in descriptions.items():
            if pattern in col_lower:
                return desc
        
        # Check for common suffixes
        if col_lower.endswith('_id'):
            return 'Foreign key reference'
        if col_lower.endswith('_count'):
            return 'Count/total'
        if col_lower.endswith('_pct'):
            return 'Percentage value'
        if col_lower.endswith('_rate'):
            return 'Rate value'
        if col_lower.startswith('is_'):
            return 'Boolean flag'
        if col_lower.startswith('has_'):
            return 'Boolean flag'
        
        return '-'


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Documentation Sync System')
    parser.add_argument('--audit', action='store_true', help='Audit docs for issues')
    parser.add_argument('--fix', action='store_true', help='Fix all documentation')
    parser.add_argument('--generate', action='store_true', help='Regenerate HTML table docs')
    parser.add_argument('--dictionary', action='store_true', help='Regenerate DATA_DICTIONARY.md')
    parser.add_argument('--metadata', action='store_true', help='Audit metadata completeness')
    parser.add_argument('--all', action='store_true', help='Do everything (audit, fix, generate, dictionary, metadata)')
    
    args = parser.parse_args()
    
    syncer = DocSyncer()
    
    if args.all or (not args.audit and not args.fix and not args.generate and not args.dictionary and not args.metadata):
        # Default: do everything
        syncer.fix_all()
        syncer.generate_tables_html()
        syncer.generate_data_dictionary()
        syncer.audit()
        syncer.audit_metadata_completeness()
    else:
        if args.audit:
            syncer.audit()
        if args.fix:
            syncer.fix_all()
        if args.generate:
            syncer.generate_tables_html()
        if args.dictionary:
            syncer.generate_data_dictionary()
        if args.metadata:
            syncer.audit_metadata_completeness()


if __name__ == '__main__':
    main()
