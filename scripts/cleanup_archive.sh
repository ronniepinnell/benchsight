#!/bin/bash
# =============================================================================
# BenchSight Archive Cleanup Script
# =============================================================================
# Run this to delete 52 obsolete files from docs/archive
# Generated: 2026-01-21
#
# Usage: ./scripts/cleanup_archive.sh
# =============================================================================

set -e
cd "$(dirname "$0")/.."

echo "=== BenchSight Archive Cleanup ==="
echo "This will delete 52 obsolete files from docs/archive"
echo ""

# Count files before
BEFORE=$(ls docs/archive/*.md 2>/dev/null | wc -l | tr -d ' ')
echo "Files in archive before cleanup: $BEFORE"
echo ""

# Agent Handoff Documents (16 files)
echo "Deleting agent handoff documents..."
rm -f docs/archive/AGENT_HANDOFF.md
rm -f docs/archive/AGENT_HANDOFF_V29.2.md
rm -f docs/archive/AGENT_HANDOFF_V29.3.md
rm -f docs/archive/AGENT_HANDOFF_V29.4.md
rm -f docs/archive/AGENT_HANDOFF_V29.5.md
rm -f docs/archive/AGENT_HANDOFF_V29.6.md
rm -f docs/archive/AGENT_HANDOFF_V29.7.md
rm -f docs/archive/AGENT_HANDOFF_V29.8.md
rm -f docs/archive/AGENT_HANDOFF_20260113_111958.md
rm -f docs/archive/AGENT_HANDOFF_PROMPT.md
rm -f docs/archive/NEXT_AGENT_PROMPT.md
rm -f docs/archive/NEXT_SESSION_PROMPT.md
rm -f docs/archive/NEXT_PROMPT.md
rm -f docs/archive/AGENT_PROMPT_NEXT_SESSION.md
rm -f docs/archive/QUICK_START_NEXT_AGENT.md
rm -f docs/archive/QUICK_START_NEXT_AGENT_20260113_111958.md

# Timestamped Duplicates (4 files)
echo "Deleting timestamped duplicates..."
rm -f docs/archive/NEXT_STEPS_20260113_111958.md
rm -f docs/archive/REFACTORING_SUMMARY_20260113_111958.md
rm -f docs/archive/REFACTORING_COMPLETE_20260113_111958.md
rm -f "docs/archive/README copy.md"

# Refactoring Notes (4 files)
echo "Deleting obsolete refactoring notes..."
rm -f docs/archive/REFACTORING_SUMMARY.md
rm -f docs/archive/REFACTORING_COMPLETE.md
rm -f docs/archive/REFACTORING_V29_SUMMARY.md
rm -f docs/archive/NEXT_STEPS.md

# Tracker Docs - obsolete (10 files)
echo "Deleting obsolete tracker docs..."
rm -f docs/archive/TRACKER_REBUILD_PROGRESS.md
rm -f docs/archive/TRACKER_REBUILD_STATUS.md
rm -f docs/archive/TRACKER_REBUILD_COMPLETE.md
rm -f docs/archive/TRACKER_REBUILD_ANALYSIS.md
rm -f docs/archive/TRACKER_EXTRACTION_SUMMARY.md
rm -f docs/archive/TRACKER_COMPLETE_EXTRACTION.md
rm -f docs/archive/TRACKER_DEPLOYMENT_CHECKLIST.md
rm -f docs/archive/TRACKER_USAGE_AND_DEPLOYMENT.md
rm -f docs/archive/TRACKER_HIGHLIGHT_VIDEO_URLS.md
rm -f docs/archive/TRACKER_DROPDOWN_MAP.md

# Video Tables Docs (8 files)
echo "Deleting video tables docs..."
rm -f docs/archive/VIDEO_DATA_FORMAT_GUIDE.md
rm -f docs/archive/VIDEO_DIMENSION_TABLES_PROPOSAL.md
rm -f docs/archive/VIDEO_TABLES_DEPLOYMENT.md
rm -f docs/archive/VIDEO_TABLES_EXAMPLES.md
rm -f docs/archive/VIDEO_TABLES_IMPLEMENTATION.md
rm -f docs/archive/VIDEO_TABLES_READY.md
rm -f docs/archive/VIDEO_TABLES_VISUAL_GUIDE.md
rm -f docs/archive/VIDEO_TABLES_INTEGRATION_COMPLETE.md

# XY Export Docs (4 files)
echo "Deleting XY export docs..."
rm -f docs/archive/XY_EXPORT_EXAMPLE.md
rm -f docs/archive/XY_EXPORT_EXAMPLE_SUPABASE.md
rm -f docs/archive/XY_EXPORT_PROPOSAL.md
rm -f docs/archive/XY_STANDARDIZATION_FLIP_BUTTON.md

# Environment Docs (6 files)
echo "Deleting environment docs..."
rm -f docs/archive/ENVIRONMENT_MAPPING.md
rm -f docs/archive/ENVIRONMENT_VARIABLES_EXPLAINED.md
rm -f docs/archive/ENVIRONMENT_VARIABLES.md
rm -f docs/archive/BRANCHES_AND_SUPABASE.md
rm -f docs/archive/PRODUCTION_SETUP.md
rm -f docs/archive/PRODUCTION_CHECKLIST.md

# Obsolete workflow/misc docs
echo "Deleting other obsolete docs..."
rm -f docs/archive/TODO.md
rm -f docs/archive/TRACKER_VIDEO_EXPORT_COLUMNS.md
rm -f docs/archive/TRACKER_VIDEO_MANAGEMENT.md

# Count files after
AFTER=$(ls docs/archive/*.md 2>/dev/null | wc -l | tr -d ' ')
DELETED=$((BEFORE - AFTER))

echo ""
echo "=== Cleanup Complete ==="
echo "Files deleted: $DELETED"
echo "Files remaining in archive: $AFTER"
echo ""
echo "Remaining files are historical references that may still be useful."
echo "Run 'ls docs/archive/' to see what remains."
