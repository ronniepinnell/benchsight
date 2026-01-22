#!/usr/bin/env python3
"""
Analyze skill/agent usage to identify unused ones.

Usage:
    python scripts/analyze-usage.py           # Show usage summary
    python scripts/analyze-usage.py --unused  # Show only unused
    python scripts/analyze-usage.py --detail  # Show detailed breakdown
"""
import json
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime, timedelta

LOG_FILE = Path(__file__).parent.parent / '.claude' / 'usage.log'
SKILLS_DIR = Path(__file__).parent.parent / '.claude' / 'skills'
AGENTS_DIR = Path(__file__).parent.parent / '.claude' / 'agents'

def get_all_skills():
    """Get all defined skills."""
    skills = []
    if SKILLS_DIR.exists():
        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir() and (skill_dir / 'SKILL.md').exists():
                skills.append(skill_dir.name)
    return set(skills)

def get_all_agents():
    """Get all defined agents."""
    agents = []
    if AGENTS_DIR.exists():
        for agent_file in AGENTS_DIR.glob('*.md'):
            agents.append(agent_file.stem)
    return set(agents)

def load_usage_log():
    """Load and parse usage log."""
    entries = []
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            for line in f:
                try:
                    entries.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
    return entries

def analyze():
    entries = load_usage_log()
    all_skills = get_all_skills()
    all_agents = get_all_agents()

    # Count usage
    skill_usage = Counter()
    agent_usage = Counter()
    command_usage = Counter()

    for entry in entries:
        if entry.get('type') == 'skill':
            skill_usage[entry['name']] += 1
        elif entry.get('type') == 'agent':
            agent_usage[entry['name']] += 1
        elif entry.get('type') == 'command':
            command_usage[entry['name']] += 1

    # Find unused
    used_skills = set(skill_usage.keys())
    used_agents = set(agent_usage.keys())
    unused_skills = all_skills - used_skills
    unused_agents = all_agents - used_agents

    # Print report
    print("=" * 60)
    print("USAGE ANALYTICS REPORT")
    print("=" * 60)
    print(f"Log entries: {len(entries)}")
    print(f"Date range: {entries[0]['timestamp'][:10] if entries else 'N/A'} to {entries[-1]['timestamp'][:10] if entries else 'N/A'}")
    print()

    print("SKILLS")
    print("-" * 40)
    print(f"Defined: {len(all_skills)}")
    print(f"Used: {len(used_skills)}")
    print(f"Unused: {len(unused_skills)}")
    print()

    if '--detail' in sys.argv or '--unused' not in sys.argv:
        print("Top skills by usage:")
        for skill, count in skill_usage.most_common(10):
            print(f"  {skill}: {count}")
        print()

    if unused_skills and ('--unused' in sys.argv or '--detail' in sys.argv):
        print("Unused skills (candidates for removal):")
        for skill in sorted(unused_skills):
            print(f"  - {skill}")
        print()

    print("AGENTS")
    print("-" * 40)
    print(f"Defined: {len(all_agents)}")
    print(f"Used: {len(used_agents)}")
    print(f"Unused: {len(unused_agents)}")
    print()

    if '--detail' in sys.argv or '--unused' not in sys.argv:
        print("Top agents by usage:")
        for agent, count in agent_usage.most_common(10):
            print(f"  {agent}: {count}")
        print()

    if unused_agents and ('--unused' in sys.argv or '--detail' in sys.argv):
        print("Unused agents (candidates for removal):")
        for agent in sorted(unused_agents):
            print(f"  - {agent}")
        print()

    if command_usage and '--detail' in sys.argv:
        print("COMMANDS")
        print("-" * 40)
        for cmd, count in command_usage.most_common(10):
            print(f"  {cmd}: {count}")

if __name__ == "__main__":
    analyze()
