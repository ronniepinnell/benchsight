#!/usr/bin/env python3
"""
Goal counting rule guard.
Warns when editing files that contain goal counting logic.
"""
import json
import sys
import re

GOAL_RELATED_FILES = [
    "goals.py",
    "scoring.py",
    "fact_goals",
    "fact_player_game",
    "calculations/goals",
]

GOAL_COUNTING_REMINDER = """
CRITICAL RULE REMINDER - Goal Counting:

Goals are ONLY counted when BOTH conditions are true:
  event_type == 'Goal' AND event_detail == 'Goal_Scored'

NEVER count: event_type == 'Shot' with event_detail == 'Goal' (that's a shot attempt)

The canonical filter:
  GOAL_FILTER = (df['event_type'] == 'Goal') & (df['event_detail'] == 'Goal_Scored')
"""

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(0)

tool_name = data.get("tool_name", "")
tool_input = data.get("tool_input", {})

# Check Edit and Write tools
if tool_name not in ["Edit", "Write"]:
    sys.exit(0)

file_path = tool_input.get("file_path", "")

# Check if editing goal-related file
for pattern in GOAL_RELATED_FILES:
    if pattern in file_path.lower():
        print(json.dumps({
            "message": GOAL_COUNTING_REMINDER
        }))
        break

sys.exit(0)
