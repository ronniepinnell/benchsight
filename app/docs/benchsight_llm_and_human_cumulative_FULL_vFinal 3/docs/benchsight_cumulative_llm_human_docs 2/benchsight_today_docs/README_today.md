# BenchSight – Today's Design & Strategy Notes

Generated: 2025-12-26T19:10:59.636497 (UTC)

This bundle summarizes what we focused on **today** around the BenchSight / Beer League Beauties
project. It’s meant as a compact companion to the big “ultimate” project bundle.

## Main Themes Today

1. **Commercial framing** – how BenchSight could become a product
   - Target segments: beer league, junior, college, pro clubs.
   - Value props: better decisions (coaching, player development, GM), better stories (visuals, reports),
     and better experience (bench iPad / phone view, fan reports).

2. **Advanced stat and microstat catalog**
   - We extended the stats dictionary with:
     - play‑by‑play core (goals, shots, passes, turnovers, takeaways, faceoffs, penalties, blocks, hits, etc.)
     - on‑ice context (score, zone, manpower, shift IDs, line combos)
     - event chains & sequences (linked_event_id, sequence_index, play_index, counter‑rush tags)
     - rating‑aware context (teammate and opponent strength, matchups, quality of competition)
     - vision‑era stats (future: speed, routes, spacing, pressure, reaction time, etc.).

3. **Multi‑horizon roadmap**
   - Short term: “team & resume” – stable ETL, datamart, Power BI dashboards, simple Python dashboard.
   - Mid term: “bench tool” – real‑time(ish) tracking UI, video links, xy overlays, simple subscription product.
   - Long term: “vision platform” – auto‑tracking, xG/xPlay models, cross‑league benchmarking.

4. **Implementation hooks back into the existing project**
   - We focused on **designing stats and flows** so they can plug into your current
     Postgres + Python + Power BI stack, without rewriting the whole codebase today.

The rest of the files in this folder go deeper into stats, backlog, and how to talk about
the project with other LLMs, teammates, or coaches.
