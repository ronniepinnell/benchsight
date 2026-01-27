#!/usr/bin/env python3
"""
Log skill and agent usage for analytics.
Helps identify unused skills/agents for cleanup.
"""
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Log file location
LOG_FILE = Path(os.environ.get('CLAUDE_PROJECT_DIR', '.')) / '.claude' / 'usage.log'

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(0)

tool_name = data.get("tool_name", "")
tool_input = data.get("tool_input", {})

# Track Task tool usage (agents)
if tool_name == "Task":
    agent_type = tool_input.get("subagent_type", "unknown")
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": "agent",
        "name": agent_type,
        "description": tool_input.get("description", "")[:50]
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

# Track Skill tool usage
elif tool_name == "Skill":
    skill_name = tool_input.get("skill", "unknown")
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": "skill",
        "name": skill_name,
        "args": tool_input.get("args", "")[:50]
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

# Track Bash commands (for benchsight.sh usage)
elif tool_name == "Bash":
    command = tool_input.get("command", "")
    if "benchsight.sh" in command or command.startswith("gh "):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "command",
            "name": command.split()[0] if command else "unknown",
            "full": command[:100]
        }

        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

sys.exit(0)
