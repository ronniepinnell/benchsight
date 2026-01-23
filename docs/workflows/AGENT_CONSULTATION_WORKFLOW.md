# Agent Consultation Workflow

This document defines when and how to consult BenchSight's specialized agents during different types of work.

## Available BenchSight-Specific Agents

| Agent | Expertise | When to Consult |
|-------|-----------|-----------------|
| **hockey-analytics-sme** | Hockey stats, metrics, industry standards | Any stat calculation, metric design, dashboard feature |
| **etl-specialist** | ETL pipeline, phases, table creation | ETL bugs, new tables, performance issues |
| **data-dictionary-specialist** | Documentation, lineage, schema docs | After schema changes, new tables, deprecations |
| **supabase-specialist** | Database, views, RLS, performance | Query optimization, view design, migrations |
| **tracker-specialist** | Tracker app, export format, game tracking | Tracker features, export changes, data capture |
| **dashboard-developer** | Next.js dashboard, components, pages | Dashboard features, UI bugs, data fetching |

## Workflow by Task Type

### 1. Table/Schema Audits

**Required Agents:**
1. **hockey-analytics-sme** - Validate tables are analytically valuable
2. **etl-specialist** - Understand how tables are built, find duplicates
3. **data-dictionary-specialist** - Update documentation after changes

**Consultation Order:**
```
1. Discovery (explore codebase)
   ↓
2. hockey-analytics-sme: "Do we need these tables from an analytics perspective?"
   ↓
3. etl-specialist: "Why were these built? What breaks if removed?"
   ↓
4. Implementation decisions
   ↓
5. data-dictionary-specialist: "Update docs to reflect changes"
```

**Example Questions:**
- Hockey SME: "Is fact_shot_danger providing unique value vs fact_scoring_chances?"
- ETL: "Where is fact_h2h created and what downstream tables depend on it?"
- Data Dict: "What documentation needs updating after removing duplicates?"

---

### 2. New Table Creation

**Required Agents:**
1. **hockey-analytics-sme** - Define what metrics/columns are needed
2. **etl-specialist** - Design the builder function and ETL phase
3. **data-dictionary-specialist** - Document the new table

**Consultation Order:**
```
1. hockey-analytics-sme: "What columns/calculations does this table need?"
   ↓
2. etl-specialist: "Which phase? What's the source data?"
   ↓
3. Implementation
   ↓
4. data-dictionary-specialist: "Add to DATA_DICTIONARY.md"
```

---

### 3. Dashboard Feature Development

**Required Agents:**
1. **hockey-analytics-sme** - What metrics should be shown?
2. **supabase-specialist** - Optimal query/view design
3. **dashboard-developer** - Component implementation

**Consultation Order:**
```
1. hockey-analytics-sme: "What stats matter for this feature?"
   ↓
2. supabase-specialist: "Should we create a view? How to optimize?"
   ↓
3. dashboard-developer: "How to implement the component?"
```

---

### 4. Tracker Changes

**Required Agents:**
1. **tracker-specialist** - Understand current format, propose changes
2. **etl-specialist** - Ensure ETL can handle new/changed columns
3. **hockey-analytics-sme** - Validate new data capture is analytically useful

**Consultation Order:**
```
1. tracker-specialist: "What does current export look like?"
   ↓
2. hockey-analytics-sme: "Is this new data point valuable?"
   ↓
3. etl-specialist: "Can ETL handle this? What tables affected?"
   ↓
4. Implementation
```

---

### 5. ETL Bug Investigation

**Required Agents:**
1. **etl-specialist** - Debug the pipeline
2. **hockey-analytics-sme** - Validate expected calculations

**Consultation Order:**
```
1. etl-specialist: "Where is this calculated? What's the code path?"
   ↓
2. hockey-analytics-sme: "What SHOULD the calculation be?"
   ↓
3. Fix implementation
```

---

### 6. View Optimization

**Required Agents:**
1. **supabase-specialist** - Query/index optimization
2. **dashboard-developer** - How is the view used?

**Consultation Order:**
```
1. dashboard-developer: "How is this data fetched/used?"
   ↓
2. supabase-specialist: "How to optimize the query/view?"
```

---

### 7. Documentation Updates

**Required Agents:**
1. **data-dictionary-specialist** - Primary documentation owner
2. **etl-specialist** - For lineage tracing
3. **hockey-analytics-sme** - For metric definitions

**When to Update:**
- After any table creation/modification/deletion
- After view changes
- After calculation formula changes
- After tracker export changes

---

## Consultation Checklist

Before closing any table/schema related issue, verify:

- [ ] **hockey-analytics-sme** consulted on analytical value
- [ ] **etl-specialist** consulted on technical implementation
- [ ] **data-dictionary-specialist** updated documentation
- [ ] **supabase-specialist** consulted if views affected

Before closing any tracker-related issue, verify:

- [ ] **tracker-specialist** consulted on export format
- [ ] **etl-specialist** confirmed ETL handles changes
- [ ] Documentation updated

---

## Agent Invocation Examples

### Consulting Hockey Analytics SME

```
Use Task tool with subagent_type="hockey-analytics-sme"

Prompt: "We're considering removing fact_shot_danger and consolidating
into fact_scoring_chances. From a hockey analytics perspective:
1. Is danger_level vs danger_zone meaningfully different?
2. What fields are essential for shot quality analysis?
3. What do MoneyPuck/Natural Stat Trick use?"
```

### Consulting ETL Specialist

```
Use Task tool with subagent_type="etl-specialist"

Prompt: "fact_head_to_head has 835 rows, same as fact_h2h. Please:
1. Find where both are created in ETL phases
2. Check if any downstream tables depend on fact_head_to_head
3. Confirm if safe to delete"
```

### Consulting Data Dictionary Specialist

```
Use Task tool with subagent_type="data-dictionary-specialist"

Prompt: "We're removing fact_head_to_head (duplicate of fact_h2h). Please:
1. What sections of DATA_DICTIONARY.md need updating?
2. Should we create a DEPRECATED_TABLES.md?
3. Does SCHEMA_ERD.md need changes?"
```

---

## Skills Integration

These agents are also available via skills for common workflows:

| Skill | Invokes |
|-------|---------|
| `/hockey-stats` | hockey-analytics-sme |
| `/etl` | etl-specialist |
| `/db-dev` | supabase-specialist (dev environment) |
| `/db-prod` | supabase-specialist (prod environment) |
| `/tracker-dev` | tracker-specialist |
| `/dashboard-dev` | dashboard-developer |

---

## When NOT to Consult Agents

**Skip agent consultation for:**
- Simple typo fixes
- Comment/documentation-only changes (unless affecting DATA_DICTIONARY)
- UI styling changes with no data impact
- Test file changes

**Always consult agents for:**
- Any table creation/modification/deletion
- Any calculation formula changes
- Any column additions/removals
- Any view changes
- Any tracker export changes
