# ML/CV Implementation Plan

**Step-by-step guide to implement ML/CV layer for automated tracking**

Last Updated: 2026-01-13

---

## Overview

This plan details how to implement ML/CV (Machine Learning/Computer Vision) for automated game tracking, reducing manual tracking time by 50-70%.

---

## Architecture

```
┌─────────────────┐
│  Video Upload   │
│  (Dashboard)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Cloudflare R2   │
│ (Video Storage) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  API Gateway    │
│   (Railway)     │
└────────┬────────┘
         │
         ├─────────────────┐
         ▼                 ▼
┌──────────────┐  ┌──────────────┐
│  Replicate   │  │   RunPod     │
│  (MVP)       │  │  (Production)│
└──────────────┘  └──────────────┘
         │                 │
         └────────┬────────┘
                  ▼
         ┌──────────────┐
         │   Results    │
         │  (Supabase)  │
         └──────────────┘
```

---

## Phase 1: Video Storage Setup (Week 1)

### 1.1 Create Cloudflare R2 Bucket

1. **Sign up for Cloudflare R2**
   - Go to https://dash.cloudflare.com
   - Navigate to R2
   - Create bucket: `benchsight-videos`

2. **Get Access Keys**
   - Create API token
   - Save Access Key ID and Secret Access Key

3. **Configure Environment Variables**
   ```bash
   R2_ACCOUNT_ID=your-account-id
   R2_ACCESS_KEY_ID=your-access-key
   R2_SECRET_ACCESS_KEY=your-secret-key
   R2_BUCKET_NAME=benchsight-videos
   R2_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com
   ```

### 1.2 Create Upload API Endpoint

```python
# api/routes/video.py
from fastapi import FastAPI, UploadFile, File
import boto3
from botocore.config import Config

@app.post("/api/video/upload")
async def upload_video(
    file: UploadFile = File(...),
    game_id: str = None
):
    # Initialize R2 client (S3-compatible)
    s3 = boto3.client(
        's3',
        endpoint_url=os.getenv('R2_ENDPOINT_URL'),
        aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
        config=Config(signature_version='s3v4')
    )
    
    # Upload to R2
    key = f"games/{game_id}/{file.filename}"
    s3.upload_fileobj(file.file, os.getenv('R2_BUCKET_NAME'), key)
    
    # Get public URL
    url = f"{os.getenv('R2_ENDPOINT_URL')}/{os.getenv('R2_BUCKET_NAME')}/{key}"
    
    # Save metadata to Supabase
    supabase.table('videos').insert({
        'game_id': game_id,
        'filename': file.filename,
        'url': url,
        'size': file.size,
        'status': 'uploaded'
    }).execute()
    
    return {"video_id": video_id, "url": url}
```

---

## Phase 2: ML Service Integration (Week 2)

### 2.1 MVP: Replicate API Integration

**Why Replicate for MVP:**
- Quick setup (2-4 hours)
- No infrastructure management
- Pay-per-use pricing
- Pre-built models available

#### Setup

1. **Create Replicate Account**
   - Go to https://replicate.com
   - Sign up and get API token

2. **Install Replicate SDK**
   ```bash
   pip install replicate
   ```

3. **Create ML Processing Endpoint**
   ```python
   # api/routes/ml.py
   import replicate
   import os
   
   REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
   
   @app.post("/api/ml/process-video")
   async def process_video(video_id: str):
       # Get video from R2
       video = get_video_from_r2(video_id)
       
       # Process with Replicate (YOLO v8)
       output = replicate.run(
           "ultralytics/yolov8:latest",
           input={
               "source": video.url,
               "task": "detect",  # Object detection
               "conf": 0.25,      # Confidence threshold
           }
       )
       
       # Parse results
       events = parse_yolo_output(output)
       
       # Save to Supabase
       save_events_to_supabase(video.game_id, events)
       
       return {"status": "success", "events": len(events)}
   ```

#### Models to Use

- **YOLO v8:** Object detection (puck, players, net)
- **Video Processing:** Frame extraction
- **Custom Models:** Train on hockey-specific data

### 2.2 Production: RunPod GPU Setup

**When to Migrate:**
- Need custom models
- Higher accuracy requirements
- Cost optimization at scale
- Full control needed

#### Setup

1. **Create RunPod Account**
   - Go to https://www.runpod.io
   - Create GPU pod

2. **Deploy ML Service**
   ```dockerfile
   # Dockerfile
   FROM pytorch/pytorch:latest
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY app.py .
   CMD ["python", "app.py"]
   ```

3. **ML Service Code**
   ```python
   # app.py
   from fastapi import FastAPI
   import cv2
   from ultralytics import YOLO
   
   app = FastAPI()
   model = YOLO('yolov8n.pt')  # Load model
   
   @app.post("/process")
   async def process_video(video_url: str):
       # Download video
       video = download_video(video_url)
       
       # Process frames
       results = model(video)
       
       # Extract events
       events = extract_events(results)
       
       return {"events": events}
   ```

---

## Phase 3: Hybrid Tracking System (Week 3)

### 3.1 ML Suggestions in Tracker

#### Frontend Integration

```typescript
// Tracker component
const [mlSuggestions, setMlSuggestions] = useState<Event[]>([]);
const [confidence, setConfidence] = useState<number>(0);

useEffect(() => {
  // Load ML suggestions when game loads
  loadMLSuggestions(gameId);
}, [gameId]);

const loadMLSuggestions = async (gameId: string) => {
  const response = await fetch(
    `${API_URL}/api/ml/suggestions/${gameId}`
  );
  const suggestions = await response.json();
  setMlSuggestions(suggestions);
};

// Display suggestions with confidence
{mlSuggestions.map(suggestion => (
  <MLSuggestionCard
    key={suggestion.id}
    event={suggestion}
    confidence={suggestion.confidence}
    onAccept={() => acceptSuggestion(suggestion)}
    onReject={() => rejectSuggestion(suggestion)}
  />
))}
```

### 3.2 Confidence-Based Auto-Accept

```typescript
// Auto-accept high confidence events
const processMLSuggestions = (suggestions: Event[]) => {
  suggestions.forEach(suggestion => {
    if (suggestion.confidence > 0.90) {
      // Auto-accept high confidence
      acceptEvent(suggestion);
    } else if (suggestion.confidence > 0.70) {
      // Queue for review
      queueForReview(suggestion);
    } else {
      // Reject low confidence
      rejectEvent(suggestion);
    }
  });
};
```

### 3.3 Learning from Corrections

```python
# Track corrections for model improvement
@app.post("/api/ml/correction")
async def log_correction(
    original: Event,
    corrected: Event,
    user_id: str
):
    # Log correction
    supabase.table('ml_corrections').insert({
        'original_event': original,
        'corrected_event': corrected,
        'user_id': user_id,
        'timestamp': datetime.now()
    }).execute()
    
    # Use for model retraining
    # (Future: Retrain model periodically)
```

---

## Phase 4: Event Detection Models (Week 4)

### 4.1 Shot Detection

```python
def detect_shots(video_frames, detections):
    shots = []
    
    for frame_idx, frame in enumerate(video_frames):
        # Detect puck near net
        puck_near_net = is_puck_near_net(detections[frame_idx])
        
        # Detect player with stick raised
        player_shooting = detect_shooting_motion(detections[frame_idx])
        
        if puck_near_net and player_shooting:
            shot = {
                'type': 'shot',
                'frame': frame_idx,
                'location': get_puck_location(detections[frame_idx]),
                'player': get_shooting_player(detections[frame_idx]),
                'confidence': calculate_confidence(...)
            }
            shots.append(shot)
    
    return shots
```

### 4.2 Goal Detection

```python
def detect_goals(video_frames, detections):
    goals = []
    
    for frame_idx, frame in enumerate(video_frames):
        # Detect puck crossing goal line
        puck_in_net = is_puck_in_net(detections[frame_idx])
        
        # Verify with multiple frames
        if puck_in_net and verify_goal_sequence(detections, frame_idx):
            goal = {
                'type': 'goal',
                'frame': frame_idx,
                'scorer': get_scoring_player(detections[frame_idx]),
                'assists': get_assisting_players(detections[frame_idx]),
                'confidence': 0.95  # High confidence for goals
            }
            goals.append(goal)
    
    return goals
```

### 4.3 Pass Detection

```python
def detect_passes(video_frames, detections):
    passes = []
    
    for frame_idx, frame in enumerate(video_frames):
        # Detect puck movement between players
        puck_movement = track_puck_movement(detections, frame_idx)
        
        # Identify passer and receiver
        passer, receiver = identify_players(puck_movement)
        
        if passer and receiver:
            pass_event = {
                'type': 'pass',
                'frame': frame_idx,
                'passer': passer,
                'receiver': receiver,
                'success': did_pass_succeed(puck_movement),
                'confidence': calculate_confidence(...)
            }
            passes.append(pass_event)
    
    return passes
```

---

## Cost Optimization

### MVP (Replicate)
- **Cost:** $0.001-0.01 per video
- **100 videos/month:** $0.10-1.00
- **Best for:** Testing, low volume

### Production (RunPod)
- **Cost:** $0.20-2/hour for GPU
- **100 videos/month (2 hours processing):** $0.40-4.00
- **Best for:** Production, custom models

### Storage (Cloudflare R2)
- **Cost:** $0.015/GB storage
- **100 videos (50GB):** $0.75/month
- **No egress fees:** Major savings vs S3

---

## Implementation Checklist

### Week 1: Infrastructure
- [ ] Set up Cloudflare R2 bucket
- [ ] Create video upload endpoint
- [ ] Test video upload/download
- [ ] Set up video metadata storage

### Week 2: ML Integration
- [ ] Set up Replicate account
- [ ] Create ML processing endpoint
- [ ] Test YOLO object detection
- [ ] Parse ML results

### Week 3: Hybrid System
- [ ] Integrate ML suggestions in tracker
- [ ] Implement confidence scoring
- [ ] Create human verification UI
- [ ] Test end-to-end workflow

### Week 4: Event Detection
- [ ] Implement shot detection
- [ ] Implement goal detection
- [ ] Implement pass detection
- [ ] Test accuracy and tune models

---

## Next Steps

1. **Start with Replicate** (quick MVP)
2. **Test with sample videos**
3. **Iterate on accuracy**
4. **Migrate to RunPod** (if needed)
5. **Train custom models** (future)

---

*See `docs/ML_CV_ARCHITECTURE_PLAN.md` for architecture details*
