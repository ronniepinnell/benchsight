/**
 * API Client for BenchSight ETL API
 * Handles all API communication
 */

class APIClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'API request failed' }));
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Health endpoints
  async health() {
    return this.request('/api/health');
  }

  async status() {
    return this.request('/api/status');
  }

  // ETL endpoints
  async triggerETL(mode, gameIds = null, options = {}) {
    // Extract exclude_game_ids and source from options to pass as top-level fields
    const excludeGameIds = options.exclude_game_ids || null;
    const source = options.source || null;
    const cleanOptions = { ...options };
    delete cleanOptions.exclude_game_ids;
    delete cleanOptions.source;
    
    return this.request('/api/etl/trigger', {
      method: 'POST',
      body: JSON.stringify({
        mode,
        game_ids: gameIds,
        exclude_game_ids: excludeGameIds,
        source: source,
        options: cleanOptions
      })
    });
  }

  async getETLStatus(jobId) {
    return this.request(`/api/etl/status/${jobId}`);
  }

  async getETLHistory(limit = 10, status = null) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (status) params.append('status', status);
    return this.request(`/api/etl/history?${params}`);
  }

  async cancelETL(jobId) {
    return this.request(`/api/etl/cancel/${jobId}`, {
      method: 'POST'
    });
  }

  // Upload/Schema endpoints
  async generateSchema(options = {}) {
    return this.request('/api/upload/generate-schema', {
      method: 'POST',
      body: JSON.stringify({ options })
    });
  }

  async getSchemaStatus(jobId) {
    return this.request(`/api/upload/status/${jobId}`);
  }

  async uploadToSupabase(tables = null, mode = 'all', options = {}) {
    return this.request('/api/upload/to-supabase', {
      method: 'POST',
      body: JSON.stringify({
        tables,
        mode,
        options
      })
    });
  }

  async getUploadStatus(jobId) {
    return this.request(`/api/upload/status/${jobId}`);
  }
}

// Create singleton instance
const api = new APIClient(API_CONFIG.baseUrl);
