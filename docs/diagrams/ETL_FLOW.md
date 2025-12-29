# BenchSight ETL Flow Diagram

## High-Level Data Flow

```mermaid
flowchart TB
    subgraph Sources["📥 SOURCE DATA"]
        BLB[("BLB_Tables.xlsx<br/>Master Data")]
        TRACK[("Game Tracking<br/>{game_id}_tracking.xlsx")]
        NORAD[("noradhockey.com<br/>Official Scores")]
    end

    subgraph ETL["⚙️ ETL PIPELINE"]
        direction TB
        E1["1. etl.py<br/>Load Dims & Base Facts"]
        E2["2. etl_orchestrator.py<br/>Build Advanced Facts"]
        E3["3. enhance_all_stats.py<br/>Add 317 Stat Columns"]
        E4["4. build_qa_facts.py<br/>QA & Monitoring"]
        
        E1 --> E2 --> E3 --> E4
    end

    subgraph Output["📤 OUTPUT"]
        DIM[("Dimension Tables<br/>25 tables")]
        FACT[("Fact Tables<br/>20 tables")]
        QA[("QA Tables<br/>3 tables")]
    end

    subgraph Validate["✅ VALIDATION"]
        V1["qa_dynamic.py<br/>17 tests"]
        V2["qa_comprehensive.py<br/>52 tests"]
        V3["test_validations.py<br/>54 tests"]
        V4["enhanced_validations.py<br/>8 tests"]
    end

    BLB --> E1
    TRACK --> E1
    NORAD -.->|"Verify Goals"| V1
    
    E4 --> DIM
    E4 --> FACT
    E4 --> QA
    
    DIM --> Validate
    FACT --> Validate
    QA --> Validate
```

## Detailed ETL Steps

```mermaid
flowchart LR
    subgraph Step1["Step 1: etl.py"]
        direction TB
        S1A["Load BLB_Tables.xlsx"]
        S1B["Process Dim Tables"]
        S1C["Load Tracking Files"]
        S1D["Build Base Facts"]
        S1A --> S1B --> S1C --> S1D
    end

    subgraph Step2["Step 2: etl_orchestrator.py"]
        direction TB
        S2A["Build fact_events"]
        S2B["Build fact_events_player"]
        S2C["Build fact_shifts_player"]
        S2D["Build fact_player_game_stats"]
        S2E["Build fact_h2h, wowy, combos"]
        S2A --> S2B --> S2C --> S2D --> S2E
    end

    subgraph Step3["Step 3: enhance_all_stats.py"]
        direction TB
        S3A["Add Corsi/Fenwick"]
        S3B["Add Per-60 Rates"]
        S3C["Add Game Score"]
        S3D["Add Rating Adjustments"]
        S3E["Add 317 Total Columns"]
        S3A --> S3B --> S3C --> S3D --> S3E
    end

    subgraph Step4["Step 4: build_qa_facts.py"]
        direction TB
        S4A["Build game_status"]
        S4B["Build suspicious_stats"]
        S4C["Build positions"]
        S4A --> S4B --> S4C
    end

    Step1 --> Step2 --> Step3 --> Step4
```

## Data Transformation Flow

```mermaid
flowchart TB
    subgraph Raw["RAW DATA"]
        R1["events sheet<br/>~3000 rows/game"]
        R2["shifts sheet<br/>~100 rows/game"]
        R3["game_rosters sheet"]
    end

    subgraph Transform["TRANSFORMATIONS"]
        T1["Normalize columns<br/>Type → event_type"]
        T2["Add keys<br/>12-char format"]
        T3["Join roster<br/>Add player_id"]
        T4["Calculate stats<br/>Goals, assists, TOI"]
        T5["Aggregate<br/>Player → Game"]
    end

    subgraph Output["FACT TABLES"]
        O1["fact_events_player<br/>11,635 rows"]
        O2["fact_shifts_player<br/>4,626 rows"]
        O3["fact_player_game_stats<br/>107 rows"]
    end

    R1 --> T1 --> T2 --> O1
    R2 --> T2 --> T3 --> O2
    R3 --> T3
    O1 --> T4 --> T5 --> O3
    O2 --> T4
```

## Validation Flow

```mermaid
flowchart LR
    subgraph Input["INPUT"]
        I1["fact_player_game_stats"]
        I2["dim_schedule"]
        I3["fact_events_player"]
    end

    subgraph Checks["VALIDATION CHECKS"]
        C1["Goal Verification<br/>vs noradhockey.com"]
        C2["Math Consistency<br/>Points = G + A"]
        C3["FK Integrity<br/>All IDs exist"]
        C4["Outlier Detection<br/>Z-score > 3"]
        C5["Aggregation<br/>Player sum = Game total"]
    end

    subgraph Output["OUTPUT"]
        O1["✅ 131 Tests Pass"]
        O2["📋 fact_suspicious_stats"]
        O3["📊 fact_game_status"]
    end

    I1 --> C1
    I2 --> C1
    I1 --> C2
    I1 --> C4
    I3 --> C3
    I1 --> C5

    C1 --> O1
    C2 --> O1
    C3 --> O1
    C4 --> O2
    C5 --> O3
```

## File Dependencies

```mermaid
flowchart TB
    subgraph Config["CONFIG"]
        CF1["config/settings.py"]
        CF2["config/table_config.json"]
    end

    subgraph Core["CORE ETL"]
        E1["etl.py"]
        E2["src/etl_orchestrator.py"]
        E3["src/enhance_all_stats.py"]
    end

    subgraph Support["SUPPORT MODULES"]
        S1["src/populate_all_fks_v2.py"]
        S2["src/final_stats_enhancement.py"]
        S3["src/create_additional_tables.py"]
    end

    subgraph QA["QA SCRIPTS"]
        Q1["scripts/qa_dynamic.py"]
        Q2["scripts/qa_comprehensive.py"]
        Q3["scripts/build_qa_facts.py"]
    end

    CF1 --> E1
    CF2 --> E2
    E1 --> E2
    E2 --> E3
    E2 --> S1
    E3 --> S2
    E3 --> S3
    E3 --> Q1
    E3 --> Q2
    E3 --> Q3
```

## Command Sequence

```bash
# FULL ETL PIPELINE (run in order)

# Step 1: Load dims and base facts from BLB_Tables.xlsx
python etl.py

# Step 2: Build advanced fact tables from tracking data  
python src/etl_orchestrator.py --all

# Step 3: Enhance with 317 stat columns
python src/enhance_all_stats.py

# Step 4: Build QA monitoring tables
python scripts/build_qa_facts.py

# Step 5: Run all validations (131 tests)
python scripts/qa_dynamic.py
python scripts/qa_comprehensive.py
python scripts/test_validations.py
python scripts/enhanced_validations.py
```

## Runtime Performance

| Step | Script | Time | Output |
|------|--------|------|--------|
| 1 | etl.py | ~8s | 25 dim tables |
| 2 | etl_orchestrator.py | ~15s | 16 fact tables |
| 3 | enhance_all_stats.py | ~5s | 317 columns |
| 4 | build_qa_facts.py | ~10s | 3 QA tables |
| 5 | All validations | ~5s | 131 tests |
| **Total** | | **~43s** | **45 tables** |
