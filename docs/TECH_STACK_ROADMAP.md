# BenchSight Tech Stack Roadmap

**Current and future technology requirements, migration paths, and adoption strategies**

Last Updated: 2026-01-15  
Version: 1.0

---

## Overview

This document outlines the current tech stack, future requirements, and migration strategies for the BenchSight platform as it evolves from MVP to commercial SaaS.

---

## Current Tech Stack

### ETL Pipeline

**Languages & Frameworks:**
- Python 3.11+
- Pandas (data processing)
- NumPy (numerical operations)
- OpenPyXL (Excel file handling)

**Key Libraries:**
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `openpyxl` - Excel file reading/writing
- `pathlib` - File path handling
- `logging` - Logging framework

**Infrastructure:**
- Local file system (CSV output)
- Supabase (PostgreSQL database)

### Dashboard

**Languages & Frameworks:**
- Next.js 14 (React framework)
- TypeScript
- Tailwind CSS (styling)
- shadcn/ui (UI components)
- Recharts (charting)

**Key Libraries:**
- `next` - React framework
- `react` - UI library
- `typescript` - Type safety
- `tailwindcss` - CSS framework
- `@radix-ui/*` - UI primitives (via shadcn)
- `recharts` - Chart library
- `@supabase/supabase-js` - Database client

**Infrastructure:**
- Vercel (hosting)
- Supabase (database)

### API

**Languages & Frameworks:**
- Python 3.11+
- FastAPI (web framework)
- Pydantic (data validation)

**Key Libraries:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `python-dotenv` - Environment variables
- `supabase` - Database client

**Infrastructure:**
- Railway/Render (hosting)
- Supabase (database)

### Tracker (Current)

**Languages & Frameworks:**
- HTML5
- JavaScript (vanilla)
- Excel export (SheetJS)

**Infrastructure:**
- Local storage (browser)
- File system (Excel export)

### Database

**Current:**
- Supabase (PostgreSQL)
- Row-level security (RLS) - planned

**Storage:**
- Local file system (CSV files)
- Supabase (production database)

---

## Future Tech Stack Requirements

### ML/CV Integration (Phase 6)

**Video Processing:**
- **FFmpeg** - Video transcoding and processing
- **OpenCV** - Computer vision operations
- **Python 3.11+** - ML/CV pipeline

**ML Frameworks:**
- **PyTorch** - Deep learning models
  - Goal detection models
  - Player identification models
  - Event classification models
- **TensorFlow** (optional) - Alternative ML framework
- **YOLO** - Object detection (goals, players, puck)
- **ResNet** - Image classification

**ML Infrastructure:**
- **GPU Support** - For model training/inference
  - AWS EC2 (g4dn instances)
  - Google Cloud (GPU instances)
  - Local GPU (development)
- **Model Storage** - S3/Cloudflare R2
- **Model Serving** - FastAPI endpoints

**Video Storage:**
- **S3/Cloudflare R2** - Video file storage
- **CDN** - Video delivery (Cloudflare)
- **Transcoding** - FFmpeg for multiple formats

**Migration Path:**
1. Set up video processing service (Week 25)
2. Integrate FFmpeg for transcoding
3. Set up GPU infrastructure for training
4. Train initial models (goal detection)
5. Deploy models to production API
6. Integrate with tracker

### Real-Time Features (Phase 7+)

**WebSocket Support:**
- **WebSockets** - Real-time communication
  - FastAPI WebSocket support
  - Next.js WebSocket client
- **Server-Sent Events (SSE)** - Alternative for one-way updates

**Message Queue:**
- **Redis** - Job queue and caching
  - Celery (Python task queue)
  - BullMQ (Node.js task queue) - if needed
- **RabbitMQ** (optional) - Alternative message broker

**Real-Time Infrastructure:**
- **WebSocket server** - FastAPI WebSocket endpoints
- **Redis pub/sub** - Real-time event broadcasting
- **Connection management** - Handle multiple connections

**Migration Path:**
1. Set up Redis instance
2. Add WebSocket support to FastAPI
3. Implement real-time updates for ETL status
4. Add real-time collaboration for tracker
5. Scale WebSocket infrastructure

### Scalability Infrastructure (Phase 7)

**Containerization:**
- **Docker** - Containerization
  - ETL service container
  - API service container
  - ML service container
- **Docker Compose** - Local development
- **Kubernetes** (future) - Container orchestration

**Orchestration:**
- **Kubernetes** - Container orchestration (future)
  - Auto-scaling
  - Load balancing
  - Service discovery
- **Helm** - Kubernetes package manager

**CDN:**
- **Cloudflare** - CDN for static assets
  - Dashboard assets
  - Video delivery
  - API caching

**Database Scaling:**
- **Read Replicas** - Supabase read replicas
- **Connection Pooling** - PgBouncer
- **Caching** - Redis for query caching

**Migration Path:**
1. Containerize services (Docker)
2. Set up CDN (Cloudflare)
3. Configure read replicas
4. Implement Redis caching
5. Set up Kubernetes (if needed)

### Monitoring & Observability (Phase 7)

**Metrics:**
- **Prometheus** - Metrics collection
- **Grafana** - Metrics visualization
- **Custom metrics** - Application-specific metrics

**Logging:**
- **Structured logging** - JSON logs
- **Log aggregation** - ELK stack or Datadog
- **Error tracking** - Sentry

**APM (Application Performance Monitoring):**
- **Datadog** (optional) - Full APM solution
- **New Relic** (optional) - Alternative APM
- **Custom dashboards** - Grafana

**Migration Path:**
1. Set up Prometheus
2. Add metrics to all services
3. Set up Grafana dashboards
4. Integrate Sentry for error tracking
5. Configure alerts

### Analytics & User Tracking (Phase 8)

**Product Analytics:**
- **Mixpanel** - User behavior tracking
- **Segment** - Event tracking and routing
- **PostHog** (optional) - Open-source alternative

**Business Analytics:**
- **Custom dashboards** - Internal analytics
- **Revenue tracking** - Stripe analytics
- **User metrics** - Custom SQL queries

**Migration Path:**
1. Set up Mixpanel/Segment
2. Add event tracking to dashboard
3. Add event tracking to portal
4. Create analytics dashboards
5. Set up revenue tracking

### Tracker Conversion (Phase 5)

**Backend:**
- **Rust** - High-performance backend
  - Actix Web - Web framework
  - SQLx - Database client
  - Serde - Serialization
  - Tokio - Async runtime

**Frontend:**
- **Next.js 14** - React framework (same as dashboard)
- **TypeScript** - Type safety
- **Zustand** - State management
- **React Query** - Data fetching

**Migration Path:**
1. Set up Rust project structure
2. Implement core API endpoints
3. Build Next.js frontend
4. Migrate HTML tracker features
5. Test feature parity
6. Deploy to production

---

## Migration Strategies

### ETL to Multi-Tenant

**Current:** Single-tenant (all data in one database)  
**Target:** Multi-tenant (tenant isolation via tenant_id)

**Strategy:**
1. Add `tenant_id` column to all tables
2. Update all queries to include `tenant_id` filter
3. Implement row-level security (RLS) policies
4. Migrate existing data (assign to default tenant)
5. Update ETL to accept `tenant_id` parameter

**Risks:**
- Data migration complexity
- Query performance impact
- Foreign key updates

**Mitigation:**
- Test migration on dev first
- Add indexes on `tenant_id`
- Update foreign keys carefully
- Rollback plan ready

### Single Database to Read Replicas

**Current:** Single Supabase instance  
**Target:** Primary + read replicas

**Strategy:**
1. Set up Supabase read replicas
2. Route read queries to replicas
3. Route write queries to primary
4. Monitor replica lag
5. Implement failover

**Risks:**
- Replica lag
- Connection management
- Failover complexity

**Mitigation:**
- Monitor replica lag
- Use connection pooling
- Test failover procedures

### Local Storage to Cloud Storage

**Current:** Local file system (CSV files)  
**Target:** S3/Cloudflare R2

**Strategy:**
1. Set up S3/R2 bucket
2. Create upload service
3. Migrate existing files
4. Update ETL to use cloud storage
5. Update API to serve from cloud

**Risks:**
- Migration time
- Cost implications
- Access control

**Mitigation:**
- Gradual migration
- Monitor costs
- Implement proper access controls

---

## Technology Adoption Timeline

### Phase 1-4 (Weeks 1-16): MVP
- ✅ Current stack (Python, Next.js, FastAPI, Supabase)
- ✅ No new technologies

### Phase 5 (Weeks 17-24): Tracker Conversion
- **Rust** - Backend development
- **Next.js** - Frontend (already in use)

### Phase 6 (Weeks 25-32): ML/CV Integration
- **PyTorch** - ML models
- **OpenCV** - Computer vision
- **FFmpeg** - Video processing
- **S3/R2** - Video storage

### Phase 7 (Weeks 33-40): Multi-Tenancy & Scale
- **Redis** - Caching and job queue
- **WebSockets** - Real-time features
- **Docker** - Containerization
- **Prometheus/Grafana** - Monitoring
- **Sentry** - Error tracking

### Phase 8 (Weeks 41-48): Commercial Launch
- **Stripe** - Payment processing
- **Mixpanel/Segment** - Analytics
- **CDN** - Cloudflare

---

## Risk Assessment

### High Risk Technologies

**Rust (Tracker Backend):**
- **Risk:** Learning curve, development time
- **Mitigation:** Start early, use existing patterns, extensive testing

**ML/CV Stack:**
- **Risk:** Complexity, GPU costs, model accuracy
- **Mitigation:** Start with simple models, use pre-trained models, gradual rollout

**Kubernetes:**
- **Risk:** Complexity, operational overhead
- **Mitigation:** Start with simpler solutions (Docker Compose), adopt Kubernetes only if needed

### Medium Risk Technologies

**Redis:**
- **Risk:** Additional infrastructure, cache invalidation complexity
- **Mitigation:** Start simple, use managed Redis, clear cache strategy

**WebSockets:**
- **Risk:** Connection management, scaling
- **Mitigation:** Use managed WebSocket service, implement connection limits

### Low Risk Technologies

**Docker:**
- **Risk:** Minimal - well-established
- **Mitigation:** Standard practices

**Prometheus/Grafana:**
- **Risk:** Minimal - standard tools
- **Mitigation:** Use managed services if available

---

## Cost Considerations

### Current Costs (MVP)
- **Supabase:** Free tier → Pro ($25/month)
- **Vercel:** Free tier → Pro ($20/month)
- **Railway/Render:** Free tier → Paid ($5-20/month)
- **Total:** ~$50-65/month

### Future Costs (Commercial)

**Infrastructure:**
- **Supabase:** Pro → Team ($599/month for 100+ teams)
- **Vercel:** Pro → Enterprise (custom pricing)
- **Railway/Render:** Paid plans ($50-200/month)
- **S3/R2:** Video storage (~$50-200/month)
- **Redis:** Managed Redis ($20-100/month)
- **GPU:** Training/inference (~$200-500/month)
- **Total:** ~$1,000-1,500/month (at scale)

**Third-Party Services:**
- **Stripe:** 2.9% + $0.30 per transaction
- **Sentry:** $26-80/month
- **Mixpanel:** $25-833/month (based on events)
- **Total:** Variable based on usage

---

## Decision Framework

### When to Adopt New Technology

**Adopt if:**
- Required for MVP feature
- Significantly improves performance
- Reduces operational complexity
- Industry standard for use case
- Well-documented and supported

**Defer if:**
- Can be achieved with current stack
- High learning curve
- Significant infrastructure cost
- Not critical for MVP
- Better alternatives may emerge

### Technology Evaluation Criteria

1. **Maturity:** Is it production-ready?
2. **Documentation:** Is it well-documented?
3. **Community:** Is there active community support?
4. **Performance:** Does it meet performance requirements?
5. **Cost:** Is it cost-effective?
6. **Learning Curve:** Can team adopt it quickly?
7. **Integration:** Does it integrate well with current stack?

---

## Related Documentation

- [MASTER_IMPLEMENTATION_PLAN.md](MASTER_IMPLEMENTATION_PLAN.md) - Implementation phases
- [MASTER_ROADMAP.md](MASTER_ROADMAP.md) - High-level roadmap
- [SCHEMA_SCALABILITY_DESIGN.md](data/SCHEMA_SCALABILITY_DESIGN.md) - Database scalability

---

*Last Updated: 2026-01-15*
