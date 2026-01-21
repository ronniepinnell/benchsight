# Tracker Rust Implementation Plan

**Detailed plan for Rust backend implementation**

Last Updated: 2026-01-15  
Version: 23.5 → Target: Rust/Next.js

---

## Overview

This document provides a detailed plan for implementing the Rust backend for the tracker conversion.

**Framework:** Axum  
**Database:** PostgreSQL (via Supabase)  
**Goal:** High-performance, type-safe API for tracker operations

---

## Why Rust?

### Performance Benefits
- **Speed:** Rust is comparable to C/C++ in performance
- **Concurrency:** Excellent async/await support
- **Memory Safety:** No garbage collection overhead
- **Zero-Cost Abstractions:** High-level code compiles to efficient machine code

### Use Cases in Tracker
- Event/shift CRUD operations (high frequency)
- XY coordinate calculations (many per game)
- Validation logic (called frequently)
- Export processing (large datasets)
- Data transformation (ETL compatibility)

---

## Project Structure

```
tracker-api/
├── Cargo.toml
├── .env.example
├── README.md
├── src/
│   ├── main.rs                       # Entry point
│   ├── lib.rs                        # Library root
│   │
│   ├── api/
│   │   ├── mod.rs
│   │   ├── events.rs                 # Event endpoints
│   │   ├── shifts.rs                 # Shift endpoints
│   │   ├── export.rs                 # Export endpoints
│   │   ├── validation.rs             # Validation endpoints
│   │   └── health.rs                 # Health check
│   │
│   ├── models/
│   │   ├── mod.rs
│   │   ├── event.rs                  # Event model
│   │   ├── shift.rs                  # Shift model
│   │   ├── game.rs                   # Game model
│   │   └── error.rs                  # Error types
│   │
│   ├── services/
│   │   ├── mod.rs
│   │   ├── event_service.rs          # Event business logic
│   │   ├── shift_service.rs         # Shift business logic
│   │   ├── validation_service.rs    # Validation logic
│   │   ├── export_service.rs        # Export logic
│   │   └── xy_service.rs            # XY calculations
│   │
│   ├── database/
│   │   ├── mod.rs
│   │   ├── connection.rs            # DB connection pool
│   │   ├── events.rs                # Event queries
│   │   ├── shifts.rs                # Shift queries
│   │   └── migrations.rs            # Database migrations
│   │
│   └── utils/
│       ├── mod.rs
│       ├── validation.rs             # Validation utilities
│       ├── xy.rs                     # XY utilities
│       └── time.rs                   # Time utilities
│
└── tests/
    ├── integration/
    │   ├── events_test.rs
    │   ├── shifts_test.rs
    │   └── export_test.rs
    └── unit/
        ├── validation_test.rs
        └── xy_test.rs
```

---

## Dependencies (Cargo.toml)

```toml
[package]
name = "tracker-api"
version = "0.1.0"
edition = "2021"

[dependencies]
# Web framework
axum = "0.7"
tower = "0.4"
tower-http = { version = "0.5", features = ["cors"] }
tokio = { version = "1", features = ["full"] }

# Database
sqlx = { version = "0.7", features = ["runtime-tokio-rustls", "postgres", "chrono", "uuid"] }
postgres = "0.19"

# Serialization
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# Error handling
anyhow = "1.0"
thiserror = "1.0"

# Validation
validator = { version = "0.18", features = ["derive"] }

# Excel export
calamine = "0.24"
rust_xlsxwriter = "0.75"

# Time
chrono = "0.4"

# UUID
uuid = { version = "1.6", features = ["v4", "serde"] }

# Environment variables
dotenv = "0.15"

# Logging
tracing = "0.1"
tracing-subscriber = "0.3"

[dev-dependencies]
# Testing
tokio-test = "0.4"
mockall = "0.12"
```

---

## Core Models

### Event Model

```rust
// src/models/event.rs
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use uuid::Uuid;
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Event {
    pub id: Uuid,
    pub game_id: i32,
    pub event_index: i32,
    pub event_type: String,
    pub event_detail: Option<String>,
    pub event_detail_2: Option<String>,
    pub play_detail: Option<String>,
    pub play_detail_2: Option<String>,
    pub period: i32,
    pub time: String,
    pub time_start_total_seconds: Option<i32>,
    pub team: String,
    pub event_player_1: Option<String>,
    pub event_player_2: Option<String>,
    pub event_player_3: Option<String>,
    pub puck_x: Option<f64>,
    pub puck_y: Option<f64>,
    pub net_x: Option<f64>,
    pub net_y: Option<f64>,
    pub zone: Option<String>,
    pub strength: Option<String>,
    pub situation: Option<String>,
    pub linked_event_id: Option<Uuid>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreateEventRequest {
    pub game_id: i32,
    pub event_type: String,
    pub event_detail: Option<String>,
    pub event_detail_2: Option<String>,
    pub play_detail: Option<String>,
    pub play_detail_2: Option<String>,
    pub period: i32,
    pub time: String,
    pub team: String,
    pub event_player_1: Option<String>,
    pub event_player_2: Option<String>,
    pub event_player_3: Option<String>,
    pub puck_x: Option<f64>,
    pub puck_y: Option<f64>,
    pub net_x: Option<f64>,
    pub net_y: Option<f64>,
    pub zone: Option<String>,
    pub strength: Option<String>,
    pub situation: Option<String>,
    pub linked_event_id: Option<Uuid>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UpdateEventRequest {
    pub event_type: Option<String>,
    pub event_detail: Option<String>,
    pub event_detail_2: Option<String>,
    pub play_detail: Option<String>,
    pub play_detail_2: Option<String>,
    pub period: Option<i32>,
    pub time: Option<String>,
    pub team: Option<String>,
    pub event_player_1: Option<String>,
    pub event_player_2: Option<String>,
    pub event_player_3: Option<String>,
    pub puck_x: Option<f64>,
    pub puck_y: Option<f64>,
    pub net_x: Option<f64>,
    pub net_y: Option<f64>,
    pub zone: Option<String>,
    pub strength: Option<String>,
    pub situation: Option<String>,
    pub linked_event_id: Option<Uuid>,
}
```

### Shift Model

```rust
// src/models/shift.rs
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use uuid::Uuid;
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Shift {
    pub id: Uuid,
    pub game_id: i32,
    pub shift_index: i32,
    pub player_id: String,
    pub player_number: Option<i32>,
    pub team: String,
    pub period: i32,
    pub start_time: String,
    pub end_time: Option<String>,
    pub start_total_seconds: i32,
    pub end_total_seconds: Option<i32>,
    pub duration_seconds: Option<i32>,
    pub start_type: Option<String>,
    pub end_type: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreateShiftRequest {
    pub game_id: i32,
    pub player_id: String,
    pub player_number: Option<i32>,
    pub team: String,
    pub period: i32,
    pub start_time: String,
    pub end_time: Option<String>,
    pub start_type: Option<String>,
    pub end_type: Option<String>,
}
```

---

## API Endpoints

### Event Endpoints

```rust
// src/api/events.rs
use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::Json,
    routing::{get, post, put, delete},
    Router,
};
use uuid::Uuid;
use crate::models::event::{Event, CreateEventRequest, UpdateEventRequest};
use crate::services::event_service::EventService;
use crate::database::connection::DbPool;

pub fn router() -> Router<DbPool> {
    Router::new()
        .route("/", post(create_event))
        .route("/:id", get(get_event))
        .route("/:id", put(update_event))
        .route("/:id", delete(delete_event))
        .route("/", get(list_events))
}

async fn create_event(
    State(pool): State<DbPool>,
    Json(request): Json<CreateEventRequest>,
) -> Result<Json<Event>, StatusCode> {
    let event = EventService::create_event(pool, request).await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    Ok(Json(event))
}

async fn get_event(
    State(pool): State<DbPool>,
    Path(id): Path<Uuid>,
) -> Result<Json<Event>, StatusCode> {
    let event = EventService::get_event(pool, id).await
        .map_err(|_| StatusCode::NOT_FOUND)?;
    Ok(Json(event))
}

async fn update_event(
    State(pool): State<DbPool>,
    Path(id): Path<Uuid>,
    Json(request): Json<UpdateEventRequest>,
) -> Result<Json<Event>, StatusCode> {
    let event = EventService::update_event(pool, id, request).await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    Ok(Json(event))
}

async fn delete_event(
    State(pool): State<DbPool>,
    Path(id): Path<Uuid>,
) -> Result<StatusCode, StatusCode> {
    EventService::delete_event(pool, id).await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    Ok(StatusCode::NO_CONTENT)
}

async fn list_events(
    State(pool): State<DbPool>,
    Query(params): Query<ListEventsParams>,
) -> Result<Json<Vec<Event>>, StatusCode> {
    let events = EventService::list_events(pool, params.game_id).await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    Ok(Json(events))
}
```

---

## Services

### Event Service

```rust
// src/services/event_service.rs
use crate::models::event::{Event, CreateEventRequest, UpdateEventRequest};
use crate::database::connection::DbPool;
use crate::database::events as event_queries;
use crate::services::validation_service::ValidationService;
use crate::services::xy_service::XYService;
use uuid::Uuid;

pub struct EventService;

impl EventService {
    pub async fn create_event(
        pool: DbPool,
        request: CreateEventRequest,
    ) -> Result<Event, ServiceError> {
        // Validate
        ValidationService::validate_event(&request)?;
        
        // Calculate derived fields
        let time_start_total_seconds = Self::calculate_total_seconds(
            request.period,
            &request.time
        )?;
        
        let zone = if let (Some(x), Some(y)) = (request.puck_x, request.puck_y) {
            Some(XYService::get_zone_from_xy(x, y))
        } else {
            None
        };
        
        // Get next event index
        let event_index = event_queries::get_next_event_index(pool.clone(), request.game_id).await?;
        
        // Create event
        let event = event_queries::create_event(
            pool,
            CreateEventRequest {
                event_index,
                time_start_total_seconds: Some(time_start_total_seconds),
                zone,
                ..request
            }
        ).await?;
        
        Ok(event)
    }
    
    pub async fn update_event(
        pool: DbPool,
        id: Uuid,
        request: UpdateEventRequest,
    ) -> Result<Event, ServiceError> {
        // Get existing event
        let mut event = event_queries::get_event(pool.clone(), id).await?;
        
        // Update fields
        if let Some(event_type) = request.event_type {
            event.event_type = event_type;
        }
        // ... update other fields
        
        // Recalculate derived fields if needed
        if request.period.is_some() || request.time.is_some() {
            event.time_start_total_seconds = Some(
                Self::calculate_total_seconds(event.period, &event.time)?
            );
        }
        
        if request.puck_x.is_some() || request.puck_y.is_some() {
            if let (Some(x), Some(y)) = (event.puck_x, event.puck_y) {
                event.zone = Some(XYService::get_zone_from_xy(x, y));
            }
        }
        
        // Update in database
        let event = event_queries::update_event(pool, id, event).await?;
        
        Ok(event)
    }
    
    pub async fn delete_event(
        pool: DbPool,
        id: Uuid,
    ) -> Result<(), ServiceError> {
        event_queries::delete_event(pool, id).await?;
        Ok(())
    }
    
    fn calculate_total_seconds(period: i32, time: &str) -> Result<i32, ServiceError> {
        // Parse time string (MM:SS)
        let parts: Vec<&str> = time.split(':').collect();
        if parts.len() != 2 {
            return Err(ServiceError::InvalidTime);
        }
        
        let minutes: i32 = parts[0].parse().map_err(|_| ServiceError::InvalidTime)?;
        let seconds: i32 = parts[1].parse().map_err(|_| ServiceError::InvalidTime)?;
        
        // Calculate total seconds
        let period_start = (period - 1) * 18 * 60; // 18 minutes per period
        let period_time = minutes * 60 + seconds;
        let total = period_start + period_time;
        
        Ok(total)
    }
}
```

### XY Service

```rust
// src/services/xy_service.rs
pub struct XYService;

impl XYService {
    pub fn convert_canvas_to_rink(
        x: f64,
        y: f64,
        period: i32,
        home_attacks_right_p1: bool,
    ) -> (f64, f64) {
        // Convert canvas coordinates (0-100, 0-50) to rink coordinates (feet)
        let rink_width = 200.0; // feet
        let rink_height = 85.0; // feet
        
        let rink_x = (x / 100.0) * rink_width - (rink_width / 2.0);
        let rink_y = (y / 50.0) * rink_height - (rink_height / 2.0);
        
        // Handle period direction
        let (final_x, final_y) = if period % 2 == 0 {
            // Even periods: flip X
            (-rink_x, rink_y)
        } else {
            (rink_x, rink_y)
        };
        
        (final_x, final_y)
    }
    
    pub fn validate_xy_position(x: f64, y: f64) -> bool {
        // Validate XY is within rink bounds
        let rink_width = 200.0;
        let rink_height = 85.0;
        
        let rink_x = (x / 100.0) * rink_width - (rink_width / 2.0);
        let rink_y = (y / 50.0) * rink_height - (rink_height / 2.0);
        
        rink_x.abs() <= rink_width / 2.0 && rink_y.abs() <= rink_height / 2.0
    }
    
    pub fn get_zone_from_xy(x: f64, y: f64) -> String {
        // Determine zone from XY position
        let rink_width = 200.0;
        let offensive_zone_start = rink_width / 3.0;
        let defensive_zone_start = -rink_width / 3.0;
        
        if x > offensive_zone_start {
            "Offensive".to_string()
        } else if x < defensive_zone_start {
            "Defensive".to_string()
        } else {
            "Neutral".to_string()
        }
    }
}
```

---

## Database Queries

```rust
// src/database/events.rs
use sqlx::PgPool;
use uuid::Uuid;
use crate::models::event::{Event, CreateEventRequest};

pub async fn create_event(
    pool: PgPool,
    request: CreateEventRequest,
) -> Result<Event, sqlx::Error> {
    let event = sqlx::query_as::<_, Event>(
        r#"
        INSERT INTO tracker_events (
            game_id, event_index, event_type, event_detail, event_detail_2,
            play_detail, play_detail_2, period, time, time_start_total_seconds,
            team, event_player_1, event_player_2, event_player_3,
            puck_x, puck_y, net_x, net_y, zone, strength, situation, linked_event_id
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22)
        RETURNING *
        "#
    )
    .bind(request.game_id)
    .bind(request.event_index)
    .bind(&request.event_type)
    .bind(&request.event_detail)
    .bind(&request.event_detail_2)
    .bind(&request.play_detail)
    .bind(&request.play_detail_2)
    .bind(request.period)
    .bind(&request.time)
    .bind(request.time_start_total_seconds)
    .bind(&request.team)
    .bind(&request.event_player_1)
    .bind(&request.event_player_2)
    .bind(&request.event_player_3)
    .bind(request.puck_x)
    .bind(request.puck_y)
    .bind(request.net_x)
    .bind(request.net_y)
    .bind(&request.zone)
    .bind(&request.strength)
    .bind(&request.situation)
    .bind(request.linked_event_id)
    .fetch_one(&pool)
    .await?;
    
    Ok(event)
}

pub async fn get_event(pool: PgPool, id: Uuid) -> Result<Event, sqlx::Error> {
    let event = sqlx::query_as::<_, Event>(
        "SELECT * FROM tracker_events WHERE id = $1"
    )
    .bind(id)
    .fetch_one(&pool)
    .await?;
    
    Ok(event)
}

pub async fn list_events(pool: PgPool, game_id: i32) -> Result<Vec<Event>, sqlx::Error> {
    let events = sqlx::query_as::<_, Event>(
        "SELECT * FROM tracker_events WHERE game_id = $1 ORDER BY event_index"
    )
    .bind(game_id)
    .fetch_all(&pool)
    .await?;
    
    Ok(events)
}
```

---

## Testing

### Unit Tests

```rust
// tests/unit/xy_test.rs
use tracker_api::services::xy_service::XYService;

#[test]
fn test_get_zone_from_xy() {
    // Test offensive zone
    let zone = XYService::get_zone_from_xy(70.0, 25.0);
    assert_eq!(zone, "Offensive");
    
    // Test defensive zone
    let zone = XYService::get_zone_from_xy(30.0, 25.0);
    assert_eq!(zone, "Defensive");
    
    // Test neutral zone
    let zone = XYService::get_zone_from_xy(50.0, 25.0);
    assert_eq!(zone, "Neutral");
}
```

### Integration Tests

```rust
// tests/integration/events_test.rs
use tracker_api::api::events;
use tracker_api::models::event::CreateEventRequest;

#[tokio::test]
async fn test_create_event() {
    // Setup test database
    let pool = setup_test_db().await;
    
    // Create event
    let request = CreateEventRequest {
        game_id: 1,
        event_type: "Shot".to_string(),
        period: 1,
        time: "15:30".to_string(),
        team: "Home".to_string(),
        ..Default::default()
    };
    
    let event = EventService::create_event(pool, request).await.unwrap();
    
    assert_eq!(event.event_type, "Shot");
    assert_eq!(event.period, 1);
}
```

---

## Deployment

### Build

```bash
# Build release binary
cargo build --release

# Binary will be at: target/release/tracker-api
```

### Docker

```dockerfile
FROM rust:1.75 as builder
WORKDIR /app
COPY . .
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/target/release/tracker-api /usr/local/bin/tracker-api
CMD ["tracker-api"]
```

### Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
PORT=3001
RUST_LOG=info
```

---

## Related Documentation

- [TRACKER_ARCHITECTURE_PLAN.md](TRACKER_ARCHITECTURE_PLAN.md) - Architecture design
- [TRACKER_CONVERSION_ROADMAP.md](TRACKER_CONVERSION_ROADMAP.md) - Conversion roadmap
- [TRACKER_CONVERSION_SPEC.md](TRACKER_CONVERSION_SPEC.md) - Conversion specification

---

*Last Updated: 2026-01-15*
