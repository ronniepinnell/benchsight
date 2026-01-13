# BenchSight Strategic Roadmap

**Path from Current State to Commercial Product**

Last Updated: 2026-01-13  
Version: 29.0  
Timeline: 16 weeks to commercial launch

---

## Vision Statement

**Build a full-stack hockey analytics platform that:**
1. Makes game tracking fast and easy (1 hour vs. 8 hours)
2. Provides comprehensive analytics for players, teams, and leagues
3. Automates tracking through ML/CV
4. Scales to commercial SaaS for junior hockey teams

---

## Current State Summary

### ✅ What Exists
- **ETL Pipeline:** 139 tables, validated, production-ready
- **Tracker Prototype:** Feature-rich HTML app (v23.5)
- **Dashboard Foundation:** Next.js app, connected to Supabase
- **Admin Portal UI:** Mockup exists
- **Documentation:** Comprehensive

### ❌ What's Missing
- **Backend API:** No way to trigger ETL from web
- **Integration:** Components don't talk to each other
- **Authentication:** No user management
- **ML/CV:** No automated tracking
- **Deployment:** Everything local
- **Multi-Tenancy:** Single league only

---

## Roadmap Overview

```
Phase 1: Integration (Weeks 1-4)    → End-to-end workflow
Phase 2: Dashboard (Weeks 5-8)     → Public-facing product
Phase 3: ML/CV (Weeks 9-12)        → Automated tracking
Phase 4: Commercial (Weeks 13-16)  → Multi-tenant SaaS
```

---

## Phase 1: Integration & Automation (Weeks 1-4)

**Goal:** Make existing components work together seamlessly

### Week 1-2: ETL API

**Objective:** Build REST API to trigger ETL from web

**Tasks:**
1. Create FastAPI backend (`api/` directory)
   - `/api/etl/trigger` - Start ETL job
   - `/api/etl/status/{job_id}` - Check status
   - `/api/etl/history` - Job history
   - `/api/games` - Game management
   - `/api/upload` - Trigger Supabase upload

2. ETL Job Queue
   - Use Celery or simple async queue
   - Background processing
   - Progress tracking
   - Error handling

3. Integration with existing ETL
   - Wrap `run_etl.py` in API
   - Support incremental ETL
   - Game-specific ETL

**Deliverables:**
- ✅ ETL API functional
- ✅ Can trigger ETL from HTTP request
- ✅ Status endpoints work
- ✅ Error handling robust

**Files to Create:**
```
api/
├── main.py              # FastAPI app
├── routes/
│   ├── etl.py          # ETL endpoints
│   ├── games.py         # Game management
│   └── upload.py        # Supabase upload
├── services/
│   ├── etl_service.py  # ETL orchestration
│   └── job_queue.py     # Job management
└── requirements.txt
```

### Week 2-3: Admin Portal Backend

**Objective:** Connect admin portal UI to backend

**Tasks:**
1. Connect UI to ETL API
   - Replace mock functions with real API calls
   - Add loading states
   - Error handling

2. Game Management
   - List games
   - Create new games
   - Update game status
   - Delete games

3. Basic Authentication
   - Simple password protection (MVP)
   - Session management
   - Admin role only (for now)

**Deliverables:**
- ✅ Admin portal functional
- ✅ Can trigger ETL from UI
- ✅ Game management works
- ✅ Basic auth implemented

**Files to Modify:**
```
ui/portal/
├── index.html           # Connect to API
├── js/
│   ├── api.js          # API client
│   ├── etl.js          # ETL controls
│   └── games.js        # Game management
```

### Week 3-4: Tracker Integration

**Objective:** Make tracker part of full stack

**Tasks:**
1. Cloud Persistence
   - Save tracking data to Supabase
   - Auto-save functionality
   - Load from cloud

2. Authentication
   - Login/logout
   - User session
   - Game access control

3. Real-time Sync
   - WebSocket or polling
   - Multi-user support (future)
   - Conflict resolution

**Deliverables:**
- ✅ Tracker saves to Supabase
- ✅ Can load games from cloud
- ✅ Authentication working
- ✅ Auto-save functional

**Files to Modify:**
```
ui/tracker/
├── tracker_index_v23.5.html  # Add cloud sync
└── js/
    ├── supabase.js           # Cloud client
    └── auth.js               # Authentication
```

**Phase 1 Success Criteria:**
- [ ] Track game → Click "Run ETL" → See stats in dashboard (< 5 min)
- [ ] Admin portal fully functional
- [ ] Tracker saves to cloud automatically
- [ ] End-to-end workflow works

---

## Phase 2: Dashboard & Polish (Weeks 5-8)

**Goal:** Production-ready public dashboard

### Week 5-6: Complete Dashboard Pages

**Objective:** Build all core dashboard features

**Tasks:**
1. Leaderboards
   - Points, goals, assists
   - Goalie stats
   - Advanced metrics

2. Player Profiles
   - Career stats
   - Game log
   - Trends/charts
   - Performance analysis

3. Team Pages
   - Roster
   - Season stats
   - Head-to-head
   - Schedule

4. Game Pages
   - Box score
   - Scoring summary
   - Shot chart
   - Play-by-play

5. Visualizations
   - Charts (Recharts)
   - Shot maps
   - Performance trends
   - Comparisons

**Deliverables:**
- ✅ All core pages functional
- ✅ Rich visualizations
- ✅ Responsive design
- ✅ Fast load times

### Week 6-7: Authentication & Roles

**Objective:** User management and access control

**Tasks:**
1. Supabase Auth Integration
   - Email/password
   - OAuth (optional)
   - Session management

2. Role-Based Access
   - Public (viewer)
   - Admin (full access)
   - Scorer (track games)
   - Team Manager (view team)

3. Protected Routes
   - Public pages (standings, leaders)
   - Protected pages (admin, tracker)
   - Role-based navigation

**Deliverables:**
- ✅ Authentication working
- ✅ Role-based access
- ✅ Protected routes
- ✅ User management UI

### Week 7-8: Deployment

**Objective:** Deploy to production

**Tasks:**
1. Vercel Deployment
   - Next.js dashboard
   - Environment variables
   - Domain setup

2. API Deployment
   - Railway or Render
   - Environment config
   - Health checks

3. Supabase Production
   - Production database
   - RLS policies
   - Backup strategy

4. Monitoring
   - Error tracking (Sentry)
   - Analytics
   - Uptime monitoring

**Deliverables:**
- ✅ Dashboard live on domain
- ✅ API accessible
- ✅ Production Supabase
- ✅ Monitoring in place

**Phase 2 Success Criteria:**
- [ ] Dashboard live and public
- [ ] All pages functional
- [ ] Authentication working
- [ ] Fast, responsive, polished

---

## Phase 3: ML/CV Foundation (Weeks 9-12)

**Goal:** Automated tracking foundation

### Week 9-10: Video Processing Pipeline

**Objective:** Build infrastructure for video analysis

**Tasks:**
1. Video Storage
   - Cloud storage (S3/Cloudflare R2)
   - Upload API
   - Video management

2. Frame Extraction
   - Extract frames from video
   - Multiple angles support
   - Frame labeling

3. Basic Object Detection
   - Puck detection
   - Player detection
   - Net detection
   - Simple tracking

**Deliverables:**
- ✅ Video upload/storage working
- ✅ Frame extraction pipeline
- ✅ Basic object detection

**Technology Stack:**
- **Computer Vision:** OpenCV, YOLO, or similar
- **Storage:** Cloudflare R2 or AWS S3
- **Processing:** Python backend or edge functions

### Week 10-11: Play Detection

**Objective:** Detect plays automatically

**Tasks:1. Shot Detection
   - Detect shots from video
   - Classify shot type
   - Track shot location

2. Goal Detection
   - Detect goals
   - Verify with multiple angles
   - Confidence scoring

3. Pass Detection
   - Detect passes
   - Track passer/receiver
   - Pass success/failure

4. Event Classification
   - Classify event types
   - Extract event details
   - Player attribution

**Deliverables:**
- ✅ Shot detection working
- ✅ Goal detection working
- ✅ Basic play detection
- ✅ Confidence scores

### Week 11-12: ML Integration

**Objective:** Integrate ML into tracker workflow

**Tasks:**
1. ML Suggestions in Tracker
   - Show ML-detected events
   - Human verification
   - Accept/reject workflow

2. Hybrid Tracking
   - ML suggests, human confirms
   - Learn from corrections
   - Improve over time

3. Confidence Scoring
   - Show confidence levels
   - Auto-accept high confidence
   - Flag low confidence for review

**Deliverables:**
- ✅ ML suggestions in tracker
- ✅ Human verification workflow
- ✅ Confidence scoring
- ✅ Learning from corrections

**Phase 3 Success Criteria:**
- [ ] ML detects 80%+ of shots correctly
- [ ] Tracking time reduced by 50%
- [ ] Human verification smooth
- [ ] System learns from corrections

---

## Phase 4: Commercialization (Weeks 13-16)

**Goal:** Multi-tenant SaaS ready for customers

### Week 13-14: Multi-Tenancy

**Objective:** Support multiple leagues

**Tasks:**
1. Tenant Architecture
   - League isolation
   - Data segregation
   - Tenant management

2. Tenant Management UI
   - Create leagues
   - Manage users
   - Billing integration

3. Tenant-Specific Features
   - Custom branding
   - League-specific rules
   - Custom reports

**Deliverables:**
- ✅ Multi-tenant architecture
- ✅ Tenant management UI
- ✅ Data isolation working

### Week 14-15: Advanced Features

**Objective:** Enterprise features

**Tasks:**
1. Advanced Analytics
   - Custom reports
   - Export functionality
   - API access

2. Team Management
   - Roster management
   - Player management
   - Season management

3. Communication
   - Email notifications
   - In-app messaging
   - Announcements

**Deliverables:**
- ✅ Advanced analytics
- ✅ Team management
- ✅ Communication features

### Week 15-16: Launch Prep

**Objective:** Ready for customers

**Tasks:**
1. Documentation
   - User guides
   - API documentation
   - Video tutorials

2. Onboarding
   - Welcome flow
   - Setup wizard
   - Training materials

3. Support System
   - Help center
   - Support tickets
   - FAQ

4. Marketing
   - Landing page
   - Pricing page
   - Demo videos

**Deliverables:**
- ✅ Complete documentation
- ✅ Onboarding flow
- ✅ Support system
- ✅ Marketing materials

**Phase 4 Success Criteria:**
- [ ] 3+ leagues using system
- [ ] Paying customers
- [ ] System stable at scale
- [ ] Support system functional

---

## Technology Stack Recommendations

### Backend API
- **Framework:** FastAPI (Python)
- **Job Queue:** Celery + Redis
- **Deployment:** Railway or Render
- **Database:** Supabase (PostgreSQL)

### Frontend
- **Dashboard:** Next.js 14 (already chosen)
- **Tracker:** Enhance existing HTML/JS or migrate to React
- **Admin Portal:** Enhance existing or migrate to Next.js

### ML/CV
- **Framework:** PyTorch or TensorFlow
- **Object Detection:** YOLO or similar
- **Video Processing:** OpenCV, FFmpeg
- **Storage:** Cloudflare R2 or AWS S3

### Infrastructure
- **Hosting:** Vercel (dashboard), Railway (API)
- **Database:** Supabase
- **Storage:** Cloudflare R2 or AWS S3
- **CDN:** Cloudflare
- **Monitoring:** Sentry, Vercel Analytics

---

## Risk Mitigation

### High-Risk Items

1. **ML/CV Complexity**
   - **Risk:** May be harder than expected
   - **Mitigation:** Start simple, iterate, consider external help
   - **Fallback:** Manual tracking remains primary

2. **Performance at Scale**
   - **Risk:** ETL may not scale
   - **Mitigation:** Optimize before scaling, use incremental ETL
   - **Fallback:** Batch processing, longer wait times

3. **Multi-Tenancy Complexity**
   - **Risk:** Architecture changes needed
   - **Mitigation:** Design for it early, implement later
   - **Fallback:** Single-tenant MVP first

4. **Video Storage Costs**
   - **Risk:** Multiple angles = high costs
   - **Mitigation:** Use cost-effective storage (Cloudflare R2)
   - **Fallback:** Compress videos, limit retention

---

## Success Metrics

### Phase 1 Metrics
- ETL trigger time: < 30 seconds
- End-to-end workflow: < 5 minutes
- Admin portal uptime: > 99%

### Phase 2 Metrics
- Dashboard load time: < 2 seconds
- Page views: Track usage
- User satisfaction: Survey

### Phase 3 Metrics
- ML accuracy: > 80% for shots
- Tracking time reduction: > 50%
- Human verification rate: < 20% need review

### Phase 4 Metrics
- Active leagues: 3+
- Paying customers: 5+
- System uptime: > 99.9%
- Customer satisfaction: > 4/5

---

## Dependencies & Prerequisites

### Phase 1 Prerequisites
- ✅ ETL pipeline working
- ✅ Supabase configured
- ✅ Tracker prototype functional

### Phase 2 Prerequisites
- ✅ Phase 1 complete
- ✅ Dashboard foundation built
- ✅ Design system established

### Phase 3 Prerequisites
- ✅ Phase 2 complete
- ✅ Video storage solution
- ✅ ML/CV expertise or resources

### Phase 4 Prerequisites
- ✅ Phase 3 complete
- ✅ Multi-tenant architecture designed
- ✅ Billing system selected

---

## Resource Requirements

### Development
- **Backend Developer:** API, ETL integration
- **Frontend Developer:** Dashboard, admin portal
- **ML/CV Engineer:** Video processing, object detection (Phase 3)
- **DevOps:** Deployment, infrastructure

### Infrastructure Costs (Monthly)
- **Vercel:** $0 (free tier) → $20 (pro)
- **Railway/Render:** $5-20 (API hosting)
- **Supabase:** $0 (free tier) → $25 (pro)
- **Storage (R2/S3):** $5-50 (depends on video volume)
- **Domain:** $12/year
- **Total:** ~$50-100/month (scales with usage)

---

## Next Steps (Immediate)

### This Week
1. **Decide on API framework** (FastAPI recommended)
2. **Set up API project structure**
3. **Create first endpoint** (health check)
4. **Test API deployment** (Railway/Render)

### Next Week
1. **Build ETL trigger endpoint**
2. **Test end-to-end** (tracker → API → ETL → dashboard)
3. **Document API**
4. **Plan admin portal integration**

---

## Questions to Answer

Before starting Phase 1, clarify:

1. **API Hosting:** Railway, Render, or other?
2. **Authentication:** Supabase Auth or custom?
3. **Video Storage:** Cloudflare R2, AWS S3, or other?
4. **ML/CV Timeline:** Is 4 weeks realistic, or need more time?
5. **Commercial Timeline:** Is 16 weeks realistic, or need to adjust?

---

*Roadmap created: 2026-01-13*  
*Next review: After Phase 1 completion*
