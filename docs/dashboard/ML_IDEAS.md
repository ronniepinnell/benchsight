# BenchSight Dashboard - ML Idea Bank

**Last Updated:** 2026-01-21  
**Status:** Draft (defense-focused)

## Purpose

Quick, implementable ML ideas that translate directly into dashboard insights and on-ice adjustments, with an emphasis on defensive play.

## Ideas

### 1) Gap Control vs. Entry Outcomes
- **Question:** How much does defender gap at the blue line change entry success and post-entry threat?
- **Data:** `fact_zone_entries`, `fact_events` (shots/xG/turnovers within 10–15s), `fact_shifts` (defender on-ice, speed if available).
- **Features:** Blue-line gap, lateral position (inside/outside dots), carrier speed, support count (friends vs. foes), handedness alignment, entry type (carry/chip/dump).
- **Label:** Entry result (denied/clean/carry-under-pressure) and downstream threat (xG or shot within 10–15s).
- **Model:** Gradient boosting or calibrated logistic regression for interpretability.
- **Dashboard Output:** Heatmap of optimal gap by carrier speed; rule cards (e.g., “<7 ft gap vs fast carriers → +12% xG against”).

### 2) Entry Denial Probability (Pre-Blue Line)
- **Question:** Given starting positions, what’s the probability the defender denies the entry?
- **Data:** `fact_zone_entries`, pre-entry defender position (from tracking or shift start), `fact_events`.
- **Features:** Defender inside/outside dots, stick lane angle (if tracked), defender vs. carrier speed delta, support distance to strong-side forward, bench side (for long change).
- **Label:** Denied vs. allowed.
- **Model:** XGBoost classifier with SHAP to expose cues.
- **Dashboard Output:** “Deny score” widget on game pages and coaching card with top 3 denial cues.

### 3) Retrieval → Exit Quality
- **Question:** Which retrieval patterns produce clean exits vs. turnovers?
- **Data:** `fact_events` (retrieval timestamp, exit outcome), `fact_zone_exits`, forecheck pressure tags if available.
- **Features:** Retrieval location (corner/half-wall/behind net), time-to-first-move, partner distance, wall option availability, pressure type (1-2-2, 1-1-3 if tagged).
- **Label:** Exit outcome (clean control / controlled fail / turnover / icing).
- **Model:** Gradient boosting; optionally sequence length-3 events for tempo.
- **Dashboard Output:** Suggested first-touch options by pressure type; “exit success by retrieval spot” chart for film review.

### 4) Slot Pass Suppression
- **Question:** How does body/stick positioning affect slot pass completion?
- **Data:** `fact_events` (passes into slot), defender position and stick angle if tracked.
- **Features:** Distance to passer, distance to slot, stick lane angle, inside/outside body position, goalie depth, man advantage state.
- **Label:** Slot pass completed vs. broken up/blocked.
- **Model:** Logistic regression with interaction terms for positioning; SHAP for cues.
- **Dashboard Output:** Completion probability grid; clip filters for “good lane vs. bad lane” teaching set.

### 5) PK Lane Coverage Archetypes
- **Question:** Which PK positioning templates suppress xG the best?
- **Data:** PK shifts from `fact_shifts`, `fact_events` (shots/xG), player locations if tracked.
- **Features:** Heatmap of defender locations during PK, distance between defenders, stick orientation buckets, clear attempts per shift.
- **Label:** xG/shot rate allowed per shift archetype.
- **Model:** Clustering (k-means or HDBSCAN) on positioning features → compare xG allowed per cluster.
- **Dashboard Output:** Archetype cards (“Passive box”, “Aggressive wedge”) with xG allowed deltas and recommended template per opponent.

### 6) Shooting Threat Map + Release Quality (Skaters)
- **Question:** Which skaters create high-threat shots by location, angle, and release speed?
- **Data:** `fact_shot_event` or `fact_events` with shot locations, shot type; goalie depth if present; shooter handedness from `dim_player`.
- **Features:** Shot location (xy, distance, angle), pre-shot movement (pass vs. carry, east-west distance), shot type, release time (event delta), game state (5v5/PP/PK), score/clock context.
- **Label:** Goal vs. no goal, xG bucket, rebound-generated (next event within 3s).
- **Model:** Gradient boosting or calibration model to refine xG; secondary model for rebound probability.
- **Dashboard Output:** Player “threat map” with zones of above/below expected finishing; quick cues on best release spots.

### 7) Goalie Rebound & Lateral Control
- **Question:** Which patterns drive rebound danger allowed by goalies?
- **Data:** `fact_goalie_game_stats` (rebound fields if present), `fact_saves`, `fact_shot_event` with pre/post coordinates, `fact_events` for follow-up shots.
- **Features:** Shot speed/type, pre-shot east-west movement, goalie depth, save type, traffic indicator, lateral distance to next shot.
- **Label:** Rebound allowed yes/no; rebound xG within 5s; goals off rebound.
- **Model:** Gradient boosting; SHAP for cues; cluster save contexts to coach positioning.
- **Dashboard Output:** Rebound heatmap by zone, “danger off rebounds” rate, drill list (e.g., east-west + tips).

### 8) Line Chemistry & WOWY Upside
- **Question:** Which line combos materially improve xG differential compared to parts?
- **Data:** `fact_line_combos`, `fact_wowy`, `fact_player_game_stats`, on-ice events from `fact_events`.
- **Features:** Usage (TOI, zone starts), opponent quality, score effects, entry/exit success while combo on-ice.
- **Label:** xG differential/60, goal differential/60, controlled entry rate, retrieval-to-exit success.
- **Model:** Ridge or Bayesian hierarchical to shrink small samples; clustering for similar combos.
- **Dashboard Output:** “Keep/Tweak/Split” recommendations per line; matchup suggestions by opponent forecheck style.

### 9) Power Play Entry & Set Efficiency
- **Question:** Which PP entry patterns lead to set possession and shots?
- **Data:** `fact_zone_entries` (strength state), `fact_events` (shots/xG within 20s), PP personnel from `fact_line_combos` or shift data.
- **Features:** Entry type (drop, bump, carry), carrier, support lane usage, gap pressure, entry side, handness mix.
- **Label:** Set possession achieved, time to first shot, PP xG/entry.
- **Model:** Sequence tree or gradient boosting; survival model for time-to-shot.
- **Dashboard Output:** PP entry report: success rates by play type, recommended carrier, clip filters for coaching.

### 10) PK Clear & Denial Efficiency
- **Question:** Which PK patterns clear fastest and suppress re-entries?
- **Data:** `fact_events` (loose puck, clear, dump), `fact_zone_entries` (opponent PP re-entry), `fact_shifts` for PK units.
- **Features:** Retrieval spot, touch count, glass vs. controlled clear, time-to-clear, unit personnel, pressure type.
- **Label:** Successful clear, time off clock, re-entry success on next attempt.
- **Model:** Gradient boosting or rules mining for simple cues.
- **Dashboard Output:** PK unit card with “time burned/clear”, recommended first-touch options under pressure.

### 11) Fatigue/Load Management
- **Question:** How does shift load impact performance late in shifts and later games?
- **Data:** `fact_shifts`, `fact_events` (turnovers, penalties, goals against), schedule density from `dim_schedule`.
- **Features:** Shift length, cumulative TOI in last 5/10 minutes, back-to-back flag, zone start, score state.
- **Label:** Negative events per 60 late in shift; success rates on exits/entries late in shift; injury/penalty proxies.
- **Model:** Survival/hazard for “bad event” risk over shift time; regression for performance drop.
- **Dashboard Output:** “Red zone” shift length per player, suggested deployment caps on back-to-backs.

### 12) Situational Faceoff Playbook
- **Question:** Which plays off the draw produce controlled exits/entries or shots?
- **Data:** `fact_faceoffs`, `fact_events` (first 10s after draw), handedness + deployment from `dim_player`, zone context.
- **Features:** Win/loss, set play type (if tagged), strong/weak side, opponent matchup, support positions.
- **Label:** Controlled exit/entry within 10s, shot/xG within 10s.
- **Model:** Association rules or gradient boosting; conditional probabilities by zone and handedness.
- **Dashboard Output:** Playbook tiles: “Strong-side chip vs. opponent X → +8% shot probability”; recommended centers/wingers by zone.

### 13) Penalty Risk & Discipline Tipping Points
- **Question:** When are we most likely to take minors, and which players/contexts spike risk?
- **Data:** `fact_events` (penalties, hits, stick infractions), `fact_shifts` (shift length, deployment), `dim_schedule` (back-to-back), opponent forecheck style if tagged.
- **Features:** Shift length, score/clock state, zone start, cumulative hits taken/given, opponent style, player penalty history.
- **Label:** Penalty taken in next 20–30s (yes/no, infraction type bucket).
- **Model:** Calibrated logistic or survival model; SHAP for cues.
- **Dashboard Output:** “Discipline risk” meter on bench view; per-player cue cards (e.g., “>55s D-zone shift + 1-goal lead → +14% trip/hook risk”).

### 14) Change Timing Risk (Odd-Man Rush Prevention)
- **Question:** Which change windows create rushes against, and how do we adjust deployment to avoid them?
- **Data:** `fact_shifts` (change timestamps, bench side), `fact_events` (rushes/goals within ±10s), `dim_schedule` (long-change periods).
- **Features:** Change timing vs. puck location, score state, period (long change), previous shift length, line combination.
- **Label:** Odd-man rush or goal against within 10s of change (yes/no).
- **Model:** Hazard model or gradient boosting; simple rules mined for coachability.
- **Dashboard Output:** “Safe change windows” by period/score; alerts for long-change danger; coaching note per line (e.g., “delay change if puck below hashmarks”).

### 15) Opponent-Specific Counterplays (Recipe Engine)
- **Question:** What repeatable counterplays work vs. specific opponent lines/players?
- **Data:** `fact_events` (entries/exits/plays by opponent player), `fact_line_combos`, `fact_zone_entries` (entry type), `fact_zone_exits`.
- **Features:** Opponent carrier patterns (preferred side, drop-pass frequency), support spacing, success vs. forecheck types, faceoff tendencies.
- **Label:** Success probability of counter (deny, turnover, forced dump) given pattern.
- **Model:** Sequence pattern mining + gradient boosting for conditional success; cluster opponent line archetypes.
- **Dashboard Output:** “Opponent recipes” cards (e.g., “vs Line A: angle to backhand, force rim → +11% dump rate”); pre-game scouting module.

### 16) Loose Puck Race Anticipation
- **Question:** How do starting position/angle/speed affect loose-puck win probability?
- **Data:** `fact_events` (loose puck recoveries), tracking-derived positions/speeds if available, `fact_shifts` for on-ice players.
- **Features:** Initial distance/angle to puck, speed delta, body orientation (if tracked), wall vs. open ice, man-advantage state.
- **Label:** Recovery win (yes/no) and time-to-win.
- **Model:** Gradient boosting; survival model for time-to-recovery; SHAP for coachable cues.
- **Dashboard Output:** “Win chance” grid by angle/speed; teaching clips for best approach angles; pre-set positioning tips on faceoffs and dump-ins.

### 17) Ice Tilt & Timeout Advisor
- **Question:** When is momentum swinging enough to justify a timeout or matchup change?
- **Data:** `fact_events` (shots, xG, hits, penalties), rolling xG/shot attempts, `fact_shifts` for deployment sequences.
- **Features:** Rolling xG differential, shot attempt bursts, zone time proxies, penalty pressure, goalie workload (shots in last 5m).
- **Label:** Goal against in next 2–4 minutes or high-danger sequence probability.
- **Model:** Time-series logistic/hazard; calibration for bench-readiness signal.
- **Dashboard Output:** Live “tilt meter” with suggested actions (timeout, change pairing, slow pace), surfaced on coaching/dashboard view.

### 18) Period Momentum Pulse
- **Question:** How fast is momentum shifting inside a period, and when should we slow/play fast?
- **Data:** `fact_events` (shots, xG, hits, takeaways, penalties), `fact_shifts` (deployment), game clock/score from `dim_schedule`.
- **Features:** 30–60s rolling xG differential, shot attempt bursts, hit/forecheck intensity proxies, faceoff win streak, rest differential (shift length history).
- **Label:** Probability of conceding/scoring in next 90–120s; swing magnitude bucket.
- **Model:** Sliding-window time-series logistic/hazard; smoothed for coachability.
- **Dashboard Output:** Period “pulse” strip showing surges/dips; micro-actions (“slow roll for 1 shift”, “push pace next shift”).

### 19) Live Win Probability (Beer-League Tuned)
- **Question:** What’s our in-game win probability with beer-league dynamics baked in?
- **Data:** `dim_schedule` (score/clock), `fact_events` (PP/PK, ENG, penalties), `fact_shifts` (goalie TOI, player fatigue), `fact_player_game_stats` (goalie strength, lineup quality).
- **Features:** Score/clock, manpower state, goalie fatigue proxy (shots faced last 5/10), bench shortness (missing skaters), back-to-back flag, pulled-goalie state.
- **Label:** Win/loss.
- **Model:** Gradient boosting or calibrated logistic updated in real time; optional Bayesian prior for short rosters.
- **Dashboard Output:** Live WP meter with “swing factors” (e.g., “down 1 but opponent short bench → +6%”); shareable win graph for fun.

### 20) Beer League Specials (Fun but Useful)
- **Late-Arrival Impact**
  - **Data:** Manual arrival timestamps per player (tiny form) + `fact_shifts` for deployment gaps.
  - **Features:** Missing first X shifts, late first shift performance, line scramble frequency.
  - **Label:** Goals/xG against in first 5 minutes; puck possession in first 3 shifts.
  - **Model:** Simple logistic/regression; rule cards.
  - **Dashboard Output:** “If Bob is late, start with conservative DZ faceoff set; add spare callout.”
- **Warmup Attendance Effect**
  - **Data:** Manual warmup attendance flag; `fact_events` first-period turnovers/penalties.
  - **Features:** Warmup flag, first 5 minutes TOI, first-touch turnovers.
  - **Label:** Early-period negative events.
  - **Model:** Logistic; CI bands for small N.
  - **Dashboard Output:** “No warmup → +9% early turnover risk; keep shifts short first 3 rotations.”
- **Bench Beer-to-Bite Correlation (tongue-in-cheek)**
  - **Data:** Self-reported post-game beer count; `fact_player_game_stats` next-game performance.
  - **Features:** Beer count, recovery days, back-to-back flag.
  - **Label:** Next-game points/xG, penalties.
  - **Model:** Regression with humor disclaimer.
  - **Dashboard Output:** “2 beers sweet spot; 5 beers → -12% xG next game (sample: small, fun only).”

### 21) Live Draft “Moneyball” (Rating Cap Solver)
- **Question:** Given rating caps (e.g., 1×6, 3×5s, 4×4s, 3×3s, 2×2s), which players maximize team value while fitting the constraint?
- **Data:** `dim_player` (rating 2–6, position), `fact_player_game_stats` (GAR/xG impact, TOI/usage), `fact_player_career_stats` (stability), `fact_line_combos` (chemistry hints), manual/imported scouting for new/unknown players (light EliteProspects scrape or manual entry fields: league, PPG, age, size).
- **Features:** Rating, position, handedness, primary role (scoring/transition/PK/faceoff), recent form, durability (games played), pace (shots/60), penalty risk, chemistry proxies with known teammates.
- **Label:** Draft value score (expected GAR/xG differential per game adjusted for league strength), role coverage completeness.
- **Model:** Constrained optimizer (ILP/knapsack) that fills required rating slots; Bayesian priors for players with low sample (borrow from league-strength-adjusted stats).
- **Dashboard Output:** “Best available” list filtered by remaining rating slots, positional needs, and role coverage; auto-updating draft board with projected team GAR and balance (scoring/transition/PK/goal prevention). Manual override field for unknown players.

### 22) Unknown/New Player Estimator
- **Question:** How do we rate unknown players quickly for draft/waiver decisions?
- **Data:** Minimal: age/height/weight/handedness, last league + PPG (manual entry), position; optional EliteProspects career line; `dim_player` for known comparables.
- **Features:** League strength multiplier, age curve adjustment, size/handedness rarity, position scarcity, comparables by style (shot volume, passing if any data), self-reported role.
- **Label:** Imputed rating (2–6) and projected GAR/xG differential with uncertainty band.
- **Model:** Bayesian regression with shrinkage to league baseline; similarity-weighted kNN to known players.
- **Dashboard Output:** Quick “slot” suggestion (e.g., “projected 4 with wide CI; treat as 3–5”) and recommended bid if using auction; feeds the draft optimizer.

### 23) Rating-Efficient Chemistry Builder
- **Question:** Which cheap (lower-rating) players unlock value when paired with specific higher-rating cores?
- **Data:** `fact_line_combos`, `fact_wowy`, `fact_player_game_stats` (on-ice xG +/-), `dim_player` (rating).
- **Features:** On-ice xG diff by combo, entry/exit success while combo on-ice, OZ/DZ start performance, handedness mix, forecheck/backcheck workload sharing.
- **Label:** Chemistry uplift (combo xG/60 minus weighted individual baselines).
- **Model:** Hierarchical shrinkage to handle small samples; uplift estimation per pair/line.
- **Dashboard Output:** “Value pairs” that make a 3-rated player play like a 4 when with a specific 5; draft board helper to target undervalued complements.

### 24) Role Coverage Scorecard (Draft & Season)
- **Question:** Are we covering essential roles within rating caps?
- **Data:** `fact_player_game_stats` (PK/PP usage, DZ/OZ starts), `fact_events` (retrievals, exits, entries), `dim_player` (position, rating).
- **Features:** PK prowess (GA/60 on-ice, deny rate), PP generation (xG/60 on-ice, shot assists), transition (entries/exits with control), faceoff specialty, physical pressure, penalty risk.
- **Label:** Role coverage flags (green/yellow/red) by slot (PPQB, bumper, F1 forechecker, PK wedge, shutdown pair).
- **Model:** Rule-based + percentile thresholds, optionally boosted for edge cases.
- **Dashboard Output:** Draft checklist showing which roles are filled by rating slot; “best available by missing role” with rating constraint filter.

### 25) Low-Sample Lift via Historical Context
- **Question:** For players with limited recent data, who boosted their output historically (linemates, goalie context, team strength)?
- **Data:** `fact_player_game_stats` (game-level G/A aggregates by season), `fact_line_combos` or approximated frequent teammates per game, `fact_team_game_stats` (team strength proxy), `fact_goalie_game_stats` (own/opp goalie quality), `dim_schedule` (season/league).
- **Features:** Frequent linemate IDs per season, team offense/defense strength (GF/GA/xG proxies), own goalie quality (support), opponent goalie quality, schedule strength; career stage (age/season count).
- **Label:** Goals/assists per game (by season/segment); uplift vs. baseline when paired with specific linemates or vs. weaker goalies.
- **Model:** Hierarchical/Bayesian regression with partial pooling to borrow strength from linemate and team-strength effects; shrink to league average when sparse.
- **Dashboard Output:** “Context card” for low-sample players: likely rating band, best-fit linemates based on past spikes, expected production vs. average/weak/strong goalies, and confidence interval. Feeds the draft optimizer with adjusted priors.

### 26) Sparse Data Partner/Uplift (No Line Combos)
- **Question:** With only game-level rosters and G/A, who tends to “travel with” a player when they produce?
- **Data:** `fact_player_game_stats` (game G/A), game roster membership per player/game, opponent goalie from `fact_goalie_game_stats`, team strength from `fact_team_game_stats`.
- **Features:** Co-presence counts (games played together), co-scoring lift = player G/A/game when teammate also dressed minus baseline, teammate assist share (teammate assists in player scoring games), opponent goalie quality bucket, team offense bucket.
- **Label:** Production lift when co-present vs. baseline (goals/game, primary points/game); uncertainty band for low counts.
- **Model:** Partial pooling on co-presence pairs (hierarchical); shrink small samples to team/league averages; simple rules for “boosters” (teammates whose assist share aligns with player’s scoring games).
- **Dashboard Output:** “Helpful partners” list for sparse players (e.g., “+0.18 G/game with Teammate X, low confidence”), context by goalie strength bucket, and suggested draft pairing even without true line data.

### 27) Unified Player Value Engine (Rich + Sparse + New)
- **Question:** How do we produce one coherent draft/value score combining rich-tracking players, sparse game-level players, and brand-new players?
- **Data:** Blend of all pipelines: rich stats (`fact_events`, `fact_zone_entries/exits`, `fact_line_combos`), game-level aggregates (`fact_player_game_stats`), roster-only co-presence, new-player priors (manual league/PPG, EliteProspects line), team/goalie strength (`fact_team_game_stats`, `fact_goalie_game_stats`).
- **Features:** Route-specific features (xG/on-ice for rich; G/A per game and co-presence lift for sparse; league-strength-adjusted PPG for new), rating/position/handedness, role coverage tags, uncertainty metrics per route.
- **Label:** Unified value target = expected GAR/xG differential per game with rating cap context; uncertainty band.
- **Model:** Mixture-of-experts or hierarchical Bayesian: expert_rich, expert_sparse, expert_new feed a meta-learner that weights by data availability/confidence; shrink to league baseline when low confidence. Constrained optimizer consumes the unified outputs for draft suggestions.
- **Dashboard Output:** Single “value + confidence” score per player, tagged with source route (rich/sparse/new) and top drivers; feeds best-available list under rating cap, and role coverage view.

### 28) Moneyball Offense/Defense Mix (Draft Optimizer Add-On)
- **Question:** Given rating caps, how do we maximize goal differential by mixing high-offense/high-allowed players with defensive stoppers?
- **Data:** `fact_player_game_stats` (GF, GA on-ice, goals/assists), `fact_team_game_stats` (team strength), `fact_goalie_game_stats` (support), `dim_player` (rating/position).
- **Features:** On-ice goals for/against per game (or per 60), individual scoring (G/A), penalty risk, deployment (OZ/DZ starts if available), opponent-strength adjusted splits.
- **Label:** Goal differential contribution per game (or per 60) with uncertainty.
- **Model:** Two-sides value (offense and defense) merged into goal-diff projection; constrained optimizer balances “scores a lot but gives up a lot” with “suppresses but low offense” to hit cap slots and role coverage.
- **Dashboard Output:** Draft board toggles for “maximize goal diff”, “maximize offense”, “lock defense”; highlights sneaky value (e.g., 3-rated who bleeds less GA to offset a leaky 5-rated scorer). Shows projected team goal diff under current selections and best-available recommendations.

### 29) Team Offense/Defense Impact via With/Without (No Shift Data)
- **Question:** How much does a player change team offense/defense when they dress, even without shift-level on-ice data?
- **Data:** `fact_player_game_stats` (presence + G/A), `fact_team_game_stats` (team GF/GA per game), `fact_goalie_game_stats` (goalie quality), `dim_schedule` (opponent/season).
- **Features:** Team GF/GA per game when player dressed vs. when absent (per season), opponent-strength buckets, goalie-strength buckets (own and opponent), sample size, player scoring (G/A) to separate personal offense from team effects.
- **Label:** With/without lift on team GF and GA per game (and per 60 proxy), season-level deltas with confidence intervals.
- **Model:** Hierarchical regression of team GF/GA on player presence + goalie quality + opponent quality; partial pooling by season to avoid overfitting sparse absences; report on/off effect sizes.
- **Dashboard Output:** “With/without impact” card: offensive lift and defensive lift with error bars; goalie support delta (team GA with/without player, adjusted for goalie); helps identify quiet defensive value players vs. high-event scorers. Feeds draft optimizer and role coverage.

## Comprehensive Interactive Model (How it fits together)
- **Pipelines (experts):**
  - Rich: tracking/events/entries/exits/line combos → xG/GAR-like estimates, chemistry.
  - Sparse: game-level G/A + co-presence → lifts and on/off goal diff.
  - New: league-strength-adjusted priors (manual + EliteProspects), age curve, similarity to known comps.
  - Context: moneyball goal-diff mix, with/without team GF/GA, goalie/opponent strength buckets.
- **Meta-model:** Mixture-of-experts or hierarchical weighting by data confidence (route tag + uncertainty). Outputs unified value (goal diff/GAR proxy) + offense/defense split + confidence.
- **Optimizers:** Constrained solver for rating caps and role coverage (PP/PK/transition/faceoff/defense). Toggles: maximize goal diff, maximize offense, lock defense, balance roles.
- **UI surfaces:** Draft board (best available with route tag and confidence), role coverage heatmap, chemistry/value pairs, “what-if” selections updating projected team goal diff/coverage, sparse/new player context cards, live “moneyball” sliders (offense/defense weight).
- **Data freshness:** Nightly rebuild of expert features; on-demand recalculation of optimizer when roster selections change; cache meta-model outputs with timestamps.

### 30) Opponent Draft Interest Predictor
- **Question:** Which players are other teams most likely to target given caps and needs?
- **Data:** Historical draft orders (if available), team rosters/holes, rating caps, positions already filled, perceived value scores from our model, simple heuristics (teams that favor offense vs. defense), schedule/attendance (who is present).
- **Features:** Team need vectors (roles missing, rating slots left), player value rank, scarcity of position/handedness, opponent tendencies (offense-heavy vs. defense-heavy past picks), attendance flags.
- **Label:** Pick probability per player per opponent pick slot; next-pick likelihood.
- **Model:** Heuristic + probabilistic choice model (e.g., Bradley-Terry or multinomial logit) seeded with our value scores, constrained by rating slots and role needs.
- **Dashboard Output:** “At risk” indicator on draft board (“Player X 48% likely to go in next 2 picks”), suggested reach/hold guidance, and simulated draft runs to stress-test your plan.

### 31) Keepers + Draft Simulation (With Last-Year Data)
- **Question:** How do keeper rules and historical draft behavior shift best-available and risk?
- **Data:** Last year’s draft order and picks, current keeper lists with ratings/positions, rating cap rules, team needs/holes, value scores from unified model.
- **Features:** Locked keeper value per team (rating slots consumed), remaining cap structure, historical tendencies (offense/defense bias, positional runs), scarcity by position/handedness, projected boards from unified model.
- **Label:** Simulated pick distributions and “at risk” probabilities conditioned on keepers.
- **Model:** Monte Carlo draft simulation with probabilistic choice (multinomial logit/Bradley-Terry) per pick, constrained by rating slots, roles, and keepers; incorporates last-year pick priors to bias tendencies.
- **Dashboard Output:** Live draft sim panel: who’s likely gone by your next pick, recommended reach/hold, and alternative plans if a run starts. Keeper summary table with remaining cap/roles per team.

### 32) Human Factors & Vibes Heuristics
- **Question:** How do we fold human signals (friend groups, locker-room fit, “fun to play with”) into draft risk?
- **Data:** Manual notes per team/player (friend groups, “fun”, captain preferences), past co-dressing frequency (from rosters), attendance/availability flags, last-year draft choices.
- **Features:** Friend-group proximity (players who dress together a lot), team-specific biases (offense-heavy, physicality, locker-room favorite tags), “fun” or chemistry notes, attendance reliability.
- **Label:** Soft prior: propensity score per team→player independent of pure value; adjust pick probability.
- **Model:** Heuristic overlay on the draft interest predictor: additive bump to pick probability when human heuristics align (e.g., friend-group + captain note). Optional lightweight Bayesian prior with manual weights.
- **Dashboard Output:** “Human bump” badge on draft board entries; sliders to weight human heuristics vs. model value; team profiles showing known biases (favor vibes vs. value). Helps explain reach picks and adjust risk flags.

### 33) Moneyball Draft Board & Counterfactuals (Fun Layer)
- **Question:** How do we make draft strategy playful and transparent while optimizing goal diff?
- **Data:** Unified value outputs (rich/sparse/new), rating caps, keepers, last-year draft order/picks, human/vibes notes.
- **Features:** Best-available by cap slots/roles, reach/hold risk, offense/defense sliders, human bump slider, counterfactual “what if we picked X one round earlier?” estimates on goal diff.
- **Label:** Projected team goal diff (and offense/defense splits) under current picks and counterfactual swaps.
- **Model:** Uses the existing optimizer + draft sim; counterfactual = re-run sim with altered pick and compute delta in projected goal diff.
- **Dashboard Output:** Live draft board with shareable “steal/whiff” badges, counterfactual graphs, and confidence bars so it stays light-hearted but informative.

## Integration Notes
- Prioritize ideas 1–2 for quickest value and easy dashboard surfacing (rule cards, probability widgets).
- Use MDX-enabled blog posts to narrate model findings and show reproducible charts.
- Log feature importance and calibration curves to keep coaching guidance explainable.
