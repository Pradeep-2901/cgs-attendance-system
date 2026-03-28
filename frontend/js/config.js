/**
 * Configuration Management
 * Handles API URL configuration based on environment
 */

// Automatically set API URL based on environment
function initializeConfig() {
    const hostname = window.location.hostname;
    
    let apiUrl;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        apiUrl = 'http://localhost:5000';
    } else if (hostname.includes('netlify.app')) {
        // Use Render backend URL for production
        apiUrl = localStorage.getItem('API_URL') || 'https://cgs-backend.onrender.com';
    } else {
        apiUrl = localStorage.getItem('API_URL') || `https://${hostname}:5000`;
    }
    
    // Store in localStorage for access across all pages
    localStorage.setItem('API_URL', apiUrl);
    
    console.log('[CONFIG] API URL:', apiUrl);
    console.log('[CONFIG] Environment:', hostname);
    
    return apiUrl;
}

// Get API URL from storage or config
function getApiUrl() {
    return localStorage.getItem('API_URL') || 'http://localhost:5000';
}

// Check if user is authenticated (from session)
function isAuthenticated() {
    // Check if user_id exists in localStorage
    return !!localStorage.getItem('user_id');
}

// Get current user info
function getCurrentUser() {
    return {
        user_id: localStorage.getItem('user_id'),
        username: localStorage.getItem('username'),
        role: localStorage.getItem('user_role'),
        name: localStorage.getItem('user_name')
    };
}

// Store current user info
function setCurrentUser(userData) {
    localStorage.setItem('user_id', userData.user_id || '');
    localStorage.setItem('username', userData.username || '');
    localStorage.setItem('user_role', userData.role || 'employee');
    localStorage.setItem('user_name', userData.name || data.username);
}

// Clear user session
function clearUserSession() {
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_name');
}

// Initialize config on page load
document.addEventListener('DOMContentLoaded', initializeConfig);
