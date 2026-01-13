# Phase 1 Quick Start Guide

**How to use Phase 1 implementation plans in future chats**

Last Updated: 2026-01-13

---

## 📋 Quick Reference

### When Starting a New Chat

```bash
# 1. Read the implementation plans
cat docs/PHASE1_ETL_API_PLAN.md
cat docs/ADMIN_PORTAL_SPEC.md

# 2. Check what's been done
grep -E "\[x\]|\[ \]" docs/PHASE1_ETL_API_PLAN.md | head -20
grep -E "\[x\]|\[ \]" docs/ADMIN_PORTAL_SPEC.md | head -20

# 3. Check current project state
ls -la api/ 2>/dev/null || echo "API not started yet"
ls -la ui/portal/js/ 2>/dev/null || echo "Portal JS not started yet"
```

---

## 🎯 How to Use These Plans

### 1. **Reference in Chat Prompts**

When starting a new chat, say:

```
"I'm working on Phase 1 of the ETL API. 
Please read docs/PHASE1_ETL_API_PLAN.md and help me with [specific task]."
```

Or:

```
"Following docs/ADMIN_PORTAL_SPEC.md, I need to connect the ETL trigger button.
What's the current state of the API integration?"
```

### 2. **Track Progress**

The plans have checkboxes. Update them as you complete tasks:

```markdown
# In PHASE1_ETL_API_PLAN.md
- [x] API runs locally          ← Mark done
- [ ] Health endpoint works     ← Still todo
- [ ] Can trigger ETL via API   ← Still todo
```

### 3. **Follow the Timeline**

Each plan has a day-by-day breakdown:

- **Week 1:** Core API structure
- **Week 2:** Advanced features & deployment

Check which day you're on and follow that section.

---

## 📁 File Structure to Build

### ETL API (`api/`)

```
api/
├── main.py                 # Start here (Day 1)
├── config.py
├── requirements.txt
├── routes/
│   ├── health.py          # Day 1
│   ├── etl.py             # Day 3-4
│   ├── games.py           # Day 5
│   └── upload.py          # Day 6-7
├── services/
│   ├── etl_service.py     # Day 3-4
│   ├── job_manager.py     # Day 3-4
│   └── supabase_service.py # Day 6-7
└── tests/
    └── test_etl_api.py    # Day 10
```

### Admin Portal (`ui/portal/js/`)

```
ui/portal/js/
├── config.js              # Day 1
├── api.js                  # Day 1
├── etl.js                  # Day 1-2
├── games.js                # Day 3
├── status.js               # Day 4
└── auth.js                 # Day 5
```

---

## 🔄 Development Workflow

### Step 1: Start with API

```bash
# Create API directory
mkdir -p api/{routes,services,models,utils,tests}

# Initialize FastAPI
cd api
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install fastapi uvicorn pydantic

# Create main.py (copy from plan)
# Test it
uvicorn main:app --reload
```

### Step 2: Test Each Endpoint

```bash
# Health check
curl http://localhost:8000/api/health

# Trigger ETL (after implementing)
curl -X POST http://localhost:8000/api/etl/trigger \
  -H "Content-Type: application/json" \
  -d '{"mode": "full"}'
```

### Step 3: Connect Portal

```bash
# Update ui/portal/js/config.js with API URL
# Add api.js client
# Connect buttons in etl.js
# Test in browser
```

---

## ✅ Progress Checklist

### Week 1: Core API

- [ ] **Day 1-2:** Setup & Basic Endpoints
  - [ ] Create `api/` structure
  - [ ] FastAPI app running
  - [ ] Health endpoint works
  - [ ] Status endpoint works

- [ ] **Day 3-4:** ETL Integration
  - [ ] ETL service wrapper created
  - [ ] Job manager working
  - [ ] Can trigger ETL via API
  - [ ] Job status tracking works

- [ ] **Day 5:** Game Management
  - [ ] Game endpoints created
  - [ ] Can list games
  - [ ] Can get game details

### Week 2: Advanced Features

- [ ] **Day 6-7:** Upload Integration
  - [ ] Upload service created
  - [ ] Can upload to Supabase via API
  - [ ] Upload progress tracking

- [ ] **Day 8-9:** Job Persistence
  - [ ] Jobs stored in database
  - [ ] Job history works
  - [ ] Logging implemented

- [ ] **Day 10:** Testing & Deployment
  - [ ] Tests written
  - [ ] Deployed to Railway/Render
  - [ ] End-to-end tested

### Admin Portal Integration

- [ ] **Day 1:** API Client
  - [ ] `api.js` created
  - [ ] Can make API calls

- [ ] **Day 2:** ETL Controls
  - [ ] Trigger button works
  - [ ] Status updates in real-time
  - [ ] Progress bar works

- [ ] **Day 3:** Game Management
  - [ ] Game list loads
  - [ ] Can trigger ETL for game

- [ ] **Day 4:** System Status
  - [ ] Status updates automatically
  - [ ] Stats display correctly

- [ ] **Day 5:** Authentication
  - [ ] Login works
  - [ ] Session persists

---

## 🐛 Common Issues & Solutions

### Issue: API can't import `run_etl.py`

**Solution:**
```python
# In api/services/etl_service.py
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from run_etl import run_full_etl
```

### Issue: CORS errors from portal

**Solution:**
```python
# In api/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Job status not updating

**Solution:**
- Check job manager is storing status
- Verify polling interval (2 seconds)
- Check browser console for errors

---

## 📝 Updating the Plans

As you implement, update the plans:

1. **Mark checkboxes complete:**
   ```markdown
   - [x] API runs locally  # Done!
   ```

2. **Add notes:**
   ```markdown
   - [x] Health endpoint works
     - Note: Added version endpoint too
   ```

3. **Document deviations:**
   ```markdown
   - [x] Job manager (used SQLite instead of in-memory)
   ```

---

## 🎯 Next Steps After Phase 1

Once Phase 1 is complete:

1. **Phase 2:** Dashboard polish & public launch
2. **Phase 3:** ML/CV integration
3. **Phase 4:** Commercial features

See `docs/STRATEGIC_ROADMAP.md` for full roadmap.

---

## 💡 Tips for Future Chats

### When Asking for Help

**Good prompts:**
- "Following `docs/PHASE1_ETL_API_PLAN.md` Day 3, I'm stuck on the ETL service wrapper. Help?"
- "I've completed the health endpoint. What's next in the plan?"
- "The job manager isn't tracking status. Check `api/services/job_manager.py`."

**Less helpful:**
- "Help with API" (too vague)
- "Fix my code" (no context)

### When Starting Fresh

1. Read the relevant plan section
2. Check what's already done
3. Ask: "What's the next step in the plan?"
4. Show current code if stuck

---

## 📚 Related Documents

- **`docs/PHASE1_ETL_API_PLAN.md`** - Full ETL API plan
- **`docs/ADMIN_PORTAL_SPEC.md`** - Full admin portal spec
- **`docs/STRATEGIC_ROADMAP.md`** - Overall roadmap
- **`docs/HANDOFF.md`** - General handoff guide

---

*Quick start guide created: 2026-01-13*
