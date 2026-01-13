#!/usr/bin/env python3
"""
Archive Documentation Script

Automatically identifies and archives temporary/old documentation files to docs/archive/

Usage:
    python scripts/archive_docs.py              # Dry run (preview only)
    python scripts/archive_docs.py --execute    # Actually archive files
    python scripts/archive_docs.py --auto       # Auto-archive without prompts
"""

import shutil
from pathlib import Path
from datetime import datetime
import argparse
import sys

# Patterns for files that should be archived
ARCHIVE_PATTERNS = [
    # Versioned handoff files (keep only latest)
    'AGENT_HANDOFF_V*.md',
    # Temporary handoff files
    'QUICK_START_NEXT_AGENT.md',
    'NEXT_STEPS.md',
    'NEXT_PROMPT.md',
    # Old refactoring summaries (if newer versions exist)
    'REFACTORING_SUMMARY.md',
    'REFACTORING_COMPLETE.md',
    'FORMULA_SYSTEM_SUMMARY.md',
    # Old handoff files (if newer versioned ones exist)
    'AGENT_HANDOFF.md',  # Only if versioned ones exist
]

# Files to always keep in root (never archive)
KEEP_IN_ROOT = [
    'README.md',
    'VERSION.txt',
    'requirements.txt',
]

def find_files_to_archive(base_dir: Path) -> list[Path]:
    """Find files that should be archived."""
    files_to_archive = []
    
    # Check for versioned handoff files
    versioned_handoffs = sorted(base_dir.glob('AGENT_HANDOFF_V*.md'))
    if len(versioned_handoffs) > 1:
        # Keep only the latest version
        latest = versioned_handoffs[-1]
        for f in versioned_handoffs[:-1]:
            files_to_archive.append(f)
        # Also archive non-versioned AGENT_HANDOFF.md if it exists
        non_versioned = base_dir / 'AGENT_HANDOFF.md'
        if non_versioned.exists() and non_versioned not in files_to_archive:
            files_to_archive.append(non_versioned)
    
    # Check other patterns
    for pattern in ARCHIVE_PATTERNS:
        if pattern.startswith('AGENT_HANDOFF'):
            continue  # Already handled above
        
        matches = list(base_dir.glob(pattern))
        for match in matches:
            if match.name not in KEEP_IN_ROOT:
                files_to_archive.append(match)
    
    # Remove duplicates and sort
    files_to_archive = sorted(set(files_to_archive))
    return files_to_archive


def archive_file(file_path: Path, archive_dir: Path, dry_run: bool = True) -> bool:
    """Archive a single file."""
    if not file_path.exists():
        return False
    
    archive_path = archive_dir / file_path.name
    
    # Handle conflicts (if file already exists in archive)
    if archive_path.exists():
        # Add timestamp suffix
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        stem = file_path.stem
        suffix = file_path.suffix
        archive_path = archive_dir / f"{stem}_{timestamp}{suffix}"
    
    if dry_run:
        print(f"  [DRY RUN] Would archive: {file_path.name}")
        print(f"            → {archive_path.relative_to(file_path.parent.parent)}")
        return True
    else:
        try:
            shutil.move(str(file_path), str(archive_path))
            print(f"  ✓ Archived: {file_path.name}")
            return True
        except Exception as e:
            print(f"  ✗ Error archiving {file_path.name}: {e}")
            return False


def update_archive_readme(archive_dir: Path, archived_files: list[Path], dry_run: bool = True):
    """Update docs/archive/README.md with newly archived files."""
    readme_path = archive_dir / 'README.md'
    
    if not readme_path.exists():
        # Create initial README
        content = f"""# Archived Documentation

This folder contains temporary handoff documents and summaries that were created during development sessions but are no longer actively maintained.

## Contents

### Recently Archived
"""
    else:
        content = readme_path.read_text()
    
    # Add new entries
    if archived_files:
        today = datetime.now().strftime('%Y-%m-%d')
        content += f"\n### Archived {today}\n"
        for f in archived_files:
            content += f"- **{f.name}** - Archived {today}\n"
    
    content += f"""
## Why Archived?

These files were created for specific development sessions or as temporary summaries. The information they contain has been:
- Consolidated into main documentation files (e.g., `docs/REFACTORING.md`, `docs/HANDOFF.md`)
- Superseded by more comprehensive guides
- No longer actively referenced

## Current Documentation

For up-to-date information, see:
- **Main docs:** `docs/README.md` - Complete documentation index
- **Refactoring:** `docs/REFACTORING.md` - Current refactoring guide
- **Handoff:** `docs/HANDOFF.md` - Current handoff document
- **Supabase:** `docs/SUPABASE_RESET_GAMEPLAN.md` - Comprehensive Supabase guide

---

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    if dry_run:
        print(f"\n  [DRY RUN] Would update: {readme_path.relative_to(archive_dir.parent)}")
    else:
        readme_path.write_text(content)
        print(f"\n✓ Updated {readme_path.relative_to(archive_dir.parent)}")


def main():
    parser = argparse.ArgumentParser(description='Archive old documentation files')
    parser.add_argument('--execute', action='store_true', 
                       help='Actually archive files (default is dry run)')
    parser.add_argument('--auto', action='store_true',
                       help='Auto-archive without prompts (implies --execute)')
    args = parser.parse_args()
    
    base_dir = Path(__file__).parent.parent
    archive_dir = base_dir / 'docs' / 'archive'
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    dry_run = not (args.execute or args.auto)
    
    print("=" * 60)
    print("DOCUMENTATION ARCHIVE SCRIPT")
    print("=" * 60)
    print(f"\nBase directory: {base_dir}")
    print(f"Archive directory: {archive_dir}")
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print()
    
    # Find files to archive
    files_to_archive = find_files_to_archive(base_dir)
    
    if not files_to_archive:
        print("✓ No files found to archive")
        return 0
    
    print(f"Found {len(files_to_archive)} file(s) to archive:\n")
    for f in files_to_archive:
        print(f"  • {f.name}")
    
    # Confirm if not auto mode
    if not args.auto and not dry_run:
        print("\n" + "=" * 60)
        response = input("Archive these files? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Cancelled.")
            return 0
    
    # Archive files
    print("\nArchiving files...")
    archived = []
    for file_path in files_to_archive:
        if archive_file(file_path, archive_dir, dry_run=dry_run):
            archived.append(file_path)
    
    # Update README
    if archived:
        update_archive_readme(archive_dir, archived, dry_run=dry_run)
    
    print("\n" + "=" * 60)
    if dry_run:
        print("DRY RUN COMPLETE")
        print("Run with --execute to actually archive files")
    else:
        print(f"✓ ARCHIVE COMPLETE ({len(archived)} files)")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
