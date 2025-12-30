# BenchSight Technical Diagrams

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                   BenchSight System                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────┐
│   Data Entry    │     │    ETL Layer    │     │   Data Store    │     │  Consumers  │
│                 │     │                 │     │                 │     │             │
│ ┌─────────────┐ │     │ ┌─────────────┐ │     │ ┌─────────────┐ │     │ ┌─────────┐ │
│ │   Tracker   │─┼────►│ │  Ingestion  │ │     │ │    CSV      │ │     │ │Dashboard│ │
│ │   (HTML)    │ │     │ │   Layer     │ │     │ │   Files     │ │     │ │  (HTML) │ │
│ └─────────────┘ │     │ └──────┬──────┘ │     │ └──────┬──────┘ │     │ └─────────┘ │
│                 │     │        │        │     │        │        │     │             │
│ ┌─────────────┐ │     │ ┌──────▼──────┐ │     │ ┌──────▼──────┐ │     │ ┌─────────┐ │
│ │   Portal    │─┼────►│ │ Transform   │─┼────►│ │  Supabase   │─┼────►│ │ Portal  │ │
│ │   (HTML)    │ │     │ │   Layer     │ │     │ │ (PostgreSQL)│ │     │ │  (HTML) │ │
│ └─────────────┘ │     │ └──────┬──────┘ │     │ └─────────────┘ │     │ └─────────┘ │
│                 │     │        │        │     │                 │     │             │
│ ┌─────────────┐ │     │ ┌──────▼──────┐ │     │                 │     │ ┌─────────┐ │
│ │   Excel     │─┼────►│ │  Datamart   │ │     │                 │     │ │Power BI │ │
│ │  Tracking   │ │     │ │   Layer     │ │     │                 │     │ │ Reports │ │
│ └─────────────┘ │     │ └─────────────┘ │     │                 │     │ └─────────┘ │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────┘
```

## 2. ETL Pipeline Detail

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              ETL Pipeline Stages                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘

    INPUT                    STAGE               INTERMEDIATE            DATAMART
    ─────                    ─────               ────────────            ────────

┌──────────────┐        ┌──────────────┐       ┌──────────────┐      ┌──────────────┐
│BLB_Tables.xlsx│───────►│ stg_players  │──────►│ int_players  │─────►│ dim_player   │
│              │        │ stg_teams    │       │ int_teams    │      │ dim_team     │
│ • Players    │        │ stg_schedule │       │ int_schedule │      │ dim_schedule │
│ • Teams      │        └──────────────┘       └──────────────┘      └──────────────┘
│ • Schedule   │
└──────────────┘

┌──────────────┐        ┌──────────────┐       ┌──────────────┐      ┌──────────────┐
│Game Tracking │───────►│ stg_events   │──────►│ int_events   │─────►│ fact_events  │
│   Excel      │        │ stg_shifts   │       │ int_shifts   │      │ fact_shifts  │
│              │        │ stg_xy       │       │ int_xy       │      │ fact_*_xy    │
│ • Events     │        └──────────────┘       └──────────────┘      └──────────────┘
│ • Shifts     │                                      │
│ • XY coords  │                                      │
└──────────────┘                                      ▼
                                              ┌──────────────┐      ┌──────────────┐
                                              │ Stats Calc   │─────►│fact_player_  │
                                              │              │      │ game_stats   │
                                              │ • 317 cols   │      │ (317 cols)   │
                                              │ • Per player │      └──────────────┘
                                              │ • Per game   │
                                              └──────────────┘
                                                      │
                                                      ▼
                                              ┌──────────────┐      ┌──────────────┐
                                              │ Analytics    │─────►│ fact_h2h     │
                                              │              │      │ fact_wowy    │
                                              │ • H2H        │      │ fact_line_   │
                                              │ • WOWY       │      │  combos      │
                                              │ • Lines      │      └──────────────┘
                                              └──────────────┘
```

## 3. Data Loading Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              Supabase Loading Flow                                   │
└─────────────────────────────────────────────────────────────────────────────────────┘

    CSV FILES              LOADER                  SUPABASE               RESULT
    ─────────              ──────                  ────────               ──────

┌──────────────┐      ┌──────────────────┐     ┌──────────────┐     ┌──────────────┐
│data/output/  │      │bulletproof_loader│     │              │     │              │
│              │      │                  │     │   dim_*      │     │   ✓ 44 dims  │
│ dim_*.csv ───┼─────►│  1. Read CSV     │────►│   tables     │────►│   loaded     │
│ (44 files)   │      │  2. Validate     │     │              │     │              │
│              │      │  3. Batch (500)  │     └──────────────┘     └──────────────┘
└──────────────┘      │  4. Upsert       │
                      │                  │     ┌──────────────┐     ┌──────────────┐
┌──────────────┐      │  Error Handling: │     │              │     │              │
│              │      │  • Retry logic   │     │   fact_*     │     │   ✓ 51 facts │
│ fact_*.csv ──┼─────►│  • Batch rollback│────►│   tables     │────►│   loaded     │
│ (51 files)   │      │  • Detailed logs │     │              │     │              │
│              │      │                  │     └──────────────┘     └──────────────┘
└──────────────┘      │                  │
                      │  Modes:          │     ┌──────────────┐     ┌──────────────┐
┌──────────────┐      │  • upsert (safe) │     │              │     │              │
│              │      │  • replace (full)│     │   qa_*       │     │   ✓ 1 QA     │
│ qa_*.csv ────┼─────►│  • append (add)  │────►│   tables     │────►│   loaded     │
│ (1 file)     │      │                  │     │              │     │              │
└──────────────┘      └──────────────────┘     └──────────────┘     └──────────────┘
```

## 4. Table Relationships (Simplified)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              Core Table Relationships                                │
└─────────────────────────────────────────────────────────────────────────────────────┘

                                    ┌───────────────┐
                                    │  dim_player   │
                                    │  (337 rows)   │
                                    │───────────────│
                                    │ player_id PK  │
                                    │ player_name   │
                                    │ position      │
                                    │ jersey_number │
                                    │ primary_team  │──────┐
                                    └───────┬───────┘      │
                                            │              │
              ┌─────────────────────────────┼──────────────┼─────────────────────────┐
              │                             │              │                         │
              ▼                             ▼              ▼                         ▼
    ┌───────────────┐            ┌───────────────────┐  ┌───────────────┐  ┌───────────────┐
    │ dim_schedule  │            │fact_player_game_  │  │   dim_team    │  │  fact_events  │
    │ (562 rows)    │            │stats (107 rows)   │  │  (26 rows)    │  │ (5,833 rows)  │
    │───────────────│◄───────────│───────────────────│──│───────────────│  │───────────────│
    │ game_id PK    │            │ player_game_key PK│  │ team_id PK    │  │ event_key PK  │
    │ game_date     │            │ game_id FK        │  │ team_name     │  │ game_id FK    │
    │ home_team_id  │────┐       │ player_id FK      │  │ team_abbrev   │  │ event_player_1│
    │ away_team_id  │────┤       │ team_id FK        │  └───────────────┘  │ event_type_id │
    │ venue         │    │       │ goals             │                     │ event_detail  │
    └───────────────┘    │       │ assists           │                     │ period        │
                         │       │ points            │                     │ game_time     │
                         │       │ ... (317 cols)    │                     └───────────────┘
                         │       └───────────────────┘
                         │
                         └────────────────────────────────────────────────┐
                                                                          │
    ┌───────────────┐            ┌───────────────────┐            ┌───────▼───────┐
    │  fact_shifts  │            │    fact_h2h       │            │dim_event_type │
    │  (672 rows)   │            │   (matchups)      │            │ (codes)       │
    │───────────────│            │───────────────────│            │───────────────│
    │ shift_key PK  │            │ h2h_key PK        │            │ event_type_id │
    │ game_id FK    │            │ game_id FK        │            │ event_type    │
    │ player_id FK  │            │ player_1_id FK    │            │ description   │
    │ period        │            │ player_2_id FK    │            └───────────────┘
    │ start_time    │            │ toi_together      │
    │ end_time      │            │ goals_for         │
    │ duration      │            │ goals_against     │
    └───────────────┘            └───────────────────┘
```

## 5. Stats Calculation Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          Stats Calculation Pipeline                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘

    fact_events                 Aggregation                fact_player_game_stats
    ───────────                 ───────────                ──────────────────────

┌──────────────────┐       ┌──────────────────┐       ┌──────────────────────────────┐
│ Raw Events       │       │ GROUP BY         │       │ Final Stats (317 columns)   │
│                  │       │ game_id,         │       │                              │
│ • Shots          │──────►│ player_id        │──────►│ SCORING:                     │
│ • Passes         │       │                  │       │   goals, assists, points     │
│ • Goals          │       │ COUNT, SUM       │       │   primary_assists            │
│ • Faceoffs       │       │ AVG, etc.        │       │   secondary_assists          │
│ • Zone entries   │       └──────────────────┘       │                              │
│ • Turnovers      │                                  │ SHOOTING:                    │
│ • etc.           │                                  │   shots, sog, shooting_pct   │
└──────────────────┘                                  │   shots_blocked, missed      │
                                                      │                              │
    fact_shifts                                       │ POSSESSION:                  │
    ───────────                                       │   corsi_for, corsi_against   │
                                                      │   fenwick_for, fenwick_agst  │
┌──────────────────┐       ┌──────────────────┐       │   cf_pct, ff_pct             │
│ Raw Shifts       │       │ TIME CALCULATIONS│       │                              │
│                  │       │                  │       │ TIME ON ICE:                 │
│ • Start time     │──────►│ SUM(duration)    │──────►│   toi_seconds, toi_minutes   │
│ • End time       │       │ COUNT(shifts)    │       │   shift_count, avg_shift     │
│ • Period         │       │ AVG(shift_len)   │       │   logical_shifts             │
│ • Player         │       └──────────────────┘       │                              │
└──────────────────┘                                  │ RATES (per 60):              │
                                                      │   goals_per_60, assists_per_60│
    Derived                                           │   points_per_60, shots_per_60│
    ───────                                           │                              │
                                                      │ MICRO STATS:                 │
┌──────────────────┐       ┌──────────────────┐       │   dekes, screens, backchecks │
│ Events + Shifts  │       │ WHILE ON ICE     │       │   forechecks, poke_checks    │
│ (merged)         │       │ CALCULATIONS     │       │   ... (70+ columns)          │
│                  │──────►│                  │──────►│                              │
│ • Who was on ice │       │ For each event,  │       │ COMPOSITE:                   │
│   during event?  │       │ attribute to     │       │   offensive_rating           │
│                  │       │ all players on   │       │   defensive_rating           │
└──────────────────┘       │ ice              │       │   two_way_rating             │
                           └──────────────────┘       │   impact_score, game_score   │
                                                      │   war_estimate               │
                                                      └──────────────────────────────┘
```

## 6. Loader Class Structure

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          bulletproof_loader.py Structure                             │
└─────────────────────────────────────────────────────────────────────────────────────┘

    class BulletproofLoader
    ─────────────────────────

    ┌─────────────────────────────────────────────────────────────────────────────────┐
    │ CONSTANTS                                                                        │
    ├─────────────────────────────────────────────────────────────────────────────────┤
    │ TABLE_DEFINITIONS: Dict[str, Dict]                                              │
    │   - 98 tables with explicit primary keys                                        │
    │   - Categories: dims, core, stats, analytics, zone, tracking, other, qa        │
    │                                                                                  │
    │ LOAD_ORDER: List[str]                                                           │
    │   - Dims first, then facts (respects FK dependencies)                          │
    └─────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────────────┐
    │ INITIALIZATION                                                                   │
    ├─────────────────────────────────────────────────────────────────────────────────┤
    │ __init__(data_dir, config_path)                                                 │
    │   └── _load_config() ──► Read config/config_local.ini                          │
    │   └── _connect() ──────► Create Supabase client                                │
    └─────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────────────┐
    │ CORE METHODS                                                                     │
    ├─────────────────────────────────────────────────────────────────────────────────┤
    │ load_table(table_name, mode)                                                    │
    │   ├── Read CSV                                                                  │
    │   ├── Validate schema                                                           │
    │   ├── Truncate if mode='replace'                                               │
    │   ├── Batch upsert (500 rows)                                                  │
    │   └── Return result dict                                                        │
    │                                                                                  │
    │ load_category(category, mode)                                                   │
    │   ├── Get tables for category                                                  │
    │   ├── Loop: load_table() for each                                              │
    │   └── Return aggregate results                                                  │
    │                                                                                  │
    │ load_missing(mode)                                                              │
    │   ├── Find empty tables                                                         │
    │   ├── Load only those                                                           │
    │   └── Return results                                                            │
    └─────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────────────┐
    │ UTILITY METHODS                                                                  │
    ├─────────────────────────────────────────────────────────────────────────────────┤
    │ get_table_count(table_name) ──► Query Supabase for row count                   │
    │ truncate_table(table_name) ───► Delete all rows using PK                       │
    │ get_csv_path(table_name) ─────► Return Path to CSV                             │
    │ read_csv(path) ───────────────► Parse CSV to List[Dict]                        │
    │ get_status() ─────────────────► Compare Supabase vs CSV counts                 │
    │ get_missing_tables() ─────────► List tables with 0 rows                        │
    └─────────────────────────────────────────────────────────────────────────────────┘
```

## 7. Test Coverage Map

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              Test Coverage Analysis                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘

    Component                    Unit Tests    Integration    Coverage
    ─────────                    ──────────    ───────────    ────────

    ┌──────────────────────┐
    │ Stats Calculations   │    ███████████   ░░░░░░░░░░░    ~80%
    │ (317 formulas)       │    (250+ tests)  (0 tests)
    └──────────────────────┘

    ┌──────────────────────┐
    │ Data Validation      │    ████░░░░░░░   ░░░░░░░░░░░    ~30%
    │ (type checks, FKs)   │    (6 tests)     (0 tests)
    └──────────────────────┘

    ┌──────────────────────┐
    │ ETL Pipeline         │    ██░░░░░░░░░   ░░░░░░░░░░░    ~15%
    │ (orchestrator)       │    (5 tests)     (0 tests)
    └──────────────────────┘

    ┌──────────────────────┐
    │ Supabase Loader      │    ░░░░░░░░░░░   ░░░░░░░░░░░    ~0%
    │ (bulletproof_loader) │    (0 tests)     (0 tests)
    └──────────────────────┘

    ┌──────────────────────┐
    │ Config Management    │    ████░░░░░░░   ░░░░░░░░░░░    ~30%
    │ (file loading)       │    (15 tests)    (0 tests)
    └──────────────────────┘

    ┌──────────────────────┐
    │ Error Handling       │    ░░░░░░░░░░░   ░░░░░░░░░░░    ~5%
    │ (edge cases)         │    (minimal)     (0 tests)
    └──────────────────────┘


    LEGEND:  ███ = Good coverage   ░░░ = Poor/no coverage


    PRIORITY TESTING NEEDS:
    ──────────────────────

    1. [HIGH] Supabase Loader
       - load_table() with various modes
       - Error handling for schema mismatches
       - Batch processing edge cases

    2. [HIGH] ETL Integration
       - End-to-end game processing
       - Multi-game batch processing
       - Failure recovery

    3. [MEDIUM] Data Validation
       - FK integrity checks
       - Required field validation
       - Type coercion edge cases

    4. [MEDIUM] Error Scenarios
       - Network failures
       - Malformed input files
       - Partial load recovery
```

