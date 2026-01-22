---
name: cv-tracking
description: Work on computer vision pipeline for automated hockey tracking from video. Use when developing video analysis, player detection, or puck tracking features.
allowed-tools: Bash, Read, Write, Edit
argument-hint: [player-detection|puck-tracking|pose|action-recognition]
---

# Computer Vision Tracking

Build CV pipeline for automated hockey video analysis.

## CV Models (Planned)

### 1. Player Detection & Tracking
**Purpose:** Detect and track players across frames
**Approach:**
- YOLOv8 for detection
- DeepSORT for tracking
- Jersey number OCR

### 2. Puck Tracking
**Purpose:** Track puck location
**Challenges:**
- Small object
- Fast movement
- Occlusion
**Approach:**
- Specialized small object detection
- Motion prediction
- Multi-frame analysis

### 3. Pose Estimation
**Purpose:** Player body positioning
**Use cases:**
- Shooting form analysis
- Skating mechanics
- Goalie positioning

### 4. Action Recognition
**Purpose:** Identify events automatically
**Events:**
- Shots
- Passes
- Faceoffs
- Hits

### 5. Rink Homography
**Purpose:** Map video coordinates to rink coordinates
**Approach:**
- Line detection
- Perspective transformation
- Calibration points

## Tech Stack

**Detection/Tracking:**
- Ultralytics YOLOv8
- OpenCV
- DeepSORT / ByteTrack

**Deep Learning:**
- PyTorch
- torchvision
- timm (pretrained models)

**Video Processing:**
- FFmpeg
- MoviePy
- Decord (fast video loading)

**Inference:**
- ONNX Runtime
- TensorRT (GPU optimization)
- Triton Inference Server

## Pipeline Structure

```
src/cv/
├── detection/
│   ├── player_detector.py   # Player detection
│   ├── puck_detector.py     # Puck detection
│   └── jersey_ocr.py        # Jersey number recognition
├── tracking/
│   ├── multi_tracker.py     # Multi-object tracking
│   ├── track_association.py # Track-to-player mapping
│   └── trajectory.py        # Trajectory analysis
├── pose/
│   ├── pose_estimator.py    # Pose estimation
│   └── pose_analysis.py     # Pose interpretation
├── action/
│   ├── action_classifier.py # Action recognition
│   └── event_detector.py    # Event detection
├── calibration/
│   ├── rink_detector.py     # Rink line detection
│   ├── homography.py        # Perspective transform
│   └── calibration.py       # Camera calibration
├── inference/
│   ├── video_processor.py   # Video processing pipeline
│   ├── batch_processor.py   # Batch video processing
│   └── realtime_processor.py # Real-time processing
└── utils/
    ├── video_utils.py       # Video utilities
    ├── visualization.py     # Debug visualization
    └── annotation.py        # Annotation tools
```

## Processing Pipeline

```
Video Input
    │
    ▼
┌─────────────────┐
│ Frame Extraction │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌────────┐
│Players│ │ Puck   │
│Detect │ │ Detect │
└───┬───┘ └───┬────┘
    │         │
    ▼         ▼
┌───────────────────┐
│ Multi-Object      │
│ Tracking          │
└────────┬──────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌────────┐
│ Pose  │ │ Action │
│ Est.  │ │ Recog. │
└───┬───┘ └───┬────┘
    │         │
    ▼         ▼
┌─────────────────┐
│ Event Generation │
│ (to ETL format) │
└─────────────────┘
```

## Training Data

**Sources:**
- Manual annotations from tracker
- Public hockey datasets
- Synthetic data generation

**Annotation Format:**
```json
{
  "frame": 1234,
  "players": [
    {"bbox": [x1, y1, x2, y2], "team": "home", "jersey": 17}
  ],
  "puck": {"x": 450, "y": 320, "visible": true},
  "event": "shot"
}
```

## Hardware Requirements

**Training:**
- GPU: RTX 3090+ or A100
- RAM: 32GB+
- Storage: 1TB+ SSD

**Inference:**
- GPU: RTX 3060+ (real-time)
- CPU: Possible but slower

## Output

CV documentation goes to:
```
docs/cv/{component}-documentation.md
```

Events output to standard tracker format for ETL processing.
