#!/usr/bin/env python3
"""
Documentation Registry System
==============================
Tracks all documentable items and ensures nothing slips through undocumented.

Usage:
    python scripts/utilities/doc_registry.py --audit      # Check for undocumented items
    python scripts/utilities/doc_registry.py --discover   # Find new items not in registry
    python scripts/utilities/doc_registry.py --changelog  # Check changelog vs docs
    python scripts/utilities/doc_registry.py --update     # Update registry with discoveries
    python scripts/utilities/doc_registry.py --all        # Do everything

What it tracks:
- Tables (auto-discovered from data/output/*.csv)
- Scripts (auto-discovered from scripts/**/*.py)
- Config files (auto-discovered from config/*.json)
- Supabase files (auto-discovered from supabase/*.py, *.sql)
- Features (from changelog entries)
"""

import json
import re
from pathlib import Path
from datetime import datetime
from glob import glob

PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
REGISTRY_FILE = CONFIG_DIR / "DOC_REGISTRY.json"


class DocRegistry:
    """Manages documentation registry and discovery."""
    
    def __init__(self):
        self.registry = self._load_registry()
        self.discoveries = {
            'new_items': [],
            'removed_items': [],
            'undocumented': [],
            'needs_review': [],
            'changelog_gaps': []
        }
    
    def _load_registry(self):
        """Load existing registry or create default."""
        if REGISTRY_FILE.exists():
            with open(REGISTRY_FILE) as f:
                return json.load(f)
        return {"categories": {}, "items": {}, "changelog_tracking": {}}
    
    def _save_registry(self):
        """Save registry to file."""
        self.registry['_updated'] = datetime.now().strftime('%Y-%m-%d')
        with open(REGISTRY_FILE, 'w') as f:
            json.dump(self.registry, f, indent=2)
        print(f"✓ Registry saved to {REGISTRY_FILE}")
    
    def discover_tables(self):
        """Discover tables from ETL output."""
        output_dir = PROJECT_ROOT / "data" / "output"
        if not output_dir.exists():
            return set()
        
        tables = {f.stem for f in output_dir.glob("*.csv")}
        return tables
    
    def discover_scripts(self):
        """Discover Python scripts."""
        scripts = set()
        
        # Scripts directory
        for f in (PROJECT_ROOT / "scripts").rglob("*.py"):
            rel_path = f.relative_to(PROJECT_ROOT)
            scripts.add(str(rel_path))
        
        # Src directory (main modules)
        for f in (PROJECT_ROOT / "src").rglob("*.py"):
            if f.name != "__init__.py":
                rel_path = f.relative_to(PROJECT_ROOT)
                scripts.add(str(rel_path))
        
        return scripts
    
    def discover_supabase(self):
        """Discover Supabase-related files."""
        supabase_dir = PROJECT_ROOT / "supabase"
        if not supabase_dir.exists():
            return set()
        
        files = set()
        for ext in ['*.py', '*.sql']:
            for f in supabase_dir.glob(ext):
                files.add(f.name)
        
        return files
    
    def discover_config(self):
        """Discover config files."""
        config_dir = PROJECT_ROOT / "config"
        if not config_dir.exists():
            return set()
        
        return {f.name for f in config_dir.glob("*.json")}
    
    def parse_changelog(self):
        """Parse changelog to extract features and versions."""
        changelog_path = PROJECT_ROOT / "CHANGELOG.md"
        if not changelog_path.exists():
            return {}
        
        with open(changelog_path) as f:
            content = f.read()
        
        versions = {}
        current_version = None
        current_content = []
        
        for line in content.split('\n'):
            # Match version headers like "## v13.16 - January 7, 2026"
            version_match = re.match(r'^## (v[\d.]+)', line)
            if version_match:
                if current_version:
                    versions[current_version] = '\n'.join(current_content)
                current_version = version_match.group(1)
                current_content = []
            elif current_version:
                current_content.append(line)
        
        if current_version:
            versions[current_version] = '\n'.join(current_content)
        
        return versions
    
    def extract_features_from_changelog(self, changelog_content):
        """Extract feature names from changelog content."""
        features = []
        
        # Look for headers like "### Feature Name" or "**Feature Name:**"
        header_matches = re.findall(r'^### (.+)$', changelog_content, re.MULTILINE)
        bold_matches = re.findall(r'\*\*([^*]+)\*\*', changelog_content)
        
        for match in header_matches:
            # Clean and normalize
            feature = match.strip().lower().replace(' ', '_').replace('-', '_')
            feature = re.sub(r'[^a-z0-9_]', '', feature)
            if feature and len(feature) > 3:
                features.append(feature)
        
        return features
    
    def audit(self):
        """Audit documentation completeness."""
        print("\n" + "="*60)
        print("DOCUMENTATION REGISTRY AUDIT")
        print("="*60)
        
        items = self.registry.get('items', {})
        
        # Count by status
        stats = {'documented': 0, 'partial': 0, 'missing': 0, 'needs_review': 0}
        
        for category, category_items in items.items():
            print(f"\n📁 {category.upper()}")
            print("-" * 40)
            
            for item_name, item_info in category_items.items():
                status = item_info.get('status', 'missing')
                needs_review = item_info.get('needs_review', False)
                
                if status == 'documented' and not needs_review:
                    icon = "✅"
                    stats['documented'] += 1
                elif status == 'partial':
                    icon = "🔶"
                    stats['partial'] += 1
                elif needs_review:
                    icon = "⚠️"
                    stats['needs_review'] += 1
                else:
                    icon = "❌"
                    stats['missing'] += 1
                
                doc_file = item_info.get('doc_file', '')
                print(f"  {icon} {item_name}: {status}" + (f" → {doc_file}" if doc_file else ""))
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"  ✅ Documented:    {stats['documented']}")
        print(f"  🔶 Partial:       {stats['partial']}")
        print(f"  ⚠️  Needs Review:  {stats['needs_review']}")
        print(f"  ❌ Missing:       {stats['missing']}")
        
        total = sum(stats.values())
        if total > 0:
            pct = (stats['documented'] / total) * 100
            print(f"\n  Documentation coverage: {pct:.1f}%")
        
        return stats
    
    def discover(self):
        """Discover new items not in registry."""
        print("\n" + "="*60)
        print("DISCOVERING NEW ITEMS")
        print("="*60)
        
        items = self.registry.get('items', {})
        
        # Tables
        actual_tables = self.discover_tables()
        registered_tables = set(items.get('tables', {}).keys())
        new_tables = actual_tables - registered_tables
        removed_tables = registered_tables - actual_tables
        
        if new_tables:
            print(f"\n📊 NEW TABLES ({len(new_tables)}):")
            for t in sorted(new_tables):
                print(f"   + {t}")
                self.discoveries['new_items'].append(('tables', t))
        
        if removed_tables:
            print(f"\n🗑️  REMOVED TABLES ({len(removed_tables)}):")
            for t in sorted(removed_tables):
                print(f"   - {t}")
                self.discoveries['removed_items'].append(('tables', t))
        
        # Scripts
        actual_scripts = self.discover_scripts()
        registered_scripts = set(items.get('scripts', {}).keys())
        # Normalize paths for comparison
        actual_script_names = {Path(s).name for s in actual_scripts}
        registered_script_names = {Path(s).name for s in registered_scripts}
        new_scripts = actual_script_names - registered_script_names
        
        if new_scripts:
            print(f"\n📜 NEW SCRIPTS ({len(new_scripts)}):")
            for s in sorted(new_scripts)[:20]:  # Limit display
                print(f"   + {s}")
                self.discoveries['new_items'].append(('scripts', s))
            if len(new_scripts) > 20:
                print(f"   ... and {len(new_scripts) - 20} more")
        
        # Supabase
        actual_supabase = self.discover_supabase()
        registered_supabase = set(items.get('supabase', {}).keys())
        new_supabase = actual_supabase - registered_supabase
        
        if new_supabase:
            print(f"\n🗄️  NEW SUPABASE FILES ({len(new_supabase)}):")
            for s in sorted(new_supabase):
                print(f"   + {s}")
                self.discoveries['new_items'].append(('supabase', s))
        
        # Config
        actual_config = self.discover_config()
        registered_config = set(items.get('config_files', {}).keys())
        new_config = actual_config - registered_config
        
        if new_config:
            print(f"\n⚙️  NEW CONFIG FILES ({len(new_config)}):")
            for c in sorted(new_config):
                print(f"   + {c}")
                self.discoveries['new_items'].append(('config_files', c))
        
        # Summary
        total_new = len(self.discoveries['new_items'])
        total_removed = len(self.discoveries['removed_items'])
        
        print(f"\n{'='*60}")
        print(f"DISCOVERY SUMMARY")
        print(f"{'='*60}")
        print(f"  New items found:     {total_new}")
        print(f"  Removed items found: {total_removed}")
        
        if total_new > 0:
            print(f"\n  ⚠️  Run with --update to add new items to registry")
        
        return self.discoveries
    
    def check_changelog(self):
        """Check that changelog entries have corresponding documentation."""
        print("\n" + "="*60)
        print("CHANGELOG vs DOCUMENTATION CHECK")
        print("="*60)
        
        changelog_versions = self.parse_changelog()
        changelog_tracking = self.registry.get('changelog_tracking', {})
        
        gaps = []
        
        for version, content in changelog_versions.items():
            tracked = changelog_tracking.get(version, {})
            docs_needed = tracked.get('docs_needed', [])
            
            if docs_needed:
                print(f"\n⚠️  {version} - DOCS NEEDED:")
                for doc in docs_needed:
                    print(f"   - {doc}")
                    gaps.append((version, doc))
            
            # Check if version is tracked at all
            if version not in changelog_tracking:
                features = self.extract_features_from_changelog(content)
                if features:
                    print(f"\n❓ {version} - NOT TRACKED (features: {', '.join(features[:5])})")
                    gaps.append((version, "Not tracked in registry"))
        
        if not gaps:
            print("\n✅ All changelog entries have documentation!")
        else:
            print(f"\n{'='*60}")
            print(f"GAPS FOUND: {len(gaps)}")
        
        self.discoveries['changelog_gaps'] = gaps
        return gaps
    
    def update(self):
        """Update registry with discovered items."""
        print("\n" + "="*60)
        print("UPDATING REGISTRY")
        print("="*60)
        
        # Run discovery first
        self.discover()
        
        items = self.registry.setdefault('items', {})
        
        # Add new items
        for category, item_name in self.discoveries['new_items']:
            if category not in items:
                items[category] = {}
            
            if item_name not in items[category]:
                items[category][item_name] = {
                    'status': 'missing',
                    'discovered': datetime.now().strftime('%Y-%m-%d'),
                    'needs_review': True
                }
                print(f"  + Added {category}/{item_name}")
        
        # Mark removed items
        for category, item_name in self.discoveries['removed_items']:
            if category in items and item_name in items[category]:
                items[category][item_name]['status'] = 'removed'
                items[category][item_name]['removed_date'] = datetime.now().strftime('%Y-%m-%d')
                print(f"  - Marked removed: {category}/{item_name}")
        
        self._save_registry()
        
        return len(self.discoveries['new_items']), len(self.discoveries['removed_items'])
    
    def generate_report(self):
        """Generate a documentation status report."""
        print("\n" + "="*60)
        print("DOCUMENTATION STATUS REPORT")
        print("="*60)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        self.audit()
        self.discover()
        self.check_changelog()
        
        # Action items
        print("\n" + "="*60)
        print("ACTION ITEMS")
        print("="*60)
        
        actions = []
        
        if self.discoveries['new_items']:
            actions.append(f"📝 Add documentation for {len(self.discoveries['new_items'])} new items")
        
        if self.discoveries['changelog_gaps']:
            actions.append(f"📋 Address {len(self.discoveries['changelog_gaps'])} changelog documentation gaps")
        
        items = self.registry.get('items', {})
        needs_review_count = sum(
            1 for cat in items.values() 
            for item in cat.values() 
            if item.get('needs_review')
        )
        if needs_review_count:
            actions.append(f"⚠️  Review {needs_review_count} items marked for review")
        
        if actions:
            for i, action in enumerate(actions, 1):
                print(f"  {i}. {action}")
        else:
            print("  ✅ No action items!")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Documentation Registry System')
    parser.add_argument('--audit', action='store_true', help='Audit documentation completeness')
    parser.add_argument('--discover', action='store_true', help='Discover new undocumented items')
    parser.add_argument('--changelog', action='store_true', help='Check changelog vs documentation')
    parser.add_argument('--update', action='store_true', help='Update registry with discoveries')
    parser.add_argument('--report', action='store_true', help='Generate full status report')
    parser.add_argument('--all', action='store_true', help='Do everything')
    
    args = parser.parse_args()
    
    registry = DocRegistry()
    
    if args.all or args.report:
        registry.generate_report()
    else:
        if args.audit:
            registry.audit()
        if args.discover:
            registry.discover()
        if args.changelog:
            registry.check_changelog()
        if args.update:
            registry.update()
        
        # Default: show report if no args
        if not any([args.audit, args.discover, args.changelog, args.update]):
            registry.generate_report()


if __name__ == '__main__':
    main()
