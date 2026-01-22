#!/usr/bin/env python3
"""
Pre-execution bash validation for BenchSight.
Prevents dangerous operations and common mistakes.
"""
import json
import sys
import re

# Patterns to block with explanations
DANGEROUS_PATTERNS = [
    (r"rm\s+-rf\s+data/output", "Use './benchsight.sh etl run --wipe' instead of direct deletion"),
    (r"rm\s+-rf\s+\.git", "Cannot delete .git directory"),
    (r"DROP\s+TABLE.*(fact_|dim_|qa_)", "Use database migrations, not raw SQL drops"),
    (r"TRUNCATE\s+TABLE", "Use database migrations for truncation"),
    (r"git\s+push.*--force.*main", "Force push to main is prohibited"),
    (r"git\s+reset\s+--hard.*origin/main", "Hard reset to main requires explicit confirmation"),
]

# Patterns that require confirmation
WARN_PATTERNS = [
    (r"production", "Command references production - please confirm"),
    (r"supabase.*migration.*push", "Database migration push - please confirm"),
    (r"vercel\s+--prod", "Production deployment - please confirm"),
]

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(0)

tool_name = data.get("tool_name", "")
if tool_name != "Bash":
    sys.exit(0)

command = data.get("tool_input", {}).get("command", "")

# Check for blocked patterns
for pattern, reason in DANGEROUS_PATTERNS:
    if re.search(pattern, command, re.IGNORECASE):
        print(json.dumps({
            "decision": "block",
            "reason": reason
        }))
        sys.exit(0)

# Check for warning patterns
for pattern, reason in WARN_PATTERNS:
    if re.search(pattern, command, re.IGNORECASE):
        print(json.dumps({
            "decision": "ask",
            "reason": reason
        }))
        sys.exit(0)

# Allow command
sys.exit(0)
