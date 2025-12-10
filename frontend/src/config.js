// Detect environment - if running on localhost, it's local development
const isProduction = window.location.hostname !== 'localhost' && 
                     window.location.hostname !== '127.0.0.1';

// API Configuration
export const API_BASE_URL = isProduction 
  ? '/api'  // On cloud: use proxy
  : 'http://localhost:8000';  // Local: direct to FastAPI

console.log('Environment:', isProduction ? 'PRODUCTION (Cloud)' : 'DEVELOPMENT (Local)');
console.log('API Base URL:', API_BASE_URL);