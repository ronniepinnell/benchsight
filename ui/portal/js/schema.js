/**
 * Schema Management for Admin Portal
 * Handles schema generation and loading
 */

let schemaJobId = null;
let schemaStatusInterval = null;

/**
 * Generate schema SQL
 */
async function generateSchema() {
  try {
    document.getElementById('schemaStatusBadge').textContent = 'STARTING';
    document.getElementById('schemaStatusBadge').className = 'badge badge-warn';
    document.getElementById('schemaProgress').style.display = 'block';
    
    schemaLog('Generating schema SQL...', 'info');
    
    const response = await api.generateSchema({});
    schemaJobId = response.job_id;
    schemaLog(`Schema generation job started: ${schemaJobId}`, 'info');
    
    // Start polling for status
    startSchemaStatusPolling(schemaJobId);
    
  } catch (error) {
    schemaLog(`Failed to generate schema: ${error.message}`, 'error');
    document.getElementById('schemaStatusBadge').textContent = 'ERROR';
    document.getElementById('schemaStatusBadge').className = 'badge badge-danger';
  }
}

/**
 * Start polling for schema job status
 */
function startSchemaStatusPolling(jobId) {
  if (schemaStatusInterval) {
    clearInterval(schemaStatusInterval);
  }
  
  schemaStatusInterval = setInterval(async () => {
    try {
      const status = await api.getSchemaStatus(jobId);
      updateSchemaStatus(status);
      
      if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
        stopSchemaStatusPolling();
      }
    } catch (error) {
      schemaLog(`Error checking schema status: ${error.message}`, 'error');
    }
  }, 2000);
  
  // Also check immediately
  api.getSchemaStatus(jobId).then(updateSchemaStatus).catch(err => {
    schemaLog(`Error getting initial schema status: ${err.message}`, 'error');
  });
}

/**
 * Stop schema status polling
 */
function stopSchemaStatusPolling() {
  if (schemaStatusInterval) {
    clearInterval(schemaStatusInterval);
    schemaStatusInterval = null;
  }
}

/**
 * Update UI with schema job status
 */
function updateSchemaStatus(status) {
  const badge = document.getElementById('schemaStatusBadge');
  badge.textContent = status.status.toUpperCase();
  
  if (status.status === 'completed') {
    badge.className = 'badge badge-success';
    if (status.tables_created !== null && status.tables_created !== undefined) {
      document.getElementById('schemaTablesGenerated').textContent = status.tables_created;
    }
  } else if (status.status === 'failed') {
    badge.className = 'badge badge-danger';
  } else {
    badge.className = 'badge badge-warn';
  }
  
  // Update progress bar
  const progressFill = document.getElementById('schemaProgressFill');
  if (progressFill && status.progress !== null && status.progress !== undefined) {
    progressFill.style.width = `${status.progress}%`;
  }
  
  // Update log
  if (status.current_step) {
    schemaLog(status.current_step, 'info');
  }
  
  if (status.errors && status.errors.length > 0) {
    status.errors.forEach(err => schemaLog(err, 'error'));
  }
}

/**
 * Log message (uses global log function for now)
 */
function schemaLog(msg, level = '') {
  // Use global log function if available, otherwise console.log
  if (typeof log === 'function') {
    log(`[SCHEMA] ${msg}`, level);
  } else {
    console.log(`[SCHEMA] ${msg}`);
  }
}
