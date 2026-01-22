#!/usr/bin/env python3
"""
github-sync-reminder.py - Remind to sync GitHub issues after commits.

Triggers after git commit commands to remind about syncing the backlog.
"""
import json
import sys
import subprocess
import os


def check_github_cli():
    """Check if gh CLI is installed and authenticated."""
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def get_issue_counts():
    """Get quick issue counts from GitHub."""
    try:
        # Quick count of open issues
        result = subprocess.run(
            ["gh", "issue", "list", "--state", "open", "--limit", "1000", "--json", "number"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            issues = json.loads(result.stdout)
            return len(issues)
    except Exception:
        pass
    return None


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    command = data.get("tool_input", {}).get("command", "")
    stdout = data.get("tool_result", {}).get("stdout", "")

    # Only trigger after successful git commit
    if tool_name != "Bash":
        sys.exit(0)

    if "git commit" not in command:
        sys.exit(0)

    # Check if commit was successful (has commit message in output)
    if "create mode" not in stdout and "[" not in stdout:
        sys.exit(0)

    # Check if gh CLI available
    if not check_github_cli():
        sys.exit(0)

    # Get current counts
    open_count = get_issue_counts()

    # Output a brief status (not blocking)
    status_msg = f"Open issues: {open_count}" if open_count else "Issues: unknown"

    print(json.dumps({
        "decision": "approve",  # Don't block, just inform
        "reason": f"""
COMMIT SUCCESSFUL - GitHub Sync Reminder

{status_msg}

To sync GitHub issues with backlog:
  ./scripts/sync-github-issues.sh

Or check status with:
  ./scripts/sync-github-issues.sh --check
"""
    }))

    sys.exit(0)


if __name__ == "__main__":
    main()
