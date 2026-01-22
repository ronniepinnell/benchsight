#!/usr/bin/env python3
"""
Post-ETL execution reminder.
Prompts to run validation after ETL commands.
"""
import json
import sys

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(0)

tool_name = data.get("tool_name", "")
tool_input = data.get("tool_input", {})
tool_result = data.get("tool_result", {})

# Only trigger after Bash commands
if tool_name != "Bash":
    sys.exit(0)

command = tool_input.get("command", "")

# Check if this was an ETL run command
if "etl run" in command and "validate" not in command:
    # Check if command succeeded (no error in result)
    stdout = tool_result.get("stdout", "")
    stderr = tool_result.get("stderr", "")

    if "error" not in stderr.lower() and "failed" not in stderr.lower():
        print(json.dumps({
            "message": "\n[ETL Complete] Run /validate to verify data quality."
        }))

sys.exit(0)
