# Master Calculations & Implementation Plan (Advanced + Microstats)

**Purpose:** Master reference for microstat and advanced analytics calculations, data requirements, current BenchSight coverage, and the implementation path to reach NHL Edge / Sportlogiq / MoneyPuck / Evolving-Hockey parity. Sources: `docs/reference/inspiration/links.md`, research manuals, `BENCHSIGHT_CALCULATION_DEEP_DIVE_v34.md`, `BENCHSIGHT_DATA_DICTIONARY_v34.md`.

> **Note:** This document has been expanded with comprehensive reference documentation created in January 2026. For detailed formulas, code references, and implementation specifications, see:
>
> **Calculations:**
> - **[Calculation Catalog](calculations/CALCULATION_CATALOG.md)** - 50+ formulas with LaTeX notation and code references
> - **[WAR Methodology](calculations/WAR_METHODOLOGY.md)** - Deep dive on WAR/GAR vs. RAPM implementation
> - **[xG Model Specification](calculations/XG_MODEL_SPEC.md)** - Complete xG model specification (current vs. target)
>
> **Definitions & Standards:**
> - **[Canonical Definitions](definitions/CANONICAL_DEFINITIONS.md)** - Authoritative terminology (stint, rush, play, sequence, flurry, etc.)
>
> **Gap Analysis & Roadmap:**
> - **[NHL-Grade Benchmark](gaps/NHL_GRADE_BENCHMARK.md)** - Industry comparison vs. Evolving Hockey, MoneyPuck, NHL Edge, Sportslogiq
> - **[Implementation Priority](gaps/IMPLEMENTATION_PRIORITY.md)** - Prioritized backlog with dependency graph

---

## Current Coverage Snapshot
- **Implemented (BenchSight v34):** Corsi/Fenwick, basic xG lookup + heuristic/XY variant, rush detector (entry → shot within 5 events), zone entries/exits + summaries, shot chains, flurry detection placeholder (no probability adjustment), WAR/GAR with fixed weights (offense/defense/possession/transition/poise), goalie GAR (GSAx-style weights), game score, H2H/WOWY, QOC, shift analytics.
- **Planned/partial:** Royal Road/pass angle change (not implemented), flurry-adjusted xG, shooting talent adjustment, stint table + RAPM/WAR components, WDBE faceoffs, gap control, xT, spatial normalization, GBM xG, replacement level/daisy-chain priors.

---

## Microstat Calculations (what to ship)
| Metric | Current | Data Needed | Target Parity |
| --- | --- | --- | --- |
| Zone entries (type/outcome, shots/goals after) | ✅ | PBP; XY for entry point | Sportlogiq, NHL Edge |
| Zone exits (type/outcome, fails/icings) | ✅ | PBP; XY for exit point | Sportlogiq |
| Entry denials / forced dumps | ⚠️ outcomes only | Defender on-ice, entry outcomes; XY gap | Sportlogiq |
| Rush chances (entry → shot speed/odd-man) | ✅ basic | XY for speed/manpower angle | MoneyPuck rush models |
| Pre-shot movement (passes, royal road, east-west) | ❌ | Pass/shot linkage + XY + Δt | MoneyPuck, NHL Edge |
| Shot assists / secondary shot assists | ✅ counts | Pass→shot linkage, optional XY | Evolving-Hockey playmaking |
| Rebounds / flurries (probability-adjusted) | ⚠️ detect only | Shot grouping; flurry prob logic | MoneyPuck flurry xG |
| Net-drive / low-to-high / behind-net feeds | ❌ | Pass origin/target XY | Sportlogiq microstats |
| Slot/high-danger attempts | ✅ | Shot XY for slot polygon | NHL Edge danger |
| Cycle vs rush chains | ⚠️ rush only | Possession chains + XY/time | Sportlogiq |
| Forecheck pressures / dump recoveries | ❌ | Dump-in + first-touch + XY | Sportlogiq |
| Breakouts under pressure | ❌ | Exit events, pressure tags, XY | Sportlogiq |
| Turnovers (forced/unforced, zone) | ✅ basic | Better tagging | NHL Edge TO charts |
| Board battles / puck battles won | ❌ | Battle events + XY | Sportlogiq |
| Faceoff WDBE (clean/scrum + direction value) | ❌ | Faceoff dir vector, cleanliness, next-event | Sportlogiq WDBE |
| Gap control (static/effective) | ❌ | Player/puck XY @25Hz, velocity | NHL Edge tracking |
| Defensive touches / stick checks / lane blocks | ❌ | Tagged defensive events + XY lanes | Sportlogiq |
| Line change impacts / long shifts | ✅ | Shift data + event density | Internal |

---

## Advanced Stat Calculations
| Metric | Current | Data Needed | Target Parity |
| --- | --- | --- | --- |
| xG (GBM with spatial/context) | ⚠️ lookup/heuristic | XY normalized, pass/shot chain, shot type, speed, royal road | MoneyPuck, Evolving-Hockey |
| Flurry-adjusted xG | ❌ | Shot grouping, flurry logic | MoneyPuck |
| Shooting talent (finishing) | ❌ | Goals, shots, xG, shrinkage prior | Evolving-Hockey |
| xGF/xGA per 60 (score/venue/strength adj) | ✅ basic | Stronger context adj | NHL Edge |
| RAPM (6 components) | ❌ | Stints, sparse matrix, RidgeCV | Evolving-Hockey |
| WAR/GAR (replacement-level, priors) | ⚠️ weighted | RAPM outputs, replacement baseline, daisy-chain | Evolving-Hockey, TopDownHockey |
| Expected Threat (xT) | ❌ | XY grid, transition matrix, shots/goals by cell | Soccer xT adapted, Sportlogiq possession value |
| Entry/exit value models | ⚠️ counts | Transition probabilities, downstream outcomes | Sportlogiq |
| Faceoff WDBE EV | ❌ | Direction + next-event model | NHL faceoff research |
| Gap defense value | ❌ | Gap distance/velocity + entry outcomes | Sportlogiq |
| Goalie GSAx, rebound control, HD SV% | ⚠️ partial | Shot xG with spatial, rebound tagging | MoneyPuck goalie cards |

---

## Data & Feature Requirements
- **Baseline:** PBP + shifts with player roles, event types/details, strength, zone, timestamps; shot type; penalties; faceoffs; roster IDs.
- **Spatial:** XY for shots/passes/entries/exits, period-aware normalization, pass endpoints, puck & player velocity (tracking @25Hz).
- **Linkage:** play_key / sequence_key / shot chains for flurries and possession context.
- **Context:** score state, zone start, manpower, home/away, period, shot type, screen/deflection flags.
- **Models:** GBM (xG), RidgeCV (RAPM), Markov grid solver (xT), faceoff next-event models.

---

## Implementation Path (BenchSight → NHL Edge / Sportlogiq parity)
**Immediate (no XY dependency):**
- Flurry-adjusted xG in shot chains/scoring chances.
- WDBE v1 using event text (clean/scrum + approximate direction, next-event weighting).
- Stint schema + generator; design RAPM matrix encoding.
- WAR baseline update plan (replacement-level definition, goals-per-win = 6 for NHL).
- Glossary alignment + QA tests for xG modifier application.

**Short-Term (post-XY ingestion):**
- Coordinate normalization; shot distance/angle; royal-road/east-west and speed features.
- GBM xG training with calibration; model monitoring.
- Gap control v1 (static/effective gap on entries); puck/player speed.
- Entry/exit value models (shots/goal prob uplift).
- Shot/puck speed features; pass lanes (low-to-high, behind-net).

**Medium-Term:**
- RAPM (6 components) + WAR rebuild with replacement level and daisy-chain priors.
- Shooting talent adjustment (Bayesian shrinkage).
- xT grid model and player possession value credit.
- WDBE full (direction vectors + outcome EV).
- Defensive microstats (board battles, pressures, retrievals) if tagging or CV available.

---

## Deliverables to Generate
1) **XY Normalization + Stint Spec:** Schemas and ETL steps to produce normalized XY and stint table.  
2) **xG GBM Package:** Feature list, training pipeline, calibration checks, backtests vs lookup.  
3) **RAPM/WAR Package:** Design matrix builder, RidgeCV configs, replacement level math, priors.  
4) **xT & Possession Value:** Grid definition, transition estimation, player credit logic.  
5) **Microstat Suite:** WDBE, gap control, pre-shot movement, entry/exit value, flurry-adjusted xG.  
6) **Issue Backlog:** GitHub issue list for implementation (see `GITHUB_ISSUES_BACKLOG.md`).

---

## BenchSight Competitive Goal
- **Parity targets:** NHL Edge (speed, shot location, gap), Sportlogiq (microstat depth, possession value), MoneyPuck (xG/flurry/goalie cards), Evolving-Hockey (RAPM/WAR, shooting talent).  
- **Differentiators:** Transparent lineage (table-level), configurable models per league, open feature flags for rec/youth vs pro tuning, dashboard surfacing of microstats + possession value.  
- **Readiness checkpoints:** Calibrated xG, validated RAPM/WAR, xT in production, WDBE/gap live, dashboards exposing advanced layers.
