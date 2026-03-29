/**
 * API Service Layer
 * Centralized API calls with proper error handling
 */

const getApiUrl = () => {
  const hostname = window.location.hostname;
  
  // Netlify production
  if (hostname.includes('netlify.app')) {
    return 'https://cgs-attendance-system.onrender.com';
  }
  
  // Localhost
  if (hostname.includes('localhost') || hostname.includes('127.0.0.1')) {
    return 'http://localhost:5000';
  }
  
  // Default
  return import.meta.env.VITE_API_URL || 'https://cgs-attendance-system.onrender.com';
};

const API_BASE = getApiUrl();

export async function apiCall(endpoint, method = 'GET', data = null) {
  const url = API_BASE + endpoint;
  
  const options = {
    method,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  try {
    console.log(`[API] ${method} ${endpoint}`);
    const response = await fetch(url, options);
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.message || `API Error: ${response.status}`);
    }

    return result;
  } catch (error) {
    console.error(`[API Error] ${method} ${endpoint}:`, error.message);
    throw error;
  }
}

export async function uploadFile(endpoint, formData) {
  const url = API_BASE + endpoint;
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      credentials: 'include',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`[Upload Error] ${endpoint}:`, error.message);
    throw error;
  }
}

export function getApiBaseUrl() {
  return API_BASE;
}
