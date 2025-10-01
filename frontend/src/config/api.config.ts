// API Configuration
const API_CONFIGS = {
  production: {
    baseURL: 'https://api-etkinlik.hautmedia.com/api/v1',
  },
  development: {
    baseURL: 'http://localhost:8000/api/v1',
  },
};

// Determine environment
// Force development mode for localhost, even if using HTTPS
const isProduction = (window.location.hostname === 'etkinlik.hautmedia.com' ||
                     window.location.hostname.includes('hautmedia.com')) &&
                     !window.location.hostname.includes('localhost') &&
                     !window.location.hostname.includes('127.0.0.1');

// Export the appropriate config
export const API_CONFIG = isProduction ? API_CONFIGS.production : API_CONFIGS.development;

// Export base URL directly
export const API_BASE_URL = API_CONFIG.baseURL;

console.log('API Configuration:', {
  hostname: window.location.hostname,
  isProduction,
  apiUrl: API_BASE_URL,
});