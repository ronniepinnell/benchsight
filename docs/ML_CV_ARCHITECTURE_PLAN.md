# ML/CV Architecture Plan - Hybrid Approach

**Planning for future ML/CV integration with Vercel frontend**

Last Updated: 2026-01-13  
Phase: 3 (Future Implementation)

---

## Executive Summary

**Vercel cannot host ML/CV workloads.** We'll use a **hybrid architecture**:
- **Frontend:** Vercel (Next.js dashboard) ✅ Current
- **ML/CV Service:** Separate platform (Replicate/RunPod/AWS)
- **Video Storage:** Cloudflare R2 or AWS S3
- **API Gateway:** Railway/Render (connects frontend to ML service)

---

## Why Hybrid Architecture?

### Vercel Limitations for ML/CV

❌ **No GPU access** - ML models need GPU for performance  
❌ **Time limits** - Edge Functions: 10s, Serverless: 60s  
❌ **No long-running processes** - Video processing takes minutes  
❌ **Limited memory/CPU** - Heavy compute not supported  
❌ **No video processing** - Cannot handle large file processing  

### What Vercel CAN Do

✅ **Frontend hosting** - Perfect for Next.js dashboard  
✅ **API gateway** - Lightweight API endpoints  
✅ **Edge functions** - Fast, lightweight processing  
✅ **CDN** - Global content delivery  

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER BROWSER                              │
└───────────────┬─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│              FRONTEND (Vercel)                               │
│  - Dashboard (Next.js)                                      │
│  - Tracker UI                                                │
│  - Admin Portal                                              │
└───────────────┬─────────────────────────────────────────────┘
                │
                │ HTTP/REST
                ▼
┌─────────────────────────────────────────────────────────────┐
│         API GATEWAY (Railway/Render)                        │
│  - REST API endpoints                                        │
│  - ETL triggers                                              │
│  - Game management                                            │
│  - ML/CV request routing                                     │
└───────────────┬─────────────────────────────────────────────┘
                │
                ├─────────────────┬─────────────────┬──────────┐
                ▼                 ▼                 ▼          ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐
    │   Supabase   │  │  ML Service  │  │  Video Store │  │  ETL     │
    │  (Database)  │  │  (Replicate/ │  │ (Cloudflare  │  │ Pipeline │
    │              │  │   RunPod)    │  │     R2)      │  │          │
    └──────────────┘  └──────────────┘  └──────────────┘  └──────────┘
```

---

## ML/CV Service Options

### Option 1: Replicate API (Recommended for MVP)

**Best for:** Quick integration, pay-per-use, no infrastructure management

**Pros:**
- ✅ Pre-built models (YOLO, video processing)
- ✅ Simple API integration
- ✅ Pay only for what you use
- ✅ No server management
- ✅ Fast setup (hours, not days)

**Cons:**
- ⚠️ Less control over models
- ⚠️ Can get expensive at scale
- ⚠️ Limited customization

**Cost:** $0.001-0.01 per request  
**Setup Time:** 2-4 hours  
**Best For:** MVP, proof of concept, rapid prototyping

**Example Integration:**
```python
# API Gateway (Railway) endpoint
import replicate

def process_video(video_url):
    output = replicate.run(
        "yolo-v8:latest",
        input={"video": video_url}
    )
    return output
```

---

### Option 2: RunPod / Vast.ai (Recommended for Custom Models)

**Best for:** Custom models, full control, cost-effective GPU

**Pros:**
- ✅ Full GPU access
- ✅ Custom model training
- ✅ Docker containers (easy deployment)
- ✅ Cost-effective ($0.20-2/hour)
- ✅ Full control

**Cons:**
- ⚠️ Requires infrastructure management
- ⚠️ Need to set up Docker
- ⚠️ More complex setup

**Cost:** $0.20-2/hour for GPU instance  
**Setup Time:** 1-2 days  
**Best For:** Custom models, production scale, full control

**Example Setup:**
```dockerfile
# Dockerfile for ML service
FROM pytorch/pytorch:latest
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]
```

---

### Option 3: AWS SageMaker (Enterprise)

**Best for:** Enterprise scale, full ML pipeline, compliance

**Pros:**
- ✅ Enterprise-grade
- ✅ Full ML pipeline (train, deploy, monitor)
- ✅ Auto-scaling
- ✅ Compliance ready
- ✅ Managed infrastructure

**Cons:**
- ⚠️ More expensive
- ⚠️ Steeper learning curve
- ⚠️ AWS ecosystem lock-in

**Cost:** $0.10-10/hour + storage  
**Setup Time:** 3-5 days  
**Best For:** Enterprise, large scale, compliance needs

---

## Video Storage Options

### Cloudflare R2 (Recommended)

**Why:**
- ✅ S3-compatible API
- ✅ **No egress fees** (unlike S3)
- ✅ $0.015/GB storage
- ✅ Fast global access
- ✅ Free tier: 10GB storage

**Cost:** ~$0-5/month (depending on usage)

### AWS S3

**Why:**
- ✅ Industry standard
- ✅ Reliable
- ✅ Good integration with AWS services

**Cost:** $0.023/GB storage + egress fees

### Supabase Storage

**Why:**
- ✅ Already using Supabase
- ✅ Included in free tier (1GB)

**Cost:** Free (1GB), then $0.021/GB

---

## Implementation Phases

### Phase 1: Current (Vercel Deployment) ✅

- **Frontend:** Vercel (Next.js dashboard)
- **Backend API:** Railway (ETL triggers)
- **Database:** Supabase
- **Status:** Ready to deploy

**Cost:** $5/month

---

### Phase 2: Add ML/CV Service (Future)

**Timeline:** Phase 3 of roadmap (Weeks 9-12)

**Steps:**
1. **Choose ML service** (Replicate for MVP, RunPod for custom)
2. **Set up video storage** (Cloudflare R2)
3. **Create API endpoints** (Railway API Gateway)
4. **Integrate with frontend** (Vercel dashboard)
5. **Test end-to-end** (video upload → processing → results)

**Architecture:**
```
Frontend (Vercel) 
  → API Gateway (Railway)
    → ML Service (Replicate/RunPod)
      → Video Storage (Cloudflare R2)
        → Results back to Supabase
```

**Cost:** $5/month (base) + ML service costs

---

### Phase 3: Scale ML/CV (Future)

**Timeline:** Phase 4+ (Weeks 13+)

**Enhancements:**
- Custom model training
- Real-time processing
- Batch processing pipeline
- Model versioning
- Performance monitoring

---

## Integration Pattern

### API Gateway Endpoint (Railway)

```python
# api/routes/ml.py
from fastapi import FastAPI, UploadFile
import replicate
import boto3  # For Cloudflare R2 (S3-compatible)

app = FastAPI()

@app.post("/api/ml/process-video")
async def process_video(file: UploadFile):
    # 1. Upload video to Cloudflare R2
    s3 = boto3.client('s3',
        endpoint_url='https://your-account.r2.cloudflarestorage.com',
        aws_access_key_id=os.getenv('R2_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('R2_SECRET_KEY')
    )
    
    video_url = upload_to_r2(file, s3)
    
    # 2. Process with ML service
    output = replicate.run(
        "yolo-v8:latest",
        input={"video": video_url}
    )
    
    # 3. Store results in Supabase
    store_results(output)
    
    return {"status": "success", "results": output}
```

### Frontend Integration (Vercel)

```typescript
// Dashboard component
async function processGameVideo(videoFile: File) {
  const formData = new FormData()
  formData.append('video', videoFile)
  
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/ml/process-video`,
    {
      method: 'POST',
      body: formData
    }
  )
  
  const results = await response.json()
  // Display results in dashboard
}
```

---

## Cost Estimates

### MVP (Replicate API)
- **Frontend:** Vercel Free
- **API Gateway:** Railway $5/month
- **ML Service:** Replicate $0.001-0.01/request
- **Video Storage:** Cloudflare R2 $0-5/month
- **Database:** Supabase Free
- **Total:** ~$5-15/month

### Production (RunPod GPU)
- **Frontend:** Vercel Free
- **API Gateway:** Railway $5/month
- **ML Service:** RunPod $0.20-2/hour (~$50-200/month)
- **Video Storage:** Cloudflare R2 $10-50/month
- **Database:** Supabase $25/month
- **Total:** ~$90-280/month

### Enterprise (AWS)
- **Frontend:** Vercel $20/month
- **API Gateway:** AWS API Gateway $3.50/month
- **ML Service:** SageMaker $100-500/month
- **Video Storage:** S3 $20-100/month
- **Database:** RDS $50-200/month
- **Total:** ~$200-800/month

---

## Migration Path

### Current → Phase 2 (Add ML)

1. **Deploy frontend to Vercel** ✅ (Current)
2. **Deploy API to Railway** ✅ (Current)
3. **Set up Cloudflare R2** (30 min)
4. **Integrate Replicate API** (2-4 hours)
5. **Test video processing** (1 hour)
6. **Deploy to production** (30 min)

**Total Time:** 1 day

### Phase 2 → Phase 3 (Scale)

1. **Migrate to RunPod** (if needed)
2. **Set up custom models** (1-2 days)
3. **Implement batch processing** (1 day)
4. **Add monitoring** (4 hours)

**Total Time:** 3-4 days

---

## Key Decisions

### ✅ Decision 1: Vercel for Frontend
**Rationale:** Perfect for Next.js, free tier, excellent DX  
**Status:** Implemented

### ✅ Decision 2: Hybrid Architecture
**Rationale:** Vercel cannot host ML/CV workloads  
**Status:** Planned for Phase 3

### ⏳ Decision 3: ML Service Choice
**Options:** Replicate (MVP) vs RunPod (Custom) vs AWS (Enterprise)  
**Timeline:** Decide in Phase 3  
**Recommendation:** Start with Replicate, migrate to RunPod if needed

### ⏳ Decision 4: Video Storage
**Options:** Cloudflare R2 vs AWS S3 vs Supabase Storage  
**Timeline:** Decide in Phase 3  
**Recommendation:** Cloudflare R2 (no egress fees)

---

## Success Criteria

### Phase 2 (ML Integration)
- [ ] Video upload works
- [ ] ML processing completes
- [ ] Results stored in Supabase
- [ ] Dashboard displays results
- [ ] End-to-end workflow functional

### Phase 3 (Scale)
- [ ] Custom models trained
- [ ] Batch processing works
- [ ] Real-time processing (if needed)
- [ ] Performance monitoring
- [ ] Cost optimized

---

## Notes for Implementation

### Important Considerations

1. **Video Size Limits**
   - Replicate: 100MB limit (may need chunking)
   - RunPod: No limit (depends on instance)
   - Consider compression before upload

2. **Processing Time**
   - Replicate: 30s - 5min per video
   - RunPod: Depends on model complexity
   - Implement async processing with job queue

3. **Error Handling**
   - ML services can fail
   - Implement retry logic
   - Store failed jobs for manual review

4. **Cost Management**
   - Monitor ML service usage
   - Set up alerts for high costs
   - Optimize model selection

5. **Security**
   - Secure API endpoints
   - Authenticate ML service calls
   - Protect video storage

---

## Resources

### Documentation
- **Replicate:** https://replicate.com/docs
- **RunPod:** https://docs.runpod.io
- **Cloudflare R2:** https://developers.cloudflare.com/r2
- **AWS SageMaker:** https://docs.aws.amazon.com/sagemaker

### Example Projects
- **YOLO Object Detection:** https://replicate.com/ultralytics/yolov8
- **Video Processing:** https://replicate.com/collections/video-processing
- **RunPod Templates:** https://www.runpod.io/templates

---

## Next Steps

1. ✅ **Deploy to Vercel** (Current - Phase 1)
2. ⏳ **Build API Gateway** (Phase 1 - Weeks 1-2)
3. ⏳ **Research ML services** (Phase 2 - Weeks 5-8)
4. ⏳ **Set up video storage** (Phase 3 - Week 9)
5. ⏳ **Integrate ML service** (Phase 3 - Weeks 9-12)
6. ⏳ **Test end-to-end** (Phase 3 - Week 12)

---

**Current Status:** Vercel deployment ready ✅  
**ML/CV Status:** Planned for Phase 3 (hybrid architecture)  
**Timeline:** Weeks 9-12 of roadmap

---

*Plan created: 2026-01-13*
