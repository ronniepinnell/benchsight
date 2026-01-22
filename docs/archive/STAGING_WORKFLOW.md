# Staging Data Workflow

**Cloud-based data ingestion: Upload → Staging → ETL → Mart**

---

## Overview

This document explains how to use the staging API to upload and update data without local files.

### Architecture

```
┌─────────────────┐
│   Data Source   │
│  (Excel/API)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Supabase       │
│  STAGING AREA   │
│  - stage_dim_*  │
│  - stage_*_*    │
└────────┬────────┘
         │
         │ ETL Reads
         ▼
┌─────────────────┐
│   ETL Pipeline  │
│   (Transform)   │
└────────┬────────┘
         │
         │ Writes
         ▼
┌─────────────────┐
│  Supabase       │
│  MART (Final)   │
│  - dim_*        │
│  - fact_*       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Dashboard     │
│   (Reads Mart)  │
└─────────────────┘
```

---

## Setup

### 1. Create Staging Tables

Run the staging table SQL in Supabase SQL Editor:

```bash
# The SQL file is at:
src/sql/supabase_staging_tables.sql
```

Or create tables manually using Supabase Dashboard.

### 2. Start the API

```bash
uvicorn api.main:app --reload --port 8000
```

---

## Updating BLB Tables

### Option 1: Upload from Excel File (Recommended)

**Step 1: Upload Excel Sheet to Staging**

```bash
# Using curl
curl -X POST http://localhost:8000/api/staging/blb-tables/upload \
  -H "Content-Type: application/json" \
  -d '{
    "table_name": "dim_player",
    "data": [...],  # Your table data as JSON array
    "replace": true
  }'
```

**Step 2: Run ETL (reads from staging)**

```bash
# ETL will read from staging tables instead of Excel
python run_etl.py --source supabase
```

### Option 2: Update Individual Rows

```bash
curl -X PUT http://localhost:8000/api/staging/blb-tables/update \
  -H "Content-Type: application/json" \
  -d '{
    "table_name": "dim_player",
    "filter_column": "player_id",
    "filter_value": "P001",
    "updates": {
      "first_name": "Johnny",
      "current_skill_rating": 85
    }
  }'
```

### Option 3: Replace Entire Table

```bash
# Clear table first
curl -X POST "http://localhost:8000/api/staging/blb-tables/dim_player/clear?confirm=true"

# Then upload new data
curl -X POST http://localhost:8000/api/staging/blb-tables/upload \
  -H "Content-Type: application/json" \
  -d '{
    "table_name": "dim_player",
    "data": [...],  # All new data
    "replace": true
  }'
```

---

## Uploading Tracking Data

### From Tracker

```bash
curl -X POST http://localhost:8000/api/staging/tracking/upload \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": 18969,
    "events": [
      {
        "tracking_event_index": "1",
        "period": "1",
        "Type": "Shot",
        "event_detail": "Wrist",
        "event_start_min": "10",
        "event_start_sec": "30"
      }
    ],
    "shifts": [
      {
        "shift_index": "1",
        "Period": "1",
        "shift_start_type": "Faceoff",
        "shift_start_min": "20",
        "shift_start_sec": "00"
      }
    ]
  }'
```

---

## Available BLB Tables

Get list of valid table names:

```bash
curl http://localhost:8000/api/staging/blb-tables/list
```

**Valid Tables:**
- `dim_player`, `dim_team`, `dim_league`, `dim_season`, `dim_schedule`
- `dim_event_type`, `dim_event_detail`, `dim_play_detail`
- `fact_gameroster`, `fact_leadership`, `fact_registration`, `fact_draft`

---

## Complete Workflow

### 1. Upload BLB Tables to Staging

```bash
# For each BLB table you want to update
curl -X POST http://localhost:8000/api/staging/blb-tables/upload \
  -H "Content-Type: application/json" \
  -d @dim_player.json  # Your table data
```

### 2. Upload Tracking Data (from Tracker)

```bash
curl -X POST http://localhost:8000/api/staging/tracking/upload \
  -H "Content-Type: application/json" \
  -d @tracking_data.json
```

### 3. Run ETL (reads from staging)

```bash
# ETL reads from Supabase staging tables
python run_etl.py --source supabase
```

### 4. Upload Results to Mart

```bash
# Upload final tables to Supabase
python upload.py
```

---

## Python Helper Script

For easier Excel uploads, you can create a helper script:

```python
# upload_blb_table.py
import requests
import pandas as pd

def upload_blb_table_from_excel(table_name: str, excel_path: str, replace: bool = False):
    """Upload BLB table from Excel to staging."""
    df = pd.read_excel(excel_path, sheet_name=table_name)
    data = df.to_dict(orient='records')
    
    response = requests.post(
        'http://localhost:8000/api/staging/blb-tables/upload',
        json={
            'table_name': table_name,
            'data': data,
            'replace': replace
        }
    )
    return response.json()

# Usage:
upload_blb_table_from_excel('dim_player', 'data/raw/BLB_Tables.xlsx', replace=True)
```

---

## Notes

- **Staging tables** are temporary - they hold raw data before ETL
- **Mart tables** (dim_*, fact_*) are final - they're what the dashboard reads
- **Replace mode**: Clears table before uploading (use with caution)
- **Update mode**: Updates matching rows only
- **Large tables**: For very large tables, consider using SQL `TRUNCATE` directly in Supabase
