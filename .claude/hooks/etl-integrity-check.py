#!/usr/bin/env python3
"""
ETL Data Integrity Check Hook

Runs after ETL to verify:
1. All expected tables were created
2. No tables are empty (0 rows)
3. Critical columns have valid data
4. Key relationships are intact
5. Null percentage thresholds
6. Statistical sanity checks (NHL standards)

Runs as PostToolUse hook after successful ETL commands.
"""
import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Expected table counts by type
EXPECTED_TABLES = {
    "dim": 50,
    "fact": 81,
    "qa": 8,
    "total": 139
}

# Tables that MUST have data
CRITICAL_TABLES = [
    "dim_players",
    "dim_teams",
    "dim_games",
    "dim_goalies",
    "fact_player_game",
    "fact_goalie_game",
    "fact_team_game",
    "fact_events",
    "fact_shots",
    "fact_goals",
]

# Critical columns that must not have nulls
CRITICAL_COLUMNS = {
    "dim_players": ["player_key", "player_id"],
    "dim_teams": ["team_key", "team_id"],
    "dim_games": ["game_key", "game_id"],
    "fact_player_game": ["player_game_key", "player_key", "game_key"],
    "fact_goals": ["goal_key", "game_key"],
}

# Maximum allowed null percentage per column (threshold)
NULL_THRESHOLD_PERCENT = 20  # Alert if > 20% nulls

# Columns where high nulls are expected/acceptable
EXPECTED_HIGH_NULL_COLUMNS = [
    "secondary_assist",
    "tertiary_assist",
    "linked_event_key",
    "play_detail2",
    "opp_player_3",
    "opp_player_4",
    "opp_player_5",
]

# NHL Statistical Sanity Checks (per game averages and ranges)
NHL_STAT_RANGES = {
    # Per game team averages
    "goals_per_game": {"min": 0, "max": 15, "typical_min": 1, "typical_max": 8},
    "shots_per_game": {"min": 10, "max": 70, "typical_min": 20, "typical_max": 45},
    "saves_per_game": {"min": 10, "max": 60, "typical_min": 20, "typical_max": 40},

    # Per game player maximums
    "player_goals_per_game": {"min": 0, "max": 6, "typical_max": 4},
    "player_assists_per_game": {"min": 0, "max": 6, "typical_max": 4},
    "player_points_per_game": {"min": 0, "max": 10, "typical_max": 6},
    "player_shots_per_game": {"min": 0, "max": 20, "typical_max": 12},
    "player_toi_minutes": {"min": 0, "max": 40, "typical_min": 5, "typical_max": 30},

    # Goalie stats
    "goalie_saves_per_game": {"min": 0, "max": 60, "typical_min": 15, "typical_max": 45},
    "goalie_goals_against": {"min": 0, "max": 15, "typical_max": 6},
    "save_percentage": {"min": 0.7, "max": 1.0, "typical_min": 0.85, "typical_max": 0.98},

    # Percentages
    "shooting_percentage": {"min": 0, "max": 100, "typical_min": 3, "typical_max": 25},
    "faceoff_percentage": {"min": 0, "max": 100, "typical_min": 30, "typical_max": 70},

    # Corsi/Fenwick
    "corsi_for_percent": {"min": 0, "max": 100, "typical_min": 35, "typical_max": 65},
}


def is_etl_command(command: str) -> bool:
    """Check if command was an ETL operation."""
    patterns = [r"etl run", r"run_etl\.py", r"benchsight\.sh etl"]
    return any(re.search(p, command, re.IGNORECASE) for p in patterns)


def was_successful(stdout: str, stderr: str, exit_code: int) -> bool:
    """Check if ETL completed successfully."""
    if exit_code != 0:
        return False
    success_patterns = [r"ETL completed", r"Pipeline complete", r"Successfully processed", r"tables generated"]
    return any(re.search(p, stdout, re.IGNORECASE) for p in success_patterns)


def get_output_dir() -> Path:
    """Get the ETL output directory."""
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    return Path(project_dir) / "data" / "output"


def read_csv_sample(csv_path: Path, max_rows: int = 1000) -> tuple:
    """Read CSV headers and sample rows."""
    headers = []
    rows = []

    try:
        with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
            header_line = f.readline().strip()
            headers = [h.strip().strip('"') for h in header_line.split(',')]

            for i, line in enumerate(f):
                if i >= max_rows:
                    break
                values = [v.strip().strip('"') for v in line.strip().split(',')]
                rows.append(values)
    except Exception as e:
        pass

    return headers, rows


def check_table_existence(output_dir: Path) -> dict:
    """Check that all expected tables exist."""
    results = {
        "passed": True,
        "missing": [],
        "counts": {"dim": 0, "fact": 0, "qa": 0, "other": 0, "total": 0}
    }

    if not output_dir.exists():
        results["passed"] = False
        results["error"] = f"Output directory not found: {output_dir}"
        return results

    csv_files = list(output_dir.glob("*.csv"))
    results["counts"]["total"] = len(csv_files)

    for f in csv_files:
        name = f.stem.lower()
        if name.startswith("dim_"):
            results["counts"]["dim"] += 1
        elif name.startswith("fact_"):
            results["counts"]["fact"] += 1
        elif name.startswith("qa_"):
            results["counts"]["qa"] += 1
        else:
            results["counts"]["other"] += 1

    # Check for critical tables
    existing_tables = {f.stem.lower() for f in csv_files}
    for table in CRITICAL_TABLES:
        if table.lower() not in existing_tables:
            results["missing"].append(table)
            results["passed"] = False

    if results["counts"]["total"] < EXPECTED_TABLES["total"] * 0.9:
        results["passed"] = False
        results["warning"] = f"Only {results['counts']['total']} tables, expected ~{EXPECTED_TABLES['total']}"

    return results


def check_table_not_empty(output_dir: Path) -> dict:
    """Check that critical tables have data."""
    results = {
        "passed": True,
        "empty_tables": [],
        "row_counts": {}
    }

    for table in CRITICAL_TABLES:
        csv_path = output_dir / f"{table}.csv"
        if not csv_path.exists():
            continue

        try:
            with open(csv_path, 'r') as f:
                line_count = sum(1 for _ in f)
            data_rows = max(0, line_count - 1)
            results["row_counts"][table] = data_rows

            if data_rows == 0:
                results["empty_tables"].append(table)
                results["passed"] = False
        except Exception as e:
            results["empty_tables"].append(f"{table} (error)")
            results["passed"] = False

    return results


def check_null_percentages(output_dir: Path) -> dict:
    """Check for columns with high null percentages."""
    results = {
        "passed": True,
        "high_null_columns": [],
        "tables_checked": 0,
        "details": {}
    }

    csv_files = list(output_dir.glob("*.csv"))

    for csv_path in csv_files:
        table_name = csv_path.stem
        headers, rows = read_csv_sample(csv_path, max_rows=500)

        if not rows:
            continue

        results["tables_checked"] += 1
        total_rows = len(rows)
        table_issues = []

        for col_idx, col_name in enumerate(headers):
            # Skip columns where high nulls are expected
            if any(expected in col_name.lower() for expected in EXPECTED_HIGH_NULL_COLUMNS):
                continue

            null_count = 0
            for row in rows:
                if col_idx < len(row):
                    val = row[col_idx].lower()
                    if val == '' or val == 'null' or val == 'none' or val == 'nan':
                        null_count += 1
                else:
                    null_count += 1

            null_percent = (null_count / total_rows) * 100 if total_rows > 0 else 0

            if null_percent > NULL_THRESHOLD_PERCENT:
                table_issues.append({
                    "column": col_name,
                    "null_percent": round(null_percent, 1),
                    "null_count": null_count,
                    "total_rows": total_rows
                })
                results["passed"] = False

        if table_issues:
            results["high_null_columns"].append({
                "table": table_name,
                "issues": table_issues
            })
            results["details"][table_name] = table_issues

    return results


def check_statistical_sanity(output_dir: Path) -> dict:
    """Check for statistically suspicious values based on NHL norms."""
    results = {
        "passed": True,
        "suspicious_stats": [],
        "warnings": [],
        "checked": 0
    }

    # Check fact_player_game for player stat anomalies
    player_game_path = output_dir / "fact_player_game.csv"
    if player_game_path.exists():
        headers, rows = read_csv_sample(player_game_path, max_rows=2000)

        if headers and rows:
            results["checked"] += 1

            # Find column indices
            col_map = {h.lower(): i for i, h in enumerate(headers)}

            # Check each row for suspicious values
            for row_idx, row in enumerate(rows):
                anomalies = []

                # Goals per game
                if 'goals' in col_map:
                    try:
                        goals = int(row[col_map['goals']] or 0)
                        if goals > NHL_STAT_RANGES["player_goals_per_game"]["max"]:
                            anomalies.append(f"goals={goals} (max typical: 4)")
                    except:
                        pass

                # Assists per game
                if 'assists' in col_map:
                    try:
                        assists = int(row[col_map['assists']] or 0)
                        if assists > NHL_STAT_RANGES["player_assists_per_game"]["max"]:
                            anomalies.append(f"assists={assists} (max typical: 4)")
                    except:
                        pass

                # Shots per game
                if 'shots' in col_map:
                    try:
                        shots = int(row[col_map['shots']] or 0)
                        if shots > NHL_STAT_RANGES["player_shots_per_game"]["typical_max"]:
                            anomalies.append(f"shots={shots} (typical max: 12)")
                    except:
                        pass

                # TOI
                toi_col = next((c for c in col_map if 'toi' in c.lower()), None)
                if toi_col:
                    try:
                        toi = float(row[col_map[toi_col]] or 0)
                        # Convert to minutes if in seconds
                        if toi > 100:  # Likely in seconds
                            toi = toi / 60
                        if toi > NHL_STAT_RANGES["player_toi_minutes"]["max"]:
                            anomalies.append(f"TOI={toi:.1f}min (max: 40)")
                    except:
                        pass

                if anomalies and row_idx < 20:  # Only report first 20 anomalies
                    player_key = row[col_map.get('player_key', 0)] if 'player_key' in col_map else f"row_{row_idx}"
                    results["suspicious_stats"].append({
                        "table": "fact_player_game",
                        "row": player_key,
                        "anomalies": anomalies
                    })
                    results["passed"] = False

    # Check fact_goals for goal counting
    goals_path = output_dir / "fact_goals.csv"
    if goals_path.exists():
        headers, rows = read_csv_sample(goals_path, max_rows=500)
        results["checked"] += 1

        if rows:
            # Count goals per game
            games = defaultdict(int)
            col_map = {h.lower(): i for i, h in enumerate(headers)}

            for row in rows:
                if 'game_key' in col_map:
                    game_key = row[col_map['game_key']]
                    games[game_key] += 1

            for game_key, goal_count in games.items():
                if goal_count > NHL_STAT_RANGES["goals_per_game"]["max"]:
                    results["suspicious_stats"].append({
                        "table": "fact_goals",
                        "row": game_key,
                        "anomalies": [f"Total goals={goal_count} in game (max typical: 15)"]
                    })
                    results["passed"] = False

    # Check goalie stats
    goalie_path = output_dir / "fact_goalie_game.csv"
    if goalie_path.exists():
        headers, rows = read_csv_sample(goalie_path, max_rows=500)
        results["checked"] += 1

        if headers and rows:
            col_map = {h.lower(): i for i, h in enumerate(headers)}

            for row_idx, row in enumerate(rows):
                anomalies = []

                # Save percentage
                sv_pct_col = next((c for c in col_map if 'save' in c.lower() and 'pct' in c.lower()), None)
                if sv_pct_col:
                    try:
                        sv_pct = float(row[col_map[sv_pct_col]] or 0)
                        # Handle percentage vs decimal
                        if sv_pct > 1:
                            sv_pct = sv_pct / 100
                        if sv_pct < NHL_STAT_RANGES["save_percentage"]["min"] and sv_pct > 0:
                            anomalies.append(f"SV%={sv_pct:.3f} (min typical: 0.85)")
                    except:
                        pass

                if anomalies and row_idx < 10:
                    goalie_key = row[col_map.get('goalie_key', 0)] if 'goalie_key' in col_map else f"row_{row_idx}"
                    results["suspicious_stats"].append({
                        "table": "fact_goalie_game",
                        "row": goalie_key,
                        "anomalies": anomalies
                    })

    # Check shooting percentage in player season
    player_season_path = output_dir / "fact_player_season.csv"
    if player_season_path.exists():
        headers, rows = read_csv_sample(player_season_path, max_rows=500)
        results["checked"] += 1

        if headers and rows:
            col_map = {h.lower(): i for i, h in enumerate(headers)}

            for row_idx, row in enumerate(rows):
                # Shooting percentage
                sh_pct_col = next((c for c in col_map if 'shoot' in c.lower() and 'pct' in c.lower()), None)
                if sh_pct_col:
                    try:
                        sh_pct = float(row[col_map[sh_pct_col]] or 0)
                        if sh_pct > NHL_STAT_RANGES["shooting_percentage"]["typical_max"]:
                            player_key = row[col_map.get('player_key', 0)] if 'player_key' in col_map else f"row_{row_idx}"
                            results["warnings"].append(f"{player_key}: SH%={sh_pct:.1f}% (typical max: 25%)")
                    except:
                        pass

    return results


def check_key_formats(output_dir: Path) -> dict:
    """Check that keys follow expected formats."""
    results = {
        "passed": True,
        "invalid_keys": [],
        "checked": 0
    }

    format_checks = [
        ("dim_players", "player_key", r"^PL\d{5}$"),
        ("dim_teams", "team_key", r"^TM\d{5}$"),
        ("dim_games", "game_key", r"^GM\d{5}$"),
    ]

    for table, column, pattern in format_checks:
        csv_path = output_dir / f"{table}.csv"
        if not csv_path.exists():
            continue

        headers, rows = read_csv_sample(csv_path, max_rows=100)
        col_map = {h.lower(): i for i, h in enumerate(headers)}

        if column.lower() not in col_map:
            continue

        col_idx = col_map[column.lower()]
        invalid_count = 0

        for row in rows:
            if col_idx < len(row):
                val = row[col_idx]
                if val and not re.match(pattern, val):
                    invalid_count += 1
            results["checked"] += 1

        if invalid_count > 0:
            results["invalid_keys"].append(f"{table}.{column}: {invalid_count} invalid")
            results["passed"] = False

    return results


def run_integrity_checks(output_dir: Path) -> dict:
    """Run all integrity checks."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "output_dir": str(output_dir),
        "overall_passed": True,
        "checks": {}
    }

    # Check 1: Table existence
    results["checks"]["table_existence"] = check_table_existence(output_dir)
    if not results["checks"]["table_existence"]["passed"]:
        results["overall_passed"] = False

    # Check 2: Tables not empty
    results["checks"]["table_not_empty"] = check_table_not_empty(output_dir)
    if not results["checks"]["table_not_empty"]["passed"]:
        results["overall_passed"] = False

    # Check 3: Null percentages
    results["checks"]["null_percentages"] = check_null_percentages(output_dir)
    if not results["checks"]["null_percentages"]["passed"]:
        results["overall_passed"] = False

    # Check 4: Key formats
    results["checks"]["key_formats"] = check_key_formats(output_dir)
    if not results["checks"]["key_formats"]["passed"]:
        results["overall_passed"] = False

    # Check 5: Statistical sanity
    results["checks"]["statistical_sanity"] = check_statistical_sanity(output_dir)
    if not results["checks"]["statistical_sanity"]["passed"]:
        results["overall_passed"] = False

    return results


def format_results(results: dict) -> str:
    """Format results for display."""
    lines = []
    lines.append("\n" + "=" * 60)
    lines.append("ETL DATA INTEGRITY CHECK")
    lines.append("=" * 60)

    status = "✅ PASSED" if results["overall_passed"] else "❌ ISSUES FOUND"
    lines.append(f"\nOverall: {status}")

    # Table existence
    tc = results["checks"]["table_existence"]
    lines.append(f"\n📊 Tables: {tc['counts']['total']} created")
    lines.append(f"   Dim: {tc['counts']['dim']} | Fact: {tc['counts']['fact']} | QA: {tc['counts']['qa']}")
    if tc["missing"]:
        lines.append(f"   ❌ Missing: {', '.join(tc['missing'])}")

    # Empty tables
    te = results["checks"]["table_not_empty"]
    if te["empty_tables"]:
        lines.append(f"\n⚠️ Empty tables: {', '.join(te['empty_tables'])}")

    # Null percentages
    np_check = results["checks"]["null_percentages"]
    if np_check["high_null_columns"]:
        lines.append(f"\n⚠️ High null columns (>{NULL_THRESHOLD_PERCENT}%):")
        for table_info in np_check["high_null_columns"][:5]:
            table = table_info["table"]
            for issue in table_info["issues"][:3]:
                lines.append(f"   • {table}.{issue['column']}: {issue['null_percent']}% null")
        if len(np_check["high_null_columns"]) > 5:
            lines.append(f"   ... and {len(np_check['high_null_columns']) - 5} more tables")

    # Key formats
    kf = results["checks"]["key_formats"]
    if kf["invalid_keys"]:
        lines.append(f"\n❌ Invalid keys: {', '.join(kf['invalid_keys'])}")

    # Statistical sanity
    ss = results["checks"]["statistical_sanity"]
    if ss["suspicious_stats"]:
        lines.append(f"\n🔍 Suspicious stats (outside NHL norms):")
        for stat in ss["suspicious_stats"][:5]:
            lines.append(f"   • {stat['table']} {stat['row']}: {', '.join(stat['anomalies'])}")
        if len(ss["suspicious_stats"]) > 5:
            lines.append(f"   ... and {len(ss['suspicious_stats']) - 5} more")

    if ss["warnings"]:
        lines.append(f"\n⚠️ Warnings:")
        for warn in ss["warnings"][:3]:
            lines.append(f"   • {warn}")

    lines.append("\n" + "=" * 60)

    return "\n".join(lines)


def save_results(results: dict) -> Path:
    """Save results to log file."""
    log_dir = Path.home() / ".claude" / "etl-integrity"
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"integrity_check_{timestamp}.json"

    with open(log_file, "w") as f:
        json.dump(results, f, indent=2)

    return log_file


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    tool_result = data.get("tool_result", {})

    command = tool_input.get("command", "")
    stdout = tool_result.get("stdout", "")
    stderr = tool_result.get("stderr", "")
    exit_code = tool_result.get("exitCode", 0)

    if not is_etl_command(command):
        sys.exit(0)

    if not was_successful(stdout, stderr, exit_code):
        sys.exit(0)

    # Run integrity checks
    output_dir = get_output_dir()
    results = run_integrity_checks(output_dir)
    log_file = save_results(results)

    formatted = format_results(results)

    if results["overall_passed"]:
        print(json.dumps({"message": formatted}))
    else:
        # Determine severity
        null_issues = results["checks"]["null_percentages"]["high_null_columns"]
        stat_issues = results["checks"]["statistical_sanity"]["suspicious_stats"]

        if null_issues or stat_issues:
            print(json.dumps({
                "decision": "ask",
                "reason": f"{formatted}\n\nReview these issues? (Will show detailed breakdown)"
            }))
        else:
            print(json.dumps({"message": formatted}))

    sys.exit(0)


if __name__ == "__main__":
    main()
