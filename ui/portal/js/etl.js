/**
 * ETL Controls for Admin Portal
 * Handles ETL triggering, status polling, and UI updates
 */

let currentJobId = null;
let statusInterval = null;
let etlRunning = false;

/**
 * Trigger ETL job via API
 */
async function runETL() {
  const mode = document.getElementById('etlMode').value;
  const clean = document.getElementById('etlClean').checked;
  const verify = document.getElementById('etlVerify').checked;
  const source = document.getElementById('etlSource').value;
  
  // Get game IDs (support multiple, comma-separated)
  let gameIds = null;
  const gameIdInput = document.getElementById('etlGameId').value.trim();
  if (gameIdInput) {
    gameIds = gameIdInput.split(',').map(g => parseInt(g.trim())).filter(g => !isNaN(g));
    if (gameIds.length === 0) {
      log('Error: Invalid game ID(s)', 'error');
      return;
    }
  } else if (mode === 'single') {
    log('Error: Game ID required for single mode', 'error');
    return;
  }
  
  // Get exclude game IDs
  let excludeGameIds = null;
  const excludeInput = document.getElementById('etlExcludeGames').value.trim();
  if (excludeInput) {
    excludeGameIds = excludeInput.split(',').map(g => parseInt(g.trim())).filter(g => !isNaN(g));
    if (excludeGameIds.length === 0) {
      excludeGameIds = null;
    }
  }
  
  // Show loading state
  document.getElementById('etlStatusBadge').textContent = 'STARTING';
  document.getElementById('etlStatusBadge').className = 'badge badge-warn';
  document.getElementById('etlProgress').style.display = 'block';
  document.getElementById('stopBtn').disabled = false;
  etlRunning = true;
  
  log('Starting ETL pipeline...', 'info');
  log(`Mode: ${mode}, Source: ${source}, Clean: ${clean}, Verify: ${verify}`);
  if (gameIds) log(`Game IDs: ${gameIds.join(', ')}`, 'info');
  if (excludeGameIds) log(`Excluding: ${excludeGameIds.join(', ')}`, 'info');
  
  try {
    // Trigger ETL via API with flexible options
    const response = await api.triggerETL(mode, gameIds, {
      wipe: clean,
      validate: verify,
      source: source,
      exclude_game_ids: excludeGameIds
    });
    
    currentJobId = response.job_id;
    log(`ETL job started: ${currentJobId}`, 'info');
    
    // Start polling for status
    startStatusPolling(currentJobId);
    
  } catch (error) {
    log(`Failed to start ETL: ${error.message}`, 'error');
    document.getElementById('etlStatusBadge').textContent = 'ERROR';
    document.getElementById('etlStatusBadge').className = 'badge badge-danger';
    document.getElementById('stopBtn').disabled = true;
    etlRunning = false;
  }
}

/**
 * Start polling for job status
 */
function startStatusPolling(jobId) {
  // Clear any existing interval
  if (statusInterval) {
    clearInterval(statusInterval);
  }
  
  // Poll every 2 seconds
  statusInterval = setInterval(async () => {
    try {
      const status = await api.getETLStatus(jobId);
      updateETLStatus(status);
      
      // Stop polling if job is complete
      if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
        stopStatusPolling();
        etlRunning = false;
        document.getElementById('stopBtn').disabled = true;
      }
    } catch (error) {
      log(`Error checking status: ${error.message}`, 'error');
    }
  }, 2000);
  
  // Also check immediately
  api.getETLStatus(jobId).then(updateETLStatus).catch(err => {
    log(`Error getting initial status: ${err.message}`, 'error');
  });
}

/**
 * Stop status polling
 */
function stopStatusPolling() {
  if (statusInterval) {
    clearInterval(statusInterval);
    statusInterval = null;
  }
}

/**
 * Update UI with job status
 */
function updateETLStatus(status) {
  // Update badge
  const badge = document.getElementById('etlStatusBadge');
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
  const progressFill = document.getElementById('etlProgressFill');
  if (progressFill && status.progress !== null && status.progress !== undefined) {
    progressFill.style.width = `${status.progress}%`;
  }
  
  // Update stats
  if (status.tables_created !== null && status.tables_created !== undefined) {
    document.getElementById('etlTablesProcessed').textContent = status.tables_created;
  }
  
  // Update log with current step
  if (status.current_step) {
    log(status.current_step, 'info');
  }
  
  // Update errors
  if (status.errors && status.errors.length > 0) {
    status.errors.forEach(err => log(err, 'error'));
  }
}

/**
 * Cancel running ETL job
 */
async function stopETL() {
  if (!currentJobId) {
    log('No active job to cancel', 'warn');
    return;
  }
  
  try {
    await api.cancelETL(currentJobId);
    log('Cancellation requested...', 'warn');
    stopStatusPolling();
    etlRunning = false;
    document.getElementById('stopBtn').disabled = true;
  } catch (error) {
    log(`Failed to cancel job: ${error.message}`, 'error');
  }
}
