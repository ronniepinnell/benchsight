# BenchSight Admin Portal

**Complete admin portal documentation: current state, development plan, API requirements, and technical specification**

Last Updated: 2026-01-15  
Version: 1.0

---

## Overview

The admin portal is a web interface for managing ETL processes, data uploads, game management, and system administration.

**Location:** `ui/portal/`  
**Current Status:** UI mockup with partial API integration (10-30% complete)  
**Technology:** HTML/CSS/JavaScript  
**Backend:** FastAPI (api/)  
**Target:** Fully functional admin portal (100% complete)

**Related Documentation:**
- [PORTAL_ARCHITECTURE_DIAGRAMS.md](PORTAL_ARCHITECTURE_DIAGRAMS.md) - **NEW** Visual portal architecture diagrams (components, data flow, user journey)

---

## Table of Contents

1. [Current State](#current-state)
2. [Architecture](#architecture)
3. [API Integration](#api-integration)
4. [Development Plan](#development-plan)
5. [API Requirements](#api-requirements)
6. [Technical Specification](#technical-specification)
7. [File Structure](#file-structure)

---

## Current State

### What Exists

#### UI Components

**Design:**
- ✅ Modern dark theme UI
- ✅ Cyberpunk aesthetic
- ✅ Responsive layout
- ✅ Navigation sidebar
- ✅ Main content area

**Pages/Sections:**
- ✅ ETL Control interface (UI + partial API integration)
- ✅ Game Management interface (UI only)
- ✅ Data Browser interface (UI only)
- ✅ Settings interface (UI only)

**UI Elements:**
- ✅ Buttons and controls
- ✅ Forms and inputs
- ✅ Tables and lists
- ✅ Modals and dialogs

#### JavaScript

**Current Implementation:**
- ✅ Basic API client (`js/api.js`)
- ✅ ETL integration (`js/etl.js`)
- ✅ Schema generation (`js/schema.js`)
- ✅ Sync functionality (`js/sync.js`)
- ✅ Configuration (`js/config.js`)
- ⚠️ Partial API integration (some endpoints connected)
- ❌ No data fetching from Supabase
- ❌ No game management functionality
- ❌ No authentication

### What's Missing

#### Backend Integration

**Critical Missing Features:**
- ❌ **Limited API Integration** - Some endpoints connected, many placeholders remain
- ❌ **NO Data Fetching** - No connection to Supabase for data display
- ❌ **NO Game Management** - Cannot create/edit/delete games
- ❌ **NO Data Display** - Cannot view actual data from tables

#### Authentication

**Missing:**
- ❌ **NO Authentication** - No login system
- ❌ **NO User Management** - No user roles
- ❌ **NO Protected Routes** - No access control

#### Functionality

**Missing Features:**
- ❌ Complete ETL job triggering (partial)
- ❌ ETL status monitoring (partial)
- ❌ Upload to Supabase (partial)
- ❌ Game creation/editing
- ❌ Data browsing
- ❌ Settings persistence

---

## Architecture

### High-Level Architecture

```
┌─────────────────────┐
│  Admin Portal UI    │
│  (ui/portal/)       │
│  - HTML/CSS/JS      │
└──────────┬──────────┘
           │
           │ HTTP/REST
           ▼
┌─────────────────────┐
│   ETL API           │
│   (api/)             │
│   - FastAPI          │
└──────────┬──────────┘
           │
           └──► ETL Pipeline
           └──► Supabase
```

### Component Breakdown

**Frontend (Portal):**
- HTML/CSS/JavaScript (current)
- API client for HTTP requests
- State management (local JavaScript variables)
- UI components

**Backend (API):**
- FastAPI application
- ETL service integration
- Supabase integration
- Job management

---

## API Integration

### Base Configuration

```javascript
// ui/portal/js/config.js
const API_CONFIG = {
  baseUrl: process.env.API_URL || 'http://localhost:8000',
  apiKey: process.env.API_KEY || null,
  timeout: 30000
};

const SUPABASE_CONFIG = {
  url: process.env.SUPABASE_URL || 'https://your-project.supabase.co',
  anonKey: process.env.SUPABASE_ANON_KEY || 'your-key'
};
```

### API Client

```javascript
// ui/portal/js/api.js
class APIClient {
  constructor(baseUrl, apiKey) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'API request failed');
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // ETL endpoints
  async triggerETL(mode, gameIds = null, options = {}) {
    return this.request('/api/etl/trigger', {
      method: 'POST',
      body: JSON.stringify({
        mode,
        game_ids: gameIds,
        options
      })
    });
  }

  async getETLStatus(jobId) {
    return this.request(`/api/etl/status/${jobId}`);
  }

  async getETLHistory(limit = 10) {
    return this.request(`/api/etl/history?limit=${limit}`);
  }

  // Upload endpoints
  async uploadToSupabase(tables = null, mode = 'all') {
    return this.request('/api/upload/to-supabase', {
      method: 'POST',
      body: JSON.stringify({ tables, mode })
    });
  }

  // Staging endpoints
  async uploadBLBTable(tableName, data, replace = false) {
    return this.request('/api/staging/blb-tables/upload', {
      method: 'POST',
      body: JSON.stringify({
        table_name: tableName,
        data,
        replace
      })
    });
  }
}

const api = new APIClient(API_CONFIG.baseUrl, API_CONFIG.apiKey);
```

### ETL Integration

**Connect ETL Controls:**
```javascript
// ui/portal/js/etl.js
async function runETL() {
  const mode = document.getElementById('etlMode').value;
  const clean = document.getElementById('etlClean').checked;
  const sync = document.getElementById('etlSync').checked;
  
  const gameId = document.getElementById('etlGameId').value;
  const gameIds = gameId ? [parseInt(gameId)] : null;

  // Show loading state
  document.getElementById('etlStatusBadge').textContent = 'STARTING';
  document.getElementById('etlStatusBadge').className = 'badge badge-warn';
  document.getElementById('etlProgress').style.display = 'block';

  try {
    // Trigger ETL
    const response = await api.triggerETL(mode, gameIds, {
      wipe: clean,
      upload_to_supabase: sync
    });

    currentJobId = response.job_id;
    log(`ETL job started: ${currentJobId}`, 'info');

    // Start polling for status
    startStatusPolling(currentJobId);

  } catch (error) {
    log(`Failed to start ETL: ${error.message}`, 'error');
    document.getElementById('etlStatusBadge').textContent = 'ERROR';
    document.getElementById('etlStatusBadge').className = 'badge badge-danger';
  }
}

function startStatusPolling(jobId) {
  statusInterval = setInterval(async () => {
    try {
      const status = await api.getETLStatus(jobId);
      
      // Update UI
      updateETLStatus(status);
      
      // Stop polling if complete
      if (status.status === 'completed' || status.status === 'failed') {
        clearInterval(statusInterval);
      }
    } catch (error) {
      log(`Error checking status: ${error.message}`, 'error');
    }
  }, 2000);  // Poll every 2 seconds
}
```

---

## Development Plan

### Phase 1: API Integration (Week 1-2)

**Goal:** Connect portal to API and enable core functionality

#### Week 1: ETL Integration

**Tasks:**
1. **Replace Placeholder Functions**
   - Replace `triggerETL()` with real API call
   - Replace `uploadToSupabase()` with real API call
   - Add error handling

2. **Implement ETL Trigger**
   - Connect to `/api/etl/trigger`
   - Support all ETL modes
   - Add progress tracking

3. **Implement Status Polling**
   - Poll `/api/etl/status/{job_id}`
   - Update UI with progress
   - Handle completion/errors

4. **Add Progress Display**
   - Progress bar
   - Current step display
   - Error messages

**Deliverables:**
- ✅ ETL trigger working
- ✅ Status polling working
- ✅ Progress display functional

#### Week 2: Upload Integration

**Tasks:**
1. **Implement Upload Trigger**
   - Connect to `/api/upload/to-supabase`
   - Support all upload modes
   - Add progress tracking

2. **Implement Schema Generation**
   - Connect to `/api/upload/generate-schema`
   - Display schema file location
   - Add download link

3. **Add Upload Status**
   - Poll upload status
   - Display upload progress
   - Show completion status

**Deliverables:**
- ✅ Upload functionality working
- ✅ Schema generation working
- ✅ Upload status display

### Phase 2: Data Display (Week 3)

**Goal:** Display actual data from Supabase

#### Tasks

1. **Connect to Supabase**
   - Initialize Supabase client
   - Add authentication (if needed)
   - Test connection

2. **Game List Display**
   - Fetch games from `dim_schedule`
   - Display in table
   - Add filters (season, date, etc.)

3. **Table List Display**
   - List all ETL tables
   - Show table metadata (row count, columns)
   - Add table details view

4. **Data Browser**
   - Browse table data
   - Add pagination
   - Add search/filter

**Deliverables:**
- ✅ Game list functional
- ✅ Table list functional
- ✅ Data browser functional

### Phase 3: Game Management (Week 4)

**Goal:** Enable game creation and management

#### Tasks

1. **Create Game**
   - Form for new game
   - Validation
   - Save to Supabase

2. **Edit Game**
   - Load game data
   - Edit form
   - Update in Supabase

3. **Delete Game**
   - Confirmation dialog
   - Delete from Supabase
   - Update display

4. **Game Status**
   - Track game status (scheduled, in-progress, completed)
   - Display tracking status
   - Show ETL status

**Deliverables:**
- ✅ Create game working
- ✅ Edit game working
- ✅ Delete game working
- ✅ Game status tracking

### Phase 4: Enhanced Features (Week 5-6)

**Goal:** Add advanced features and polish

#### Tasks

1. **Staging Data Upload**
   - BLB table upload
   - Tracking data upload
   - Data validation

2. **Settings Management**
   - Save settings to localStorage/Supabase
   - User preferences
   - API configuration

3. **Notifications**
   - Toast notifications
   - Success/error messages
   - Job completion alerts

4. **UI Polish**
   - Loading states
   - Error states
   - Empty states
   - Responsive design

**Deliverables:**
- ✅ Staging upload working
- ✅ Settings functional
- ✅ Notifications working
- ✅ UI polished

---

## API Requirements

### Required Endpoints

#### ETL Endpoints (✅ Exists)

**`POST /api/etl/trigger`**
- Status: ✅ Implemented
- Purpose: Trigger ETL job
- Required for: ETL Control section

**`GET /api/etl/status/{job_id}`**
- Status: ✅ Implemented
- Purpose: Get ETL job status
- Required for: Status polling, progress display

**`GET /api/etl/history`**
- Status: ✅ Implemented
- Purpose: Get ETL job history
- Required for: Job history display

**`POST /api/etl/cancel/{job_id}`**
- Status: ✅ Implemented
- Purpose: Cancel ETL job
- Required for: Cancel button

#### Upload Endpoints (✅ Exists)

**`POST /api/upload/to-supabase`**
- Status: ✅ Implemented
- Purpose: Upload tables to Supabase
- Required for: Upload Control section

**`GET /api/upload/status/{job_id}`**
- Status: ✅ Implemented
- Purpose: Get upload status
- Required for: Upload progress display

**`POST /api/upload/generate-schema`**
- Status: ✅ Implemented
- Purpose: Generate schema SQL
- Required for: Schema generation button

#### Staging Endpoints (✅ Exists)

**`POST /api/staging/blb-tables/upload`**
- Status: ✅ Implemented
- Purpose: Upload BLB table data
- Required for: BLB data upload

**`PUT /api/staging/blb-tables/update`**
- Status: ✅ Implemented
- Purpose: Update BLB table data
- Required for: BLB data editing

**`GET /api/staging/blb-tables/list`**
- Status: ✅ Implemented
- Purpose: List BLB tables
- Required for: Table selection

**`POST /api/staging/tracking/upload`**
- Status: ✅ Implemented
- Purpose: Upload tracking data
- Required for: Tracking data upload

**`DELETE /api/staging/blb-tables/{table_name}`**
- Status: ✅ Implemented
- Purpose: Clear staging table
- Required for: Data cleanup

#### Game Management Endpoints (❌ Missing)

**`GET /api/games`**
- Status: ❌ Not implemented
- Purpose: List all games
- Required for: Game list display

**`POST /api/games`**
- Status: ❌ Not implemented
- Purpose: Create new game
- Required for: Create game functionality

**`GET /api/games/{game_id}`**
- Status: ❌ Not implemented
- Purpose: Get game details
- Required for: Game detail view

**`PUT /api/games/{game_id}`**
- Status: ❌ Not implemented
- Purpose: Update game
- Required for: Edit game functionality

**`DELETE /api/games/{game_id}`**
- Status: ❌ Not implemented
- Purpose: Delete game
- Required for: Delete game functionality

#### Data Browser Endpoints (❌ Missing)

**`GET /api/tables`**
- Status: ❌ Not implemented
- Purpose: List all tables
- Required for: Table list display

**`GET /api/tables/{table_name}`**
- Status: ❌ Not implemented
- Purpose: Get table data
- Required for: Data browser

**`GET /api/tables/{table_name}/schema`**
- Status: ❌ Not implemented
- Purpose: Get table schema
- Required for: Schema display

---

## Technical Specification

### Technology Stack

**Frontend:**
- HTML/CSS/JavaScript (current)
- OR: Convert to React/Next.js (future)

**API Integration:**
- Fetch API for HTTP requests
- WebSocket for real-time updates (future)

**State Management:**
- Local state (JavaScript variables)
- OR: React Context/Zustand (if converted to React)

### File Structure

```
ui/portal/
├── index.html              # Main portal page
├── js/
│   ├── config.js          # Configuration
│   ├── api.js             # API client
│   ├── etl.js             # ETL controls
│   ├── schema.js          # Schema generation
│   ├── sync.js            # Sync functionality
│   └── utils.js           # Utility functions
├── css/
│   └── portal.css         # Styles (if separated)
└── .env.local            # Environment variables
```

### Environment Variables

```bash
# ui/portal/.env.local
API_URL=http://localhost:8000
API_KEY=your-api-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
ADMIN_PASSWORD=your-secure-password
```

### Authentication (MVP)

**Simple Password Protection:**
```javascript
// ui/portal/js/auth.js
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'changeme';

function checkAuth() {
  const stored = localStorage.getItem('admin_authenticated');
  if (!stored || stored !== 'true') {
    showLoginModal();
  }
}

function showLoginModal() {
  // Create modal
  const modal = document.createElement('div');
  modal.className = 'auth-modal';
  modal.innerHTML = `
    <div class="auth-modal-content">
      <h2>Admin Portal Login</h2>
      <input type="password" id="adminPassword" placeholder="Enter password">
      <button onclick="handleLogin()">Login</button>
      <p id="authError" style="color: red; display: none;"></p>
    </div>
  `;
  document.body.appendChild(modal);
}

function handleLogin() {
  const password = document.getElementById('adminPassword').value;
  if (password === ADMIN_PASSWORD) {
    localStorage.setItem('admin_authenticated', 'true');
    document.querySelector('.auth-modal').remove();
  } else {
    document.getElementById('authError').style.display = 'block';
    document.getElementById('authError').textContent = 'Invalid password';
  }
}

// Check auth on page load
document.addEventListener('DOMContentLoaded', checkAuth);
```

**Production (Phase 2):**
Replace with Supabase Auth:
```javascript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function checkAuth() {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) {
    window.location.href = '/login';
  }
}
```

### Error Handling

**User-Friendly Error Messages:**
```javascript
// ui/portal/js/utils.js
function showError(message, details = null) {
  // Create error toast
  const toast = document.createElement('div');
  toast.className = 'error-toast';
  toast.innerHTML = `
    <div class="toast-content">
      <strong>Error:</strong> ${message}
      ${details ? `<br><small>${details}</small>` : ''}
    </div>
    <button onclick="this.parentElement.remove()">×</button>
  `;
  document.body.appendChild(toast);
  
  // Auto-remove after 5 seconds
  setTimeout(() => toast.remove(), 5000);
}

function showSuccess(message) {
  const toast = document.createElement('div');
  toast.className = 'success-toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}
```

### Logging System

**Enhanced Log Display:**
```javascript
// ui/portal/js/utils.js
function log(message, level = 'info') {
  const logArea = document.getElementById('etlLog');
  if (!logArea) return;

  const timestamp = new Date().toLocaleTimeString();
  const logLine = document.createElement('div');
  logLine.className = `log-line ${level}`;
  logLine.textContent = `[${timestamp}] ${message}`;
  
  logArea.appendChild(logLine);
  logArea.scrollTop = logArea.scrollHeight;

  // Keep only last 100 lines
  while (logArea.children.length > 100) {
    logArea.removeChild(logArea.firstChild);
  }
}
```

---

## Feature Checklist

### ETL Control

- [ ] Trigger ETL (full mode)
- [ ] Trigger ETL (single game mode)
- [ ] Trigger ETL (incremental mode)
- [ ] View ETL status
- [ ] View ETL history
- [ ] Cancel ETL job
- [ ] View ETL progress
- [ ] View ETL errors

### Upload Control

- [ ] Upload all tables
- [ ] Upload dimension tables
- [ ] Upload fact tables
- [ ] Upload specific tables
- [ ] View upload status
- [ ] Generate schema
- [ ] Download schema

### Game Management

- [ ] List games
- [ ] Create game
- [ ] Edit game
- [ ] Delete game
- [ ] View game details
- [ ] Filter games
- [ ] Search games

### Data Browser

- [ ] List tables
- [ ] View table data
- [ ] Filter table data
- [ ] Search table data
- [ ] Export table data
- [ ] View table schema

### Staging

- [ ] Upload BLB tables
- [ ] Update BLB tables
- [ ] Upload tracking data
- [ ] View staging data
- [ ] Clear staging tables

### Settings

- [ ] API URL configuration
- [ ] Supabase configuration
- [ ] User preferences
- [ ] Save settings
- [ ] Load settings

---

## Implementation Priority

### High Priority (Week 1-2)

1. **ETL Endpoints** - ✅ Already implemented
2. **Upload Endpoints** - ✅ Already implemented
3. **Staging Endpoints** - ✅ Already implemented
4. **Complete API Integration** - ⚠️ Partial, needs completion

### Medium Priority (Week 3-4)

5. **Game Management Endpoints** - ❌ Need to implement
6. **Data Browser Endpoints** - ❌ Need to implement
7. **Supabase Data Display** - ❌ Need to implement

### Low Priority (Future)

8. **Authentication Endpoints** - ❌ Future feature
9. **User Management Endpoints** - ❌ Future feature
10. **WebSocket Real-Time Updates** - ❌ Future feature

---

## Success Criteria

### Phase 1 Complete

- ✅ Can trigger ETL from portal
- ✅ Can see ETL status in real-time
- ✅ Can upload to Supabase
- ✅ Can see upload progress

### Phase 2 Complete

- ✅ Can view game list
- ✅ Can view table list
- ✅ Can browse table data

### Phase 3 Complete

- ✅ Can create games
- ✅ Can edit games
- ✅ Can delete games

### Phase 4 Complete

- ✅ All features functional
- ✅ UI polished
- ✅ Error handling complete
- ✅ Ready for production

---

## Related Documentation

- [API.md](../api/API.md) - Complete API reference
- [ETL.md](../etl/ETL.md) - ETL process documentation
- [Dashboard.md](../dashboard/DASHBOARD.md) - Dashboard documentation

---

*Last Updated: 2026-01-15*
