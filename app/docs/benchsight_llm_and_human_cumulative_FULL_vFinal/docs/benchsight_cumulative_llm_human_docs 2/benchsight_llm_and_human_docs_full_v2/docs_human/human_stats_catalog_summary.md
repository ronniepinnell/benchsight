# Human Summary – Stats & Microstats

This is a narrative summary of the stats catalog in `docs_llm/stats_catalog.csv`.

You can think of your stats in a few big buckets:

1. **Boxscore stats** – goals, assists, shots, penalties, TOI.
2. **Possession stats** – Corsi, Fenwick, shot attempts.
3. **Microstats** – controlled entries/exits, passes, turnovers, forecheck
   pressure, retrievals, etc.
4. **xG (expected goals)** – how dangerous shots are, regardless of
   whether they were scored.
5. **Rating context stats** – how a player does relative to the quality
   of teammates and opponents on the ice.
6. **Sequence/play stats** – rush vs cycle, length of sequences, outcomes
   of plays, counter-rush patterns.
7. **Video/XY-driven stats (future)** – speed, gap control, high-danger
   areas, etc.

For each stat in the catalog, you have:

- A clear name and short ID (e.g., `CORSI_FOR`, `MICRO_CONTROLLED_ENTRY`).
- A definition in words.
- A formula sketch (what to count or aggregate).
- A list of tables/columns needed.

This catalog is meant to be **living documentation**: as you (or an LLM)
add new metrics, they should be added here so everything stays consistent.
