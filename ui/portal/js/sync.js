/**
 * Data Sync for Admin Portal
 * Handles syncing data to Supabase
 */

let syncJobId = null;
let syncStatusInterval = null;
let syncRunning = false;

/**
 * Sync data to Supabase
 */
async function syncToSupabase() {
  const mode = document.getElementById('syncMode').value;
  const tablesInput = document.getElementById('syncTables').value.trim();
  const clean = document.getElementById('syncClean').checked;
  
  // Parse tables if provided
  let tables = null;
  if (tablesInput) {
    tables = tablesInput.split(',').map(t => t.trim()).filter(t => t);
  }
  
  // Show loading state
  document.getElementById('syncStatusBadge').textContent = 'STARTING';
  document.getElementById('syncStatusBadge').className = 'badge badge-warn';
  document.getElementById('syncProgress').style.display = 'block';
  document.getElementById('stopSyncBtn').disabled = false;
  syncRunning = true;
  
  syncLog('Starting Supabase sync...', 'info');
  syncLog(`Mode: ${mode}, Tables: ${tables ? tables.length : 'all'}, Clean: ${clean}`);
  
  try {
    const response = await api.uploadToSupabase(tables, mode, {
      clean
    });
    
    syncJobId = response.job_id;
    syncLog(`Sync job started: ${syncJobId}`, 'info');
    
    // Start polling for status
    startSyncStatusPolling(syncJobId);
    
  } catch (error) {
    syncLog(`Failed to start sync: ${error.message}`, 'error');
    document.getElementById('syncStatusBadge').textContent = 'ERROR';
    document.getElementById('syncStatusBadge').className = 'badge badge-danger';
    document.getElementById('stopSyncBtn').disabled = true;
    syncRunning = false;
  }
}

/**
 * Start polling for sync job status
 */
function startSyncStatusPolling(jobId) {
  if (syncStatusInterval) {
    clearInterval(syncStatusInterval);
  }
  
  syncStatusInterval = setInterval(async () => {
    try {
      const status = await api.getUploadStatus(jobId);
      updateSyncStatus(status);
      
      if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
        stopSyncStatusPolling();
        syncRunning = false;
        document.getElementById('stopSyncBtn').disabled = true;
      }
    } catch (error) {
      syncLog(`Error checking sync status: ${error.message}`, 'error');
    }
  }, 2000);
  
  // Also check immediately
  api.getUploadStatus(jobId).then(updateSyncStatus).catch(err => {
    syncLog(`Error getting initial sync status: ${err.message}`, 'error');
  });
}

/**
 * Stop sync status polling
 */
function stopSyncStatusPolling() {
  if (syncStatusInterval) {
    clearInterval(syncStatusInterval);
    syncStatusInterval = null;
  }
}

/**
 * Update UI with sync job status
 */
function updateSyncStatus(status) {
  const badge = document.getElementById('syncStatusBadge');
  badge.textContent = status.status.toUpperCase();
  
  if (status.status === 'completed') {
    badge.className = 'badge badge-success';
  } else if (status.status === 'failed') {
    badge.className = 'badge badge-danger';
  } else if (status.status === 'cancelled') {
    badge.className = 'badge badge-danger';
  } else {
    badge.className = 'badge badge-warn';
  }
  
  // Update progress bar
  const progressFill = document.getElementById('syncProgressFill');
  if (progressFill && status.progress !== null && status.progress !== undefined) {
    progressFill.style.width = `${status.progress}%`;
  }
  
  // Update stats
  if (status.tables_created !== null && status.tables_created !== undefined) {
    document.getElementById('syncTablesProcessed').textContent = status.tables_created;
  }
  
  // Update log
  if (status.current_step) {
    syncLog(status.current_step, 'info');
  }
  
  if (status.errors && status.errors.length > 0) {
    status.errors.forEach(err => syncLog(err, 'error'));
  }
}

/**
 * Cancel running sync job
 */
async function stopSync() {
  if (!syncJobId) {
    syncLog('No active sync job to cancel', 'warn');
    return;
  }
  
  try {
    // Note: Upload jobs might not have cancel endpoint, but we can stop polling
    syncLog('Stopping sync job polling...', 'warn');
    stopSyncStatusPolling();
    syncRunning = false;
    document.getElementById('stopSyncBtn').disabled = true;
  } catch (error) {
    syncLog(`Failed to stop sync: ${error.message}`, 'error');
  }
}

/**
 * Log message to sync log area
 */
function syncLog(msg, level = '') {
  const logArea = document.getElementById('syncLog');
  const time = new Date().toLocaleTimeString();
  logArea.innerHTML += `<div class="log-line ${level}">[${time}] ${msg}</div>`;
  logArea.scrollTop = logArea.scrollHeight;
}

/**
 * Clear sync log
 */
function clearSyncLog() {
  document.getElementById('syncLog').innerHTML = '<div class="log-line info">[INFO] Log cleared</div>';
}
