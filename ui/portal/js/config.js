/**
 * Admin Portal Configuration
 * Configuration for API and Supabase connections
 */

// API Configuration
const API_CONFIG = {
  baseUrl: 'http://localhost:8000',  // ETL API base URL
  timeout: 30000  // 30 seconds
};

// For future: Can be overridden via environment variables or settings
// const API_CONFIG = {
//   baseUrl: window.API_URL || 'http://localhost:8000',
//   timeout: 30000
// };
