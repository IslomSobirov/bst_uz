// API Configuration
// Use environment variable if available, otherwise fallback to localhost:8001
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

// Ensure base URL doesn't end with a slash
const cleanBaseUrl = API_BASE_URL.replace(/\/$/, '');

// Helper function to build API URLs
export const getApiUrl = (endpoint) => {
  // Ensure endpoint starts with a slash
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${cleanBaseUrl}${cleanEndpoint}`;
};

export default cleanBaseUrl;
