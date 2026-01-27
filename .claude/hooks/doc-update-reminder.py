#!/usr/bin/env python3
"""
doc-update-reminder.py - Remind to update docs when committing code changes.

Triggers on git commit commands and checks if code was changed without
corresponding documentation updates.
"""
import json
import sys
import subprocess


def get_staged_files():
    """Get list of staged files."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return [f for f in result.stdout.strip().split('\n') if f]
    except Exception:
        return []


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    command = data.get("tool_input", {}).get("command", "")

    # Only trigger on git commit commands
    if tool_name != "Bash" or "git commit" not in command:
        sys.exit(0)

    staged_files = get_staged_files()
    if not staged_files:
        sys.exit(0)

    # Check what types of files changed
    code_patterns = ('src/', 'api/', 'ui/dashboard/src/', 'ui/portal/', 'ui/tracker/')
    doc_patterns = ('docs/', '.md')

    code_changed = any(
        any(f.startswith(p) for p in code_patterns)
        for f in staged_files
    )
    docs_changed = any(
        f.startswith('docs/') or f.endswith('.md')
        for f in staged_files
    )

    # Identify specific doc updates that might be needed
    doc_suggestions = []

    # ETL changes
    if any(f.startswith('src/core/') for f in staged_files):
        doc_suggestions.append("- docs/etl/CODE_FLOW_ETL.md (ETL core changes)")
    if any(f.startswith('src/calculations/') for f in staged_files):
        doc_suggestions.append("- docs/etl/calculations.md (calculation changes)")
    if any(f.startswith('src/tables/') for f in staged_files):
        doc_suggestions.append("- docs/etl/ (table structure changes)")

    # API changes
    if any(f.startswith('api/routes/') for f in staged_files):
        doc_suggestions.append("- docs/api/endpoints.md (API changes)")

    # Dashboard changes
    if any(f.startswith('ui/dashboard/') for f in staged_files):
        doc_suggestions.append("- docs/dashboard/ (dashboard changes)")

    # Portal changes
    if any(f.startswith('ui/portal/') for f in staged_files):
        doc_suggestions.append("- docs/portal/ (portal changes)")

    # Tracker changes
    if any(f.startswith('ui/tracker/') for f in staged_files):
        doc_suggestions.append("- docs/tracker/TRACKER_REFERENCE.md (tracker changes)")

    # Skills/hooks changes
    if any(f.startswith('.claude/skills/') for f in staged_files):
        doc_suggestions.append("- docs/MASTER_INDEX.md (new/modified skills)")
        doc_suggestions.append("- CLAUDE.md (skill changes)")
    if any(f.startswith('.claude/hooks/') for f in staged_files):
        doc_suggestions.append("- docs/MASTER_INDEX.md (new/modified hooks)")

    # New markdown files
    new_md_files = [f for f in staged_files if f.endswith('.md') and not f.startswith('docs/')]
    if new_md_files:
        doc_suggestions.append("- docs/MASTER_INDEX.md (new documentation files)")

    # If code changed but no docs, prompt
    if code_changed and not docs_changed:
        suggestion_text = "\n".join(doc_suggestions) if doc_suggestions else "- Relevant documentation in docs/"

        print(json.dumps({
            "decision": "ask",
            "reason": f"""
CODE CHANGES WITHOUT DOC UPDATES DETECTED

Staged code files but no documentation updates found.

Consider updating:
{suggestion_text}
- docs/PROJECT_STATUS.md (if status changes)

Also consider running:
- /doc-sync to check for stale documentation

Continue without documentation updates?
"""
        }))

    sys.exit(0)


if __name__ == "__main__":
    main()
