# ETL API Deployment Guide

Quick guide to deploy the BenchSight ETL API to Railway or Render.

## Prerequisites

- ETL API code in `api/` directory ✅
- Supabase credentials
- Railway or Render account

## Option 1: Railway (Recommended)

### Step 1: Install Railway CLI

```bash
npm i -g @railway/cli
```

### Step 2: Login

```bash
railway login
```

### Step 3: Initialize Project

```bash
cd api
railway init
```

Follow prompts:
- **Project name:** benchsight-api
- **Environment:** Production

### Step 4: Set Environment Variables

In Railway Dashboard → Variables, add:

```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=xxx
DATABASE_URL=postgresql://... (if using separate DB)
PYTHON_VERSION=3.11
```

### Step 5: Configure Build

Railway auto-detects Python, but verify:

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

### Step 6: Deploy

```bash
railway up
```

### Step 7: Get URL

Railway provides a URL like: `https://benchsight-api.railway.app`

Update your dashboard environment variable:
```
NEXT_PUBLIC_API_URL=https://benchsight-api.railway.app
```

---

## Option 2: Render

### Step 1: Create Web Service

1. Go to https://render.com
2. Click **New** → **Web Service**
3. Connect GitHub repository
4. Select repository

### Step 2: Configure Service

**Settings:**
- **Name:** benchsight-api
- **Environment:** Python 3
- **Root Directory:** `api`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Environment Variables

Add in Render Dashboard:

```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=xxx
PYTHON_VERSION=3.11
```

### Step 4: Deploy

Click **Create Web Service**

Render will:
1. Build the service
2. Deploy it
3. Provide URL: `https://benchsight-api.onrender.com`

### Step 5: Update Dashboard

Add to Vercel environment variables:
```
NEXT_PUBLIC_API_URL=https://benchsight-api.onrender.com
```

---

## Testing Deployment

### 1. Health Check

```bash
curl https://your-api-url.railway.app/api/health
```

Should return:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. API Docs

Visit: `https://your-api-url.railway.app/docs`

Should show Swagger UI with all endpoints.

### 3. Test from Admin Portal

1. Open admin portal: `/admin`
2. Try triggering an ETL job
3. Check API logs in Railway/Render dashboard

---

## Troubleshooting

### Build Fails

**Error: "Module not found"**
- Check `requirements.txt` includes all dependencies
- Verify Python version (3.11+)

**Error: "Import error"**
- Check `api/main.py` imports are correct
- Verify project structure

### API Not Responding

**Check logs:**
- Railway: Dashboard → Deployments → View Logs
- Render: Dashboard → Logs

**Common issues:**
- Port not set correctly (use `$PORT` environment variable)
- Environment variables missing
- CORS not configured

### CORS Errors

If admin portal can't connect:

1. Check `api/config.py` has correct CORS origins:
```python
CORS_ORIGINS = [
    "http://localhost:3000",
    "https://your-dashboard.vercel.app",
]
```

2. Redeploy API after updating CORS

---

## Cost Comparison

| Platform | Free Tier | Paid Tier | Best For |
|----------|-----------|-----------|----------|
| **Railway** | No | $5/month | Always-on, easy setup |
| **Render** | Yes (spins down) | $7/month | Free tier testing |

**Recommendation:** Railway for production ($5/month, always-on)

---

## Next Steps

After deploying:

1. ✅ Update `NEXT_PUBLIC_API_URL` in Vercel
2. ✅ Test admin portal → ETL trigger
3. ✅ Monitor API logs
4. ✅ Set up alerts (optional)

---

## Support

- **Railway Docs:** https://docs.railway.app
- **Render Docs:** https://render.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com
