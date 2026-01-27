# Appendix - Glossary

Quick reference for hockey terms, technical terms, and BenchSight-specific terminology.

---

## Hockey Analytics Terms

### Basic Stats

| Term | Definition |
|------|------------|
| **G (Goals)** | Pucks that cross the goal line |
| **A (Assists)** | Passes leading to goals (primary/secondary) |
| **Pts (Points)** | Goals + Assists |
| **SOG (Shots on Goal)** | Shots that would score if not saved |
| **S% (Shooting %)** | Goals / SOG × 100 |
| **TOI (Time on Ice)** | Total ice time in a game |
| **+/-** | Goals for minus goals against while on ice |

### Advanced Stats

| Term | Definition |
|------|------------|
| **Corsi** | Shot attempts (SOG + missed + blocked) |
| **CF (Corsi For)** | Shot attempts by player's team while on ice |
| **CA (Corsi Against)** | Shot attempts by opponent while on ice |
| **CF%** | CF / (CF + CA) × 100 |
| **Fenwick** | Unblocked shot attempts (SOG + missed) |
| **FF (Fenwick For)** | Unblocked attempts by team |
| **FA (Fenwick Against)** | Unblocked attempts by opponent |
| **FF%** | FF / (FF + FA) × 100 |

### Expected Goals (xG)

| Term | Definition |
|------|------------|
| **xG** | Expected goals - probability a shot becomes a goal |
| **xG For** | Sum of xG for player's shots |
| **xG Against** | Sum of xG for opponent shots while on ice |
| **Goals Above Expected** | Actual goals - xG |
| **Finishing** | Goals / xG (conversion rate) |

### WAR/GAR

| Term | Definition |
|------|------------|
| **GAR** | Goals Above Replacement |
| **WAR** | Wins Above Replacement (GAR / 4.5) |
| **Replacement Level** | Performance of freely available player |

### Quality Metrics

| Term | Definition |
|------|------------|
| **QoC** | Quality of Competition (avg opponent rating) |
| **QoT** | Quality of Teammates (avg linemate rating) |
| **Zone Starts** | Where shifts begin (O/N/D zone) |

### Zones

| Term | Definition |
|------|------------|
| **Offensive Zone (O)** | Attacking end of rink |
| **Defensive Zone (D)** | Defending end of rink |
| **Neutral Zone (N)** | Center ice between blue lines |
| **High Danger** | Crease/slot area |
| **Low Danger** | Perimeter shots |

### Game Situations

| Term | Definition |
|------|------------|
| **EV (Even Strength)** | 5v5 play |
| **PP (Power Play)** | Team has player advantage |
| **PK (Penalty Kill)** | Team is shorthanded |
| **EN (Empty Net)** | Goalie pulled |
| **4v4** | Both teams have one penalty |

---

## Technical Terms

### Data Engineering

| Term | Definition |
|------|------------|
| **ETL** | Extract, Transform, Load - data pipeline |
| **Dimension Table** | Lookup/reference table (dim_*) |
| **Fact Table** | Transactional data table (fact_*) |
| **Star Schema** | Dimension tables around central facts |
| **Grain** | Level of detail per row |
| **Foreign Key (FK)** | Reference to another table |
| **Primary Key (PK)** | Unique identifier for a row |

### Python/Pandas

| Term | Definition |
|------|------------|
| **DataFrame** | 2D labeled data structure |
| **Series** | 1D labeled array |
| **Vectorized** | Operations on entire columns (fast) |
| **iterrows()** | Row-by-row iteration (slow) |
| **groupby()** | Group data for aggregation |
| **merge()** | Join two DataFrames |

### Web Development

| Term | Definition |
|------|------------|
| **Next.js** | React framework for production |
| **App Router** | File-based routing in Next.js 13+ |
| **Server Component** | Renders on server (default) |
| **Client Component** | Renders in browser ('use client') |
| **TypeScript** | JavaScript with static types |
| **Tailwind CSS** | Utility-first CSS framework |

### API

| Term | Definition |
|------|------------|
| **REST** | Representational State Transfer |
| **FastAPI** | Python web framework |
| **Endpoint** | URL that accepts requests |
| **Pydantic** | Data validation library |
| **CORS** | Cross-Origin Resource Sharing |

### Database

| Term | Definition |
|------|------------|
| **PostgreSQL** | Relational database |
| **Supabase** | PostgreSQL hosting with API |
| **SQL** | Structured Query Language |
| **View** | Saved query (v_*) |
| **Index** | Speed up queries |

---

## BenchSight-Specific Terms

### Tables

| Prefix | Meaning | Example |
|--------|---------|---------|
| **dim_** | Dimension table | dim_player |
| **fact_** | Fact table | fact_events |
| **qa_** | QA/validation table | qa_goal_accuracy |
| **v_** | View | v_player_leaders |

### Keys

| Pattern | Meaning | Example |
|---------|---------|---------|
| **PG*** | Player-game key | PG19001P001 |
| **TG*** | Team-game key | TG19001T001 |
| **E*** | Event key | E19001_P2_0845_001 |
| **S*** | Shift key | S19001_P2_001 |

### Files

| File | Purpose |
|------|---------|
| **run_etl.py** | ETL entry point |
| **base_etl.py** | ETL orchestrator |
| **goals.py** | Goal counting (single source of truth) |
| **formulas.json** | Calculation weights |
| **BLB_Tables.xlsx** | League master data |

### Commands

| Command | Purpose |
|---------|---------|
| `./benchsight.sh etl run` | Run ETL |
| `./benchsight.sh etl run --wipe` | Clean + run ETL |
| `./benchsight.sh db upload` | Upload to database |
| `./benchsight.sh dashboard dev` | Start dashboard |
| `./benchsight.sh api dev` | Start API |

---

## Formulas Quick Reference

### Goal Counting
```
Goals = COUNT WHERE event_type='Goal' AND event_detail='Goal_Scored'
```

### Corsi
```
CF% = CF / (CF + CA) × 100
```

### xG
```
xG = base_rate × modifiers (capped at 0.95)
```

### WAR
```
WAR = GAR / 4.5
```

### Rate Stats
```
stat_per_60 = stat / toi_hours × 60
```

### Game Score
```
GS = scoring + shots + playmaking + defense + hustle + 2.0
```

---

## Danger Zones (XY)

| Zone | X Range | Y Range | xG Base |
|------|---------|---------|---------|
| High | ≥180 | 30-55 | 0.25 |
| Medium | ≥160 | 20-65 | 0.08 |
| Low | Everything else | - | 0.03 |

---

## Rating Scale

| Rating | Description | Expected GS |
|--------|-------------|-------------|
| 2 | Beginner | 2.3 |
| 3 | Developing | 3.5 |
| 4 | Average | 4.7 |
| 5 | Above Average | 5.9 |
| 6 | Elite | 7.1 |

---

## Further Reading

- **Project Docs:** `docs/MASTER_INDEX.md`
- **Data Dictionary:** `docs/data/DATA_DICTIONARY.md`
- **ETL Flow:** `docs/etl/CODE_FLOW_ETL.md`
- **This Walkthrough:** `docs/walkthrough/00-START-HERE.md`

---

*Last Updated: 2026-01-21*
