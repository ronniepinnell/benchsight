# Human View – Flows & Schemas

This is a **human-readable** version of the flows and schemas.

Think of this as “how the data moves” and “how it’s organized” once it lands
in the database.

---

## 1. Data Flow in Plain English

1. **You track games.**
   - Either in the Excel tracker (like 18969_tracking) or in the new web tracker.
   - You record:
     - Shifts (who is on the ice, when, situation, zone, stoppages).
     - Events (passes, shots, goals, turnovers, entries/exits, etc.).
     - XY coordinates (where on the ice/net things happen).
     - Video times (so you can jump to a play on YouTube).

2. **Stage ETL loads that into Postgres.**
   - Each Excel tab → table in a **staging schema** (normalized column names).
   - Each CSV (XY, shots) → staging tables.
   - BLB_Tables (dim players, teams, games, etc.) → staging dims/facts.

3. **Intermediate transforms clean and enrich.**
   - Shifts:
     - Go from wide format (6 players in columns) to long format
       (1 row per player per logical shift).
     - Add shift numbers, cumulative shift counts, TOI, TOI excluding stoppages.
   - Events:
     - Go from long format (1 row per player-role) to a “wide” header
       (1 row per event with players pivoted into columns).
     - Link events into chains, sequences, and plays.
   - XY & rink coordinates:
     - Join XY points with rink and net coordinate dims to compute angles,
       distances, and zones.
   - Rating context:
     - Use player ratings from dim_players to compute average/min/max ratings
       of players involved in plays and on the ice.

4. **Mart ETL builds the final datamart.**
   - Fact tables for events, shifts, boxscore, sequences, etc.
   - Dimension tables for players, teams, games, dates, event types, zones,
     rink areas, etc.
   - These are designed so Power BI can **easily** slice and dice stats.

5. **Power BI and dashboards read from the datamart.**
   - Power BI uses CSVs exported from the datamart tables.
   - Python dashboards connect to Postgres directly or to those same CSVs.
   - ML notebooks use the same tables as a clean source.

---

## 2. Datamart in Words

You can think of the datamart like this:

- **Facts** (things that happened):
  - `fact_events` – every tracked event.
  - `fact_shifts` – every logical shift per player.
  - `fact_box_player` – player’s boxscore & microstats per game.
  - `fact_xg_shots` – one row per shot with xG and shot details.
  - `fact_sequences` / `fact_plays` – multi-event possessions and plays.

- **Dimensions** (things that describe facts):
  - `dim_players` – who.
  - `dim_teams` – which team.
  - `dim_games` – which game, date, home/away, tracking coverage.
  - `dim_dates` – calendar details.
  - `dim_event_types` – categories of events.
  - `dim_zones` / `dim_rink_areas` – where on the ice.

Each fact table has one clear “grain”, for example:

- `fact_events`: **one row = one event**.
- `fact_shifts`: **one row = one logical shift for one player**.
- `fact_box_player`: **one row = one player in one game**.

Knowing the grain is crucial for writing correct DAX and SQL.

---

## 3. How Schemas Help You Build Reports

Because of this structure, it’s easy to:

- Build **player game cards**:
  - Fact: `fact_box_player`
  - Dims: `dim_players`, `dim_teams`, `dim_games`
- Build **shift-level visuals** (TOI, deployment, fatigue):
  - Fact: `fact_shifts`
  - Join to `dim_players`, `dim_teams`, `dim_games`
- Build **shot maps and xG charts**:
  - Fact: `fact_xg_shots`
  - Join to `dim_players`, `dim_teams`, `dim_games`, `dim_zones`.

The detailed stats and formulas are cataloged in `stats_catalog.csv` and
summarized in the human stats summary doc.
