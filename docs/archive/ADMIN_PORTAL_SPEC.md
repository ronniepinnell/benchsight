# Admin Portal Backend Technical Specification

**Complete specification for admin portal backend integration**

Last Updated: 2026-01-13  
Timeline: Week 2-3 of Phase 1  
Priority: 🔴 CRITICAL

---

## Overview

The admin portal (`ui/portal/index.html`) currently has a UI mockup but no backend. This spec defines how to connect it to the ETL API and add real functionality.

---

## Current State

### What Exists
- ✅ UI design complete (`ui/portal/index.html`)
- ✅ Mockup of ETL controls
- ✅ Mockup of game management
- ✅ UI components styled

### What's Missing
- ❌ No backend connection
- ❌ All buttons are placeholders
- ❌ No real data display
- ❌ No authentication

---

## Architecture

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
```

---

## API Integration

### Base Configuration

```javascript
// ui/portal/js/config.js
const API_CONFIG = {
  baseUrl: process.env.API_URL || 'http://localhost:8000',
  apiKey: process.env.API_KEY || null,  // For MVP
  timeout: 30000  // 30 seconds
};

// Supabase config (for game data)
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

  // Game endpoints
  async getGames(status = null) {
    const url = status ? `/api/games?status=${status}` : '/api/games';
    return this.request(url);
  }

  async getGame(gameId) {
    return this.request(`/api/games/${gameId}`);
  }

  // Upload endpoints
  async uploadToSupabase(tables = null, mode = 'all') {
    return this.request('/api/upload/to-supabase', {
      method: 'POST',
      body: JSON.stringify({ tables, mode })
    });
  }
}

// Export singleton
const api = new APIClient(API_CONFIG.baseUrl, API_CONFIG.apiKey);
```

---

## ETL Integration

### Connect ETL Controls

```javascript
// ui/portal/js/etl.js
const api = new APIClient(API_CONFIG.baseUrl, API_CONFIG.apiKey);

let currentJobId = null;
let statusInterval = null;

async function runETL() {
  const mode = document.getElementById('etlMode').value;
  const clean = document.getElementById('etlClean').checked;
  const sync = document.getElementById('etlSync').checked;
  const verify = document.getElementById('etlVerify').checked;
  
  const gameId = document.getElementById('etlGameId').value;
  const gameIds = gameId ? [parseInt(gameId)] : null;

  // Show loading state
  document.getElementById('etlStatusBadge').textContent = 'STARTING';
  document.getElementById('etlStatusBadge').className = 'badge badge-warn';
  document.getElementById('etlProgress').style.display = 'block';
  document.getElementById('stopBtn').disabled = false;

  try {
    // Trigger ETL
    const response = await api.triggerETL(mode, gameIds, {
      wipe: clean,
      upload_to_supabase: sync,
      validate: verify
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
        document.getElementById('stopBtn').disabled = true;
      }
    } catch (error) {
      log(`Error checking status: ${error.message}`, 'error');
    }
  }, 2000);  // Poll every 2 seconds
}

function updateETLStatus(status) {
  // Update badge
  const badge = document.getElementById('etlStatusBadge');
  badge.textContent = status.status.toUpperCase();
  
  if (status.status === 'completed') {
    badge.className = 'badge badge-success';
  } else if (status.status === 'failed') {
    badge.className = 'badge badge-danger';
  } else {
    badge.className = 'badge badge-warn';
  }

  // Update progress
  const progressFill = document.getElementById('etlProgressFill');
  progressFill.style.width = `${status.progress || 0}%`;

  // Update stats
  if (status.tables_created !== undefined) {
    document.getElementById('etlTablesProcessed').textContent = status.tables_created;
  }
  if (status.current_step) {
    log(status.current_step, 'info');
  }

  // Update log
  if (status.errors && status.errors.length > 0) {
    status.errors.forEach(err => log(err, 'error'));
  }
}

function stopETL() {
  if (currentJobId && statusInterval) {
    clearInterval(statusInterval);
    // TODO: Implement cancel endpoint
    log('ETL job stopped', 'warn');
    document.getElementById('etlStatusBadge').textContent = 'STOPPED';
    document.getElementById('stopBtn').disabled = true;
  }
}

// Wire up button
document.getElementById('runETLBtn').addEventListener('click', runETL);
document.getElementById('stopBtn').addEventListener('click', stopETL);
```

---

## Game Management Integration

### Connect Game List

```javascript
// ui/portal/js/games.js
const api = new APIClient(API_CONFIG.baseUrl, API_CONFIG.apiKey);

async function loadGames() {
  try {
    const games = await api.getGames();
    displayGames(games);
  } catch (error) {
    console.error('Failed to load games:', error);
  }
}

function displayGames(games) {
  const tbody = document.getElementById('gamesTableBody');
  tbody.innerHTML = '';

  games.forEach(game => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${game.game_id}</td>
      <td>${game.game_date || 'N/A'}</td>
      <td>${game.home_team || 'N/A'}</td>
      <td>${game.away_team || 'N/A'}</td>
      <td><span class="badge ${getStatusBadgeClass(game.status)}">${game.status || 'Unknown'}</span></td>
      <td>
        <button onclick="viewGame(${game.game_id})">View</button>
        <button onclick="runETLForGame(${game.game_id})">Run ETL</button>
      </td>
    `;
    tbody.appendChild(row);
  });
}

function getStatusBadgeClass(status) {
  const statusMap = {
    'tracked': 'badge-success',
    'pending': 'badge-warn',
    'error': 'badge-danger'
  };
  return statusMap[status] || 'badge';
}

async function runETLForGame(gameId) {
  try {
    const response = await api.triggerETL('single', [gameId], {
      upload_to_supabase: true
    });
    log(`ETL started for game ${gameId}: ${response.job_id}`, 'info');
    // Switch to ETL section to show progress
    showSection('etl');
  } catch (error) {
    log(`Failed to start ETL for game: ${error.message}`, 'error');
  }
}

// Load games on page load
document.addEventListener('DOMContentLoaded', loadGames);
```

---

## System Status Integration

### Connect Status Display

```javascript
// ui/portal/js/status.js
const api = new APIClient(API_CONFIG.baseUrl, API_CONFIG.apiKey);
const supabase = createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.anonKey);

async function updateSystemStatus() {
  try {
    // Get API status
    const apiStatus = await api.request('/api/status');
    
    // Get Supabase stats
    const { count: tableCount } = await supabase
      .from('information_schema.tables')
      .select('*', { count: 'exact', head: true })
      .eq('table_schema', 'public');

    const { count: gameCount } = await supabase
      .from('dim_schedule')
      .select('*', { count: 'exact', head: true });

    const { count: goalCount } = await supabase
      .from('fact_events')
      .select('*', { count: 'exact', head: true })
      .eq('event_type', 'Goal')
      .eq('event_detail', 'Goal_Scored');

    // Update UI
    document.getElementById('statTables').textContent = tableCount || '--';
    document.getElementById('statGames').textContent = gameCount || '--';
    document.getElementById('statGoals').textContent = goalCount || '--';

    // Update Supabase connection status
    const sbStatus = document.getElementById('sbStatus');
    sbStatus.className = 'status-dot green';
    document.getElementById('sbStatusText').textContent = 'Connected';

  } catch (error) {
    console.error('Failed to update status:', error);
    const sbStatus = document.getElementById('sbStatus');
    sbStatus.className = 'status-dot red';
    document.getElementById('sbStatusText').textContent = 'Disconnected';
  }
}

// Update status every 30 seconds
setInterval(updateSystemStatus, 30000);
updateSystemStatus();  // Initial load
```

---

## Authentication (MVP)

### Simple Password Protection

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

### Production (Phase 2)

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

---

## File Structure

```
ui/portal/
├── index.html              # Main portal page
├── js/
│   ├── config.js          # Configuration
│   ├── api.js             # API client
│   ├── etl.js             # ETL controls
│   ├── games.js           # Game management
│   ├── status.js          # System status
│   ├── auth.js            # Authentication
│   └── utils.js           # Utility functions
├── css/
│   └── portal.css        # Styles (if separated)
└── .env.local            # Environment variables
```

---

## Environment Variables

```bash
# ui/portal/.env.local
API_URL=http://localhost:8000
API_KEY=your-api-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
ADMIN_PASSWORD=your-secure-password
```

---

## Error Handling

### User-Friendly Error Messages

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

---

## Logging System

### Enhanced Log Display

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

function clearLog() {
  const logArea = document.getElementById('etlLog');
  if (logArea) {
    logArea.innerHTML = '';
    log('[INFO] Log cleared', 'info');
  }
}
```

---

## Real-Time Updates

### WebSocket Support (Optional, Phase 2)

```javascript
// ui/portal/js/websocket.js
function connectWebSocket(jobId) {
  const ws = new WebSocket(`ws://localhost:8000/ws/etl/${jobId}`);
  
  ws.onmessage = (event) => {
    const status = JSON.parse(event.data);
    updateETLStatus(status);
  };
  
  ws.onerror = (error) => {
    log('WebSocket error, falling back to polling', 'warn');
    startStatusPolling(jobId);
  };
  
  ws.onclose = () => {
    log('WebSocket closed', 'info');
  };
}
```

---

## Testing Checklist

### ETL Integration
- [ ] Can trigger full ETL from UI
- [ ] Can trigger single-game ETL
- [ ] Progress updates in real-time
- [ ] Status badge updates correctly
- [ ] Logs display properly
- [ ] Errors show user-friendly messages
- [ ] Can cancel running ETL

### Game Management
- [ ] Game list loads from API
- [ ] Can view game details
- [ ] Can trigger ETL for specific game
- [ ] Game status updates correctly

### System Status
- [ ] Status updates automatically
- [ ] Supabase connection status accurate
- [ ] Stats display correctly
- [ ] Handles connection errors gracefully

### Authentication
- [ ] Login modal appears when not authenticated
- [ ] Can login with correct password
- [ ] Rejects incorrect password
- [ ] Session persists across page reloads

---

## Implementation Timeline

### Day 1: API Client & ETL Integration
- Create `js/api.js` with API client
- Create `js/etl.js` with ETL controls
- Connect trigger button
- Test ETL trigger

### Day 2: Status Polling & UI Updates
- Implement status polling
- Update progress bar
- Update status badges
- Display logs

### Day 3: Game Management
- Create `js/games.js`
- Connect game list
- Add game actions
- Test game management

### Day 4: System Status & Polish
- Create `js/status.js`
- Connect status display
- Add error handling
- Polish UI

### Day 5: Authentication & Testing
- Add authentication
- Test all features
- Fix bugs
- Document usage

---

## Security Considerations

### MVP (Phase 1)
- Simple password protection
- API key in environment variable
- HTTPS in production

### Production (Phase 2)
- Supabase Auth integration
- JWT tokens
- Role-based access control
- Rate limiting on API

---

## Success Criteria

### Week 2-3 Completion
- [ ] Admin portal connects to ETL API
- [ ] Can trigger ETL from UI
- [ ] Real-time status updates work
- [ ] Game management functional
- [ ] System status displays correctly
- [ ] Authentication working
- [ ] Error handling robust
- [ ] UI polished and responsive

---

## Next Steps After Integration

1. **Add WebSocket for real-time** (Phase 2)
2. **Add job history UI** (Phase 2)
3. **Add game creation UI** (Phase 2)
4. **Add user management** (Phase 2)
5. **Add advanced ETL options** (Phase 2)

---

*Specification created: 2026-01-13*
