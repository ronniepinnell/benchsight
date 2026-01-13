#!/usr/bin/env python3
"""
Generate detailed data dictionary for all BenchSight tables.

Outputs:
- docs/DATA_DICTIONARY_FULL.md - Complete documentation
- docs/validation_tracker.csv - Column-by-column validation status

Format matches the detailed view with:
- Table metadata (description, purpose, source, logic, grain, rows, columns)
- Column documentation (type, description, context, calculation, validation status)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json

# =============================================================================
# TABLE METADATA DEFINITIONS
# =============================================================================
# This is the source of truth for table documentation.
# Update this when tables change or new information is verified.

TABLE_METADATA = {
    # -------------------------------------------------------------------------
    # CORE FACT TABLES
    # -------------------------------------------------------------------------
    'fact_events': {
        'description': 'Raw event-level game tracking data - SOURCE OF TRUTH',
        'purpose': 'Store every tracked event. All other tables derive from this.',
        'source_module': 'src/etl/processors/events_processor.py:process()',
        'logic': 'Direct load from tracking spreadsheet with standardization',
        'grain': 'One row per tracked event',
    },
    'fact_event_players': {
        'description': 'Bridge table linking events to players with their roles',
        'purpose': 'Enable player-level stats from events. Query goals/assists/shots by player.',
        'source_module': 'src/core/base_etl.py:create_event_players()',
        'logic': 'Unpivots event_player_1 through event_player_6 from fact_events into rows',
        'grain': 'One row per player per event',
    },
    'fact_gameroster': {
        'description': 'Player statistics aggregated per game',
        'purpose': 'Game-level player boxscore. Used for game summaries.',
        'source_module': 'src/etl/processors/gameroster_processor.py:process()',
        'logic': 'Aggregate goals/assists/points from fact_events grouped by game_id + player_id',
        'grain': 'One row per player per game',
    },
    'fact_player_season_stats': {
        'description': 'Player statistics aggregated per season',
        'purpose': 'Season leaderboards, player profiles, historical comparison.',
        'source_module': 'src/etl/processors/player_stats_processor.py:process()',
        'logic': 'Sum of game stats from fact_gameroster grouped by player_id + season_id',
        'grain': 'One row per player per season',
    },
    'fact_team_season_stats': {
        'description': 'Team statistics aggregated per season',
        'purpose': 'Team standings, team comparison, season summaries.',
        'source_module': 'src/etl/processors/team_stats_processor.py:process()',
        'logic': 'Aggregate from fact_events + fact_gameroster grouped by team_id + season_id',
        'grain': 'One row per team per season',
    },
    'fact_goalie_game_stats': {
        'description': 'Goalie-specific statistics per game',
        'purpose': 'Goalie boxscore with saves, goals against, save percentage.',
        'source_module': 'src/etl/processors/goalie_processor.py:process()',
        'logic': 'Filter goalies from roster, calculate saves from shots faced minus goals against',
        'grain': 'One row per goalie per game',
    },
    'fact_shots': {
        'description': 'Shot-level event data',
        'purpose': 'Shot analysis, shot charts, shooting percentage calculations.',
        'source_module': 'src/etl/processors/shots_processor.py:process()',
        'logic': "Filter fact_events WHERE event_type = 'Shot'",
        'grain': 'One row per shot',
    },
    'fact_goals': {
        'description': 'Goal-level event data',
        'purpose': 'Goal analysis, scoring patterns, assist tracking.',
        'source_module': 'src/etl/processors/goals_processor.py:process()',
        'logic': "Filter fact_events WHERE event_type = 'Goal' AND event_detail = 'Goal_Scored'",
        'grain': 'One row per goal',
    },
    'fact_registration': {
        'description': 'Player season registration data',
        'purpose': 'Track player registration, draft status, skill ratings.',
        'source_module': 'src/etl/processors/registration_processor.py:process()',
        'logic': 'Direct load from registration spreadsheet',
        'grain': 'One row per player per season registration',
    },
    
    # -------------------------------------------------------------------------
    # DIMENSION TABLES
    # -------------------------------------------------------------------------
    'dim_player': {
        'description': 'Player master reference data',
        'purpose': 'Central player lookup. All player FKs reference this.',
        'source_module': 'src/etl/processors/dim_processor.py:create_dim_player()',
        'logic': 'Deduplicated from registration + roster data',
        'grain': 'One row per unique player',
    },
    'dim_team': {
        'description': 'Team master reference data',
        'purpose': 'Central team lookup. All team FKs reference this.',
        'source_module': 'src/etl/processors/dim_processor.py:create_dim_team()',
        'logic': 'Extracted from schedule + roster data',
        'grain': 'One row per unique team',
    },
    'dim_game': {
        'description': 'Game master reference data',
        'purpose': 'Central game lookup. Game schedule and results.',
        'source_module': 'src/etl/processors/dim_processor.py:create_dim_game()',
        'logic': 'From schedule with scores added from fact_events',
        'grain': 'One row per unique game',
    },
    'dim_season': {
        'description': 'Season definitions',
        'purpose': 'Season lookup and date ranges.',
        'source_module': 'src/etl/processors/dim_processor.py:create_dim_season()',
        'logic': 'Extracted from schedule data',
        'grain': 'One row per season',
    },
    'dim_event_type': {
        'description': 'Event type code reference',
        'purpose': 'Lookup table for event_type values.',
        'source_module': 'src/etl/processors/dim_processor.py:create_dim_event_type()',
        'logic': 'Distinct event_type values from fact_events',
        'grain': 'One row per event type',
    },
    'dim_event_detail': {
        'description': 'Event detail code reference',
        'purpose': 'Lookup table for event_detail values.',
        'source_module': 'src/etl/processors/dim_processor.py:create_dim_event_detail()',
        'logic': 'Distinct event_detail values from fact_events',
        'grain': 'One row per event detail',
    },
}

# =============================================================================
# COLUMN DEFINITIONS
# =============================================================================
# Define known columns with their metadata.
# Column types: Explicit, Calculated, Derived, FK, Unknown

COLUMN_DEFINITIONS = {
    # Common columns across tables
    'event_id': {
        'description': 'Unique event identifier',
        'calculation': 'Generated sequence per game',
        'column_type': 'Derived',
    },
    'game_id': {
        'description': 'Game identifier',
        'context': 'FK to dim_game.game_id',
        'calculation': 'From schedule or tracking data',
        'column_type': 'FK',
    },
    'player_id': {
        'description': 'Player identifier',
        'context': 'FK to dim_player.player_id. Format P######.',
        'calculation': 'Lookup from player name in dim_player',
        'column_type': 'FK',
    },
    'team_id': {
        'description': 'Team identifier',
        'context': 'FK to dim_team.team_id',
        'calculation': 'From roster or event data',
        'column_type': 'FK',
    },
    'season_id': {
        'description': 'Season identifier',
        'context': 'FK to dim_season.season_id',
        'calculation': 'From schedule data',
        'column_type': 'FK',
    },
    'goals': {
        'description': 'Goals scored',
        'calculation': "COUNT(*) WHERE event_type='Goal' AND event_detail='Goal_Scored'",
        'column_type': 'Calculated',
    },
    'assists': {
        'description': 'Assists (primary + secondary)',
        'calculation': "COUNT(*) WHERE player is event_player_2 or event_player_3 on goal events",
        'column_type': 'Calculated',
    },
    'points': {
        'description': 'Total points',
        'calculation': 'goals + assists',
        'column_type': 'Calculated',
    },
    'games_played': {
        'description': 'Number of games played',
        'calculation': 'COUNT(DISTINCT game_id)',
        'column_type': 'Calculated',
    },
    'event_type': {
        'description': 'Type of event',
        'context': 'Values: Shot, Goal, Pass, Faceoff, Hit, etc.',
        'column_type': 'Explicit',
    },
    'event_detail': {
        'description': 'Detail/subtype of event',
        'context': 'Values: Goal_Scored, Shot_Goal, Wrist, Slap, etc.',
        'column_type': 'Explicit',
    },
    'event_player_1': {
        'description': 'Primary player on event',
        'context': 'Scorer, shooter, passer, etc.',
        'column_type': 'Explicit',
    },
    'event_player_2': {
        'description': 'Secondary player on event',
        'context': 'Primary assist, defender, etc.',
        'column_type': 'Explicit',
    },
    'event_player_3': {
        'description': 'Tertiary player on event',
        'context': 'Secondary assist',
        'column_type': 'Explicit',
    },
}

# =============================================================================
# GENERATOR FUNCTIONS
# =============================================================================

def analyze_column(series: pd.Series, col_name: str) -> dict:
    """Analyze a column and return metadata."""
    non_null = series.dropna()
    total = len(series)
    non_null_count = len(non_null)
    null_pct = round((total - non_null_count) / total * 100, 1) if total > 0 else 0
    
    # Get column definition if exists
    col_def = COLUMN_DEFINITIONS.get(col_name, {})
    
    return {
        'column': col_name,
        'data_type': str(series.dtype),
        'description': col_def.get('description', '-'),
        'context_mapping': col_def.get('context', ''),
        'calculation_formula': col_def.get('calculation', ''),
        'column_type': col_def.get('column_type', 'Unknown'),
        'non_null': non_null_count,
        'null_pct': null_pct,
        'validated': 'No',
        'validated_by': '',
        'validated_date': '',
        'notes': '',
    }


def generate_table_doc(table_name: str, df: pd.DataFrame) -> str:
    """Generate markdown documentation for a table."""
    meta = TABLE_METADATA.get(table_name, {})
    
    doc = f"""
## {table_name}

| Property | Value |
|----------|-------|
| **Description** | {meta.get('description', 'No description')} |
| **Purpose** | {meta.get('purpose', '-')} |
| **Source Module** | `{meta.get('source_module', 'Unknown')}` |
| **Logic** | {meta.get('logic', '-')} |
| **Grain** | {meta.get('grain', '-')} |
| **Rows** | {len(df):,} |
| **Columns** | {len(df.columns)} |

### Column Documentation

**Legend:** 
`Explicit` = From raw data | 
`Calculated` = Formula-based | 
`Derived` = Generated key/aggregate | 
`FK` = Foreign key lookup

| Column | Data Type | Description | Context / Mapping | Calculation / Formula | Type | Non-Null | Null % | Validated |
|--------|-----------|-------------|-------------------|----------------------|------|----------|--------|-----------|
"""
    
    for col in df.columns:
        col_info = analyze_column(df[col], col)
        doc += f"| {col_info['column']} | {col_info['data_type']} | {col_info['description']} | {col_info['context_mapping']} | {col_info['calculation_formula']} | {col_info['column_type']} | {col_info['non_null']:,} | {col_info['null_pct']}% | {col_info['validated']} |\n"
    
    doc += "\n---\n"
    return doc


def generate_validation_tracker(data_dir: Path) -> pd.DataFrame:
    """Generate validation tracker CSV with all columns from all tables."""
    rows = []
    
    for csv_file in sorted(data_dir.glob('*.csv')):
        table_name = csv_file.stem
        df = pd.read_csv(csv_file, nrows=1000, low_memory=False)  # Sample for speed
        
        for col in df.columns:
            col_info = analyze_column(df[col], col)
            col_info['table_name'] = table_name
            rows.append(col_info)
    
    return pd.DataFrame(rows)


def main():
    """Generate all documentation."""
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / 'data' / 'output'
    docs_dir = base_dir / 'docs'
    
    print("=" * 60)
    print("GENERATING DATA DICTIONARY")
    print("=" * 60)
    
    # Generate full data dictionary markdown
    full_doc = f"""# BenchSight Data Dictionary (Full)

**Auto-generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Tables:** 131
**Version:** 21.4

---

## Quick Links

### Core Tables
- [fact_events](#fact_events)
- [fact_gameroster](#fact_gameroster)
- [fact_player_season_stats](#fact_player_season_stats)
- [dim_player](#dim_player)
- [dim_team](#dim_team)
- [dim_game](#dim_game)

---

## Column Type Legend

| Type | Meaning | Example |
|------|---------|---------|
| **Explicit** | Direct from raw/source data | event_type, period |
| **Calculated** | Formula-based derivation | points = goals + assists |
| **Derived** | Generated keys/aggregates | player_game_key |
| **FK** | Foreign key lookup | player_id → dim_player |
| **Unknown** | Needs investigation | - |

---

## Critical Business Rules

### Goal Counting (CANONICAL)
```sql
-- THE ONLY WAY TO COUNT GOALS:
WHERE event_type = 'Goal' AND event_detail = 'Goal_Scored'

-- Shot_Goal is the SHOT, not the goal!
```

### Player Attribution
```
event_player_1 = Primary player (scorer, shooter)
event_player_2 = Primary assist / secondary player
event_player_3 = Secondary assist
```

---

"""
    
    # Process each table
    tables_processed = 0
    for csv_file in sorted(data_dir.glob('*.csv')):
        table_name = csv_file.stem
        df = pd.read_csv(csv_file, low_memory=False)
        full_doc += generate_table_doc(table_name, df)
        tables_processed += 1
        print(f"  ✓ {table_name}: {len(df):,} rows, {len(df.columns)} cols")
    
    # Write markdown
    with open(docs_dir / 'DATA_DICTIONARY_FULL.md', 'w') as f:
        f.write(full_doc)
    print(f"\n✓ Generated DATA_DICTIONARY_FULL.md ({tables_processed} tables)")
    
    # Generate validation tracker
    print("\nGenerating validation tracker...")
    tracker_df = generate_validation_tracker(data_dir)
    tracker_df.to_csv(docs_dir / 'validation_tracker.csv', index=False)
    print(f"✓ Generated validation_tracker.csv ({len(tracker_df)} columns)")
    
    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
