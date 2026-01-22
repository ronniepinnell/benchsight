# 14 - Making Changes Safely

**Learning Objectives:**
- Know how to add new stats, tables, and pages
- Understand the testing workflow
- Avoid common pitfalls

---

## Adding a New Stat

Let's add a new stat: **"Rebound Goals"** (goals scored on rebounds)

### Step 1: Define the Calculation

📍 **File:** `src/calculations/goals.py` (or new file)

```python
def count_rebound_goals(events_df: pd.DataFrame, player_id: str) -> int:
    """
    Count goals scored on rebounds.

    A rebound goal is a goal where:
    - event_type = 'Goal' AND event_detail = 'Goal_Scored'
    - is_rebound = True (set by tracker)
    """
    goals = filter_goals(events_df)
    player_goals = goals[goals['event_player_1'] == player_id]
    rebound_goals = player_goals[player_goals.get('is_rebound', False) == True]
    return len(rebound_goals)
```

### Step 2: Add to Player Stats

📍 **File:** `src/builders/player_stats.py`

```python
# In the PlayerStatsBuilder class or build function:

def build_player_game_stats(events_df, shifts_df, player_id, game_id):
    # ... existing stats ...

    # Add new stat
    stats['rebound_goals'] = count_rebound_goals(
        events_df[events_df['game_id'] == game_id],
        player_id
    )

    return stats
```

### Step 3: Run ETL and Verify

```bash
# Run ETL
./benchsight.sh etl run --wipe

# Check the new column exists
head -1 data/output/fact_player_game_stats.csv | tr ',' '\n' | grep rebound

# Check values
python -c "
import pandas as pd
df = pd.read_csv('data/output/fact_player_game_stats.csv')
print(df[['player_id', 'goals', 'rebound_goals']].head(10))
"
```

### Step 4: Upload and Display

```bash
# Upload to database
./benchsight.sh db upload
```

📍 **Dashboard:** `ui/dashboard/src/lib/supabase/queries/players.ts`

```typescript
export async function getPlayerStats(playerId: string) {
  const { data, error } = await supabase
    .from('fact_player_game_stats')
    .select('goals, assists, rebound_goals')  // Add new column
    .eq('player_id', playerId);

  return data;
}
```

📍 **Component:** `ui/dashboard/src/components/players/PlayerStats.tsx`

```typescript
<div>
  <p>Goals: {stats.goals}</p>
  <p>Rebound Goals: {stats.rebound_goals}</p>  {/* New stat */}
</div>
```

---

## Adding a New Table

Let's add: **`fact_power_play_summary`** (PP stats per game)

### Step 1: Create Builder

📍 **File:** `src/tables/remaining_facts.py` (or new file)

```python
def build_fact_power_play_summary(
    events_df: pd.DataFrame,
    shifts_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Build power play summary table.

    Grain: One row per (game_id, team_id)
    """
    # Filter to PP events
    pp_events = events_df[events_df['strength'].str.contains('PP', na=False)]

    # Aggregate
    summary = pp_events.groupby(['game_id', 'team_id']).agg({
        'event_id': 'count',
        'is_goal': 'sum',
        'is_shot_on_goal': 'sum',
    }).reset_index()

    # Rename columns
    summary = summary.rename(columns={
        'event_id': 'pp_events',
        'is_goal': 'pp_goals',
        'is_shot_on_goal': 'pp_shots',
    })

    # Calculate PP%
    # Need PP opportunities from penalties...
    # (simplified for example)

    return summary
```

### Step 2: Register in ETL

📍 **File:** `run_etl.py` (or `src/tables/remaining_facts.py`)

```python
# In the appropriate phase:
try:
    from src.tables.remaining_facts import build_fact_power_play_summary
    pp_summary = build_fact_power_play_summary(fact_events, fact_shifts)
    save_table(pp_summary, 'fact_power_play_summary')
    log("Power play summary complete")
except Exception as e:
    errors.append(f"PP summary: {e}")
```

### Step 3: Update Expected Count

📍 **File:** `run_etl.py`

```python
EXPECTED_TABLE_COUNT = 139  # Was 138, now 139
```

### Step 4: Run and Verify

```bash
./benchsight.sh etl run --wipe
./benchsight.sh etl validate

# Check new table
ls data/output/fact_power_play_summary.csv
head data/output/fact_power_play_summary.csv
```

---

## Adding a New Dashboard Page

Let's add: `/norad/power-play` page

### Step 1: Create Page

📍 **File:** `ui/dashboard/src/app/norad/power-play/page.tsx`

```typescript
import { getPowerPlayStats } from '@/lib/supabase/queries/power-play';
import { PowerPlayTable } from '@/components/teams/PowerPlayTable';

export default async function PowerPlayPage() {
  const stats = await getPowerPlayStats();

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-4">Power Play Analysis</h1>
      <PowerPlayTable data={stats} />
    </div>
  );
}
```

### Step 2: Create Query

📍 **File:** `ui/dashboard/src/lib/supabase/queries/power-play.ts`

```typescript
import { supabase } from '../client';

export async function getPowerPlayStats() {
  const { data, error } = await supabase
    .from('fact_power_play_summary')
    .select(`
      *,
      dim_team(team_name)
    `)
    .order('pp_goals', { ascending: false });

  if (error) throw error;
  return data;
}
```

### Step 3: Create Component

📍 **File:** `ui/dashboard/src/components/teams/PowerPlayTable.tsx`

```typescript
'use client';

interface Props {
  data: {
    game_id: number;
    team_id: string;
    pp_goals: number;
    pp_shots: number;
    dim_team: { team_name: string };
  }[];
}

export function PowerPlayTable({ data }: Props) {
  return (
    <table className="w-full">
      <thead>
        <tr>
          <th>Team</th>
          <th>PP Goals</th>
          <th>PP Shots</th>
        </tr>
      </thead>
      <tbody>
        {data.map((row, i) => (
          <tr key={i}>
            <td>{row.dim_team.team_name}</td>
            <td>{row.pp_goals}</td>
            <td>{row.pp_shots}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

### Step 4: Add Navigation

📍 **File:** `ui/dashboard/src/components/layout/Navigation.tsx`

```typescript
const navItems = [
  { href: '/norad/dashboard', label: 'Dashboard' },
  { href: '/norad/players', label: 'Players' },
  { href: '/norad/power-play', label: 'Power Play' },  // New link
];
```

---

## Modifying a Calculation

Let's change: **xG base rates**

### Step 1: Update Config

📍 **File:** `config/formulas.json`

```json
{
  "xg_base_rates": {
    "high_danger": 0.28,    // Was 0.25
    "medium_danger": 0.10,  // Was 0.08
    "low_danger": 0.04,     // Was 0.03
    "default": 0.07         // Was 0.06
  }
}
```

### Step 2: Verify Code Uses Config

📍 **File:** `src/calculations/xg.py`

```python
import json

def get_xg_base_rate(danger_level: str) -> float:
    with open('config/formulas.json') as f:
        formulas = json.load(f)
    return formulas['xg_base_rates'].get(danger_level, 0.06)
```

### Step 3: Re-run ETL

```bash
# Config change requires re-run
./benchsight.sh etl run --wipe
```

### Step 4: Verify Changes

```python
# Check that xG values changed
import pandas as pd
df = pd.read_csv('data/output/fact_player_game_stats.csv')
print(df['xg_for'].describe())
```

---

## Testing Workflow

### Before Making Changes

```bash
# 1. Note current state
ls data/output/*.csv | wc -l
python -c "import pandas as pd; df=pd.read_csv('data/output/fact_events.csv'); print(f'Goals: {len(df[df.is_goal])}')"

# 2. Create a backup (optional)
cp -r data/output data/output_backup
```

### After Making Changes

```bash
# 1. Run ETL with wipe
./benchsight.sh etl run --wipe

# 2. Validate
./benchsight.sh etl validate

# 3. Check specific values
python -c "
import pandas as pd
df = pd.read_csv('data/output/fact_player_game_stats.csv')
print('Columns:', len(df.columns))
print('Rows:', len(df))
print(df[['player_id', 'goals', 'xg_for']].head())
"

# 4. Compare to backup (if created)
diff <(head data/output/fact_events.csv) <(head data/output_backup/fact_events.csv)
```

### Running Tests

```bash
# Python tests
pytest tests/

# Specific test
pytest tests/test_goal_verification.py

# Dashboard tests
cd ui/dashboard
npm run lint
npm run type-check
```

---

## Common Pitfalls

### 1. Forgetting to Run ETL

**Symptom:** Dashboard shows old data
**Fix:** Run `./benchsight.sh etl run --wipe`

### 2. Forgetting to Upload

**Symptom:** CSV has new data, dashboard doesn't
**Fix:** Run `./benchsight.sh db upload`

### 3. Column Name Mismatch

**Symptom:** TypeError in dashboard
**Fix:** Ensure ETL column name matches dashboard query

```python
# ETL outputs 'rebound_goals'
stats['rebound_goals'] = ...

# Dashboard must use same name
.select('rebound_goals')  // Not 'reboundGoals'
```

### 4. Missing Dependency

**Symptom:** ETL phase fails
**Fix:** Check phase order - does this phase need earlier outputs?

```python
# WRONG: Using fact_player_game_stats before it's created
def phase_5():
    stats = pd.read_csv('data/output/fact_player_game_stats.csv')  # Doesn't exist yet!

# RIGHT: Move to later phase or create dependency
```

### 5. Breaking Existing Tests

**Symptom:** Tests fail after changes
**Fix:** Update tests to match new behavior

```python
# If you changed xG base rates:
def test_xg_calculation():
    # OLD: assert xg == 0.25
    # NEW: Update expected value
    assert xg == 0.28  # Updated base rate
```

---

## Checklist for Changes

### Adding a Stat
- [ ] Define calculation in `src/calculations/`
- [ ] Add to player_stats builder
- [ ] Run ETL with wipe
- [ ] Verify CSV has new column
- [ ] Upload to database
- [ ] Add to dashboard query
- [ ] Add to dashboard display

### Adding a Table
- [ ] Create builder function
- [ ] Register in ETL phase
- [ ] Update expected table count
- [ ] Run ETL with wipe
- [ ] Verify CSV exists
- [ ] Upload to database
- [ ] Create dashboard query (if needed)
- [ ] Create dashboard page (if needed)

### Modifying Calculations
- [ ] Update config or code
- [ ] Run ETL with wipe
- [ ] Verify values changed as expected
- [ ] Update tests if needed
- [ ] Upload to database

---

## Key Takeaways

1. **Always run ETL with `--wipe`** after code changes
2. **Follow the data flow:** ETL → CSV → DB → Dashboard
3. **Test incrementally:** Check each step works before moving on
4. **Use config files** for values that might change
5. **Keep tests passing** - update them when behavior changes

---

**Next:** [appendix-glossary.md](appendix-glossary.md) - Terms reference
