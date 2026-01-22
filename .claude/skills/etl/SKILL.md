---
name: etl
description: Run the BenchSight ETL pipeline to process hockey game data. Use when updating dashboard data, processing new games, or rebuilding the data warehouse.
allowed-tools: Bash, Read
argument-hint: [--games GAME_IDS] [--wipe]
---

# ETL Pipeline Execution

Process hockey game tracking data through the BenchSight ETL pipeline.

## Usage

Full pipeline (all games):
```bash
./benchsight.sh etl run
```

Specific games:
```bash
./benchsight.sh etl run --games 18969,18970
```

Clean slate + run:
```bash
./benchsight.sh etl run --wipe
```

## Pipeline Phases

1. **Loading**: Read Excel files from `data/input/`
2. **Event Building**: Construct event/shift sequences
3. **Calculations**: Compute goals, corsi, ratings, time stats
4. **Advanced Analytics**: Line combos, heat maps, advanced metrics
5. **Table Generation**: Create 139 tables (50 dim, 81 fact, 8 QA)
6. **Output**: CSVs to `data/output/`

## Performance Targets

- ETL runtime: < 90 seconds (4 games)
- Dashboard load: < 2 seconds
- API response: < 200ms

## After Running

ALWAYS run `/validate` to verify data quality.
