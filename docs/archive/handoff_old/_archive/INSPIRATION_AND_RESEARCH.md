# BenchSight Inspiration & Research Links

## Analytics Websites

### Primary Inspiration Sources

| Site | URL | What to Learn |
|------|-----|---------------|
| **Evolving Hockey** | https://evolving-hockey.com | xG models, RAPM, player cards, WAR |
| **Money Puck** | https://moneypuck.com | Shot maps, game predictions, xG viz |
| **Natural Stat Trick** | https://naturalstattrick.com | On-ice stats, shift charts, line combos |
| **JFresh Hockey** | https://jfresh.substack.com | Player cards, team charts, visualization style |
| **All Three Zones** | https://allthreezones.com | Zone entries/exits, transition stats |
| **HockeyViz** | https://hockeyviz.com | Heat maps, shot location visualization |
| **Hockey-Reference** | https://hockey-reference.com | Historical stats, player pages |

### Tracking & Data Providers

| Resource | URL | Notes |
|----------|-----|-------|
| **NHL Edge** | https://www.nhl.com/stats/edge | Official NHL tracking data |
| **Sportlogiq** | https://sportlogiq.com | Pro tracking provider |
| **Big Data Cup** | https://www.stathletes.com/big-data-cup/ | Public tracking datasets for research |
| **InStat Hockey** | https://instatsport.com | European tracking provider |

### Design Inspiration

| Type | Examples | What to Emulate |
|------|----------|-----------------|
| **Game Summaries** | ESPN, NHL.com | Clean boxscore layout, key stats highlighted |
| **Player Cards** | NHL Edge, CapFriendly | Circular gauges, tier comparisons |
| **Shot Charts** | HockeyViz, Money Puck | Danger zones, shot density |
| **Line Combos** | Left Wing Lock, Daily Faceoff | Matrix views, TOI bars |
| **Team Dashboards** | The Athletic | Clean typography, narrative flow |

---

## Research Papers & Concepts

### xG (Expected Goals) Modeling

| Concept | Description | Implementation |
|---------|-------------|----------------|
| **Logistic Regression xG** | Basic model using shot distance/angle | Start here - simple and interpretable |
| **XGBoost xG** | Ensemble model with more features | Better accuracy, harder to explain |
| **Neural Network xG** | Deep learning approach | Best for large datasets |
| **Public xG Models** | MoneyPuck, Evolving-Hockey | Reference for calibration |

**Key xG Features:**
- Shot distance (ft from net)
- Shot angle (degrees from center)
- Shot type (wrist, slap, snap, backhand, tip)
- Rebound flag (shot within 3 sec of prior shot)
- Rush flag (shot within 4 sec of zone entry)
- Strength state (5v5, PP, PK)
- Score state (tied, up 1, down 1, etc.)
- Previous event type
- Time since last event

### RAPM (Regularized Adjusted Plus-Minus)

Ridge regression model that isolates player impact from teammates/opponents.

```
Goal Differential = Σ(player_on_ice * coefficient) + noise
```

### WAR (Wins Above Replacement)

Composite metric combining:
- Offensive contribution (xGF impact)
- Defensive contribution (xGA impact)
- Special teams value
- Replacement level baseline

### WOWY (With Or Without You)

Compare player performance with vs without specific teammates:
```
WOWY_GF_diff = GF%(with_teammate) - GF%(without_teammate)
```

---

## BLB-Specific Stats Ideas

### Rating-Aware Metrics (Unique to BenchSight)

Using the 2-6 player rating system:

| Stat | Description |
|------|-------------|
| **QoC Rating** | Avg rating of opponents faced |
| **QoT Rating** | Avg rating of linemates |
| **Rating-Adj +/-** | Plus/minus weighted by opponent quality |
| **Giveaways vs Elite** | Turnovers against 5+ rated players |
| **OZ Time vs Weak** | OZ possession vs lower-rated lines |

### Beer League Specific

| Stat | Why It Matters |
|------|----------------|
| **Shift Length** | Beer league shifts are often too long |
| **Faceoff Win %** | Often overlooked in rec leagues |
| **Bench Minor Rate** | Too many men penalties |
| **Sub Pattern** | Are players getting equal ice time? |
| **Fatigue Indicator** | Performance drop in late periods |

---

## Visualization Priorities

### Phase 1: Essential Views

1. **Game Summary (ESPN-style)**
   - Final score prominent
   - Period breakdown
   - Shot/goal totals
   - Key plays timeline

2. **Player Card (NHL Edge-style)**
   - Photo/jersey number
   - Key stats with league comparisons
   - Radar/spider chart for multi-dimensional view
   - Recent game log

3. **Shot Map**
   - Rink outline with shot locations
   - Color by goal/save/miss
   - Size by xG value

### Phase 2: Advanced Views

4. **Line Combo Matrix**
   - Rows = forward lines
   - Columns = D pairings
   - Cells = CF%, xGF%, TOI

5. **Shift Chart**
   - Timeline of who's on ice
   - Goals/shots overlaid
   - Period breaks marked

6. **WOWY Network**
   - Nodes = players
   - Edges = TOI together
   - Color = performance delta

### Phase 3: Pro Views

7. **Zone Entry Breakdown**
   - Controlled vs dump-in rates
   - Success by player
   - Location on ice

8. **Goalie Dashboard**
   - Save % by shot type
   - Net heatmap
   - Rebound/freeze rates

---

## Commercial Positioning

### Competitive Landscape

| Product | Target | Pricing | BenchSight Advantage |
|---------|--------|---------|---------------------|
| InStat | Pro/College | $$$$ | We focus on rec/junior |
| Hudl | Youth/HS | $$$ | More advanced stats |
| GameSheet | Admin/Scoring | $ | Analytics, not just scoring |
| Manual tracking | DIY | Free | Structured + automated |

### Value Proposition

**For Teams:**
- "Know your players like the pros do"
- Identify hidden gems and weak links
- Optimize line combinations

**For Leagues:**
- Engagement tool for players/fans
- Professional appearance
- Retention through gamification

**For Scouts:**
- Quantified player comparisons
- Exportable reports
- Video-linked highlights

---

## Links to Explore

### Twitter/X Accounts
- @EvolvingWild (Evolving Hockey)
- @JFaborsky (JFresh)
- @domluszczyszyn (Dom at The Athletic)
- @IneffectiveMath (HockeyViz)
- @CJTDevil (Corey Sznajder zone entries)

### Podcasts/Videos
- Evolving Hockey Podcast
- The Athletic Hockey Show
- Hockey PDOcast

### Courses/Learning
- MIT Sloan Sports Analytics Conference papers
- Stathletes webinars
- Hockey-Graphs tutorials

---

*Last Updated: December 2025*
*Maintained as part of BenchSight project*
