// API Configuration
const API_CONFIGS = {
  production: {
    baseURL: 'https://etkinlik.hautmedia.com/api/v1',
  },
  development: {
    baseURL: 'http://localhost:8000/api/v1',
  },
};

// Determine environment
const isProduction = window.location.hostname === 'etkinlik.hautmedia.com' ||
                     window.location.hostname.includes('hautmedia.com') ||
                     window.location.protocol === 'https:';

// Export the appropriate config
export const API_CONFIG = isProduction ? API_CONFIGS.production : API_CONFIGS.development;

// Export base URL directly
export const API_BASE_URL = API_CONFIG.baseURL;

console.log('API Configuration:', {
  hostname: window.location.hostname,
  isProduction,
  apiUrl: API_BASE_URL,
});