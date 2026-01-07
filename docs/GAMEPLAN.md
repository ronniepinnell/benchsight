# BenchSight Development Gameplan

## Current State (January 2026)

### What's Working ✅
1. **Tracker v22** - Full-featured game tracking interface
   - 12 event types with keyboard shortcuts
   - 6+6 player slots per event
   - Puck XY tracking (10 points per event)
   - Player XY tracking
   - Net location picker for shots
   - Undo/redo with 50-step history
   - Import/export Excel
   - Supabase push/pull

2. **Dashboard v4** - NHL-style analytics
   - 6 views (Overview, Box Score, Shot Chart, Players, Advanced, H2H)
   - Team comparison bars
   - Shot chart with filtering
   - Player cards and stats

3. **Backend API** - tracker_api.py
   - CLI and HTTP endpoints
   - Full CRUD for tracking data
   - ETL trigger support

4. **Data Model** - 111 tables defined
   - Dimension tables for reference data
   - Fact tables for tracking data
   - XY coordinate tables (long and wide formats)

### What Needs Work ⚠️
1. **ETL Pipeline** - Previous developer deleted working code
   - Need to restore stat calculations
   - Aggregation pipelines incomplete
   - QA validation needs testing

2. **Data Accuracy** - Verify against ground truth
   - Goals must match noradhockey.com
   - Player stats need validation
   - XY data storage untested

3. **Linked Events** - Logic was lost
   - Shot → Save chains
   - Pass → Receive chains
   - Need to restore from specifications

---

## Priority 1: Immediate Testing (This Week)

### Day 1: Tracker Validation
```bash
# 1. Open tracker
open tracker/tracker_v22.html

# 2. Load game 18969 (has video, roster)
# 3. Track 5 test events with XY data
# 4. Push to Supabase
# 5. Verify data in Supabase dashboard
```

### Day 2: Dashboard Validation
```bash
# 1. Open dashboard
open dashboard/dashboard_v4.html

# 2. Load game 18969
# 3. Check all 6 views
# 4. Verify stats match tracker data
```

### Day 3: API Testing
```bash
# Test all API endpoints
python scripts/tracker_api.py --action list-games
python scripts/tracker_api.py --action get-game --game-id 18969
python scripts/tracker_api.py --action export-csv --game-id 18969
```

---

## Priority 2: ETL Restoration (Week 2)

### Step 1: Audit Current Tables
```python
# Check which tables have data
from scripts.tracker_api import TrackerAPI
api = TrackerAPI()

# List tables with row counts
for table in ['fact_events', 'fact_shifts', 'fact_player_game_stats']:
    data = api.client.table(table).select('*', count='exact').execute()
    print(f"{table}: {data.count} rows")
```

### Step 2: Restore Stat Calculations
Focus on these derived tables:
1. `fact_player_game_stats` - Per-game player stats
2. `fact_team_game_stats` - Per-game team stats
3. `fact_player_micro_stats` - Detailed micro-statistics
4. `fact_scoring_chances` - Scoring chance calculations

### Step 3: Implement QA Suite
```bash
# Run validation
python scripts/qa_comprehensive.py --game-id 18969

# Expected output:
# ✅ Goals match: 3-2 (noradhockey.com verified)
# ✅ Event count: 245 events
# ✅ Shift count: 42 shifts
# ⚠️ Missing XY data: 12 events
```

---

## Priority 3: Feature Completion (Week 3-4)

### Tracker Enhancements
- [ ] Video API integration (YouTube seek/play)
- [ ] Bulk event operations
- [ ] Event templates for common patterns
- [ ] Mobile-responsive layout

### Dashboard Enhancements
- [ ] Player radar charts (like Evolving Hockey)
- [ ] Line combination tool (like Natural Stat Trick)
- [ ] Expected Goals (xG) visualization
- [ ] Heat maps for shot/event density

### Analytics Features
- [ ] xG model implementation
- [ ] WAR calculations
- [ ] RAPM breakdowns
- [ ] Zone time analysis

---

## Priority 4: Production Polish (Week 5-6)

### Error Handling
- [ ] Graceful API failures
- [ ] Offline mode for tracker
- [ ] Conflict resolution for concurrent edits

### Performance
- [ ] Lazy loading for large datasets
- [ ] Pagination for event lists
- [ ] Caching for reference data

### Documentation
- [ ] User guide with screenshots
- [ ] Video tutorial for tracking workflow
- [ ] API documentation (OpenAPI spec)

---

## Technical Debt

### Code Quality
- [ ] Add TypeScript types to tracker
- [ ] Unit tests for API
- [ ] Integration tests for ETL

### Data Quality
- [ ] Implement data validation rules
- [ ] Add audit logging
- [ ] Create data lineage tracking

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Tracking time per game | 8 hours | 1-2 hours |
| Events tracked per game | ~200 | ~400+ |
| XY data coverage | 0% | 80%+ |
| Stat accuracy vs official | Unknown | 100% |
| Dashboard load time | 3-5s | <1s |

---

## Resources

### Reference Sites
- [Natural Stat Trick](https://naturalstattrick.com) - Clean data tables
- [Evolving Hockey](https://evolving-hockey.com) - Player radar charts
- [Money Puck](https://moneypuck.com) - xG models
- [Hockey Reference](https://hockey-reference.com) - Box scores

### Documentation
- `docs/README.md` - Project overview
- `docs/DATA_DICTIONARY.md` - Table definitions
- `docs/handoffs/` - Developer handoffs

### Key Files
- `tracker/tracker_v22.html` - Production tracker
- `dashboard/dashboard_v4.html` - Analytics dashboard
- `scripts/tracker_api.py` - Backend API
- `scripts/flexible_loader.py` - Data loader

---

## Contact

For questions or issues:
1. Check documentation first
2. Review code comments
3. Test with sample data
4. Document any bugs found

---

*Gameplan created: January 2026*
*Next review: After Phase 1 testing*
