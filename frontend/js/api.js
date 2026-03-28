/**
 * Centralized API Client
 * Handles all communication with the backend
 * 
 * Usage:
 *   await apiCall('/login', 'POST', { username: 'test', password: 'test' });
 *   await uploadFile('/checkin', formData);
 */

/**
 * Make an API call to the backend
 * @param {string} endpoint - API endpoint (e.g., '/login')
 * @param {string} method - HTTP method (GET, POST, PUT, DELETE)
 * @param {object} data - Request body data (optional)
 * @returns {Promise<object>} - Response from server
 */
async function apiCall(endpoint, method = 'GET', data = null) {
    const apiBase = getApiUrl();
    const url = apiBase + endpoint;
    
    const options = {
        method: method,
        credentials: 'include', // CRITICAL: Send session cookies
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
        
        // Check for session expiration
        if (response.status === 403 && result.message && result.message.includes('login required')) {
            console.warn('[API] Session expired - redirecting to login');
            clearUserSession();
            window.location.href = './index.html';
            return { status: 'error', message: 'Session expired. Please login again.' };
        }
        
        console.log(`[API] Response:`, result);
        return result;
    } catch (error) {
        console.error('[API] Error:', error);
        return {
            status: 'error',
            message: `Network error: ${error.message}`
        };
    }
}

/**
 * Upload file(s) to backend
 * @param {string} endpoint - API endpoint
 * @param {FormData} formData - Form data with files
 * @returns {Promise<object>} - Response from server
 */
async function uploadFile(endpoint, formData) {
    const apiBase = getApiUrl();
    const url = apiBase + endpoint;
    
    try {
        console.log(`[API] POST ${endpoint} (file upload)`);
        const response = await fetch(url, {
            method: 'POST',
            credentials: 'include', // Important: Include session cookies
            body: formData
            // Don't set Content-Type header - let browser set it with boundary
        });
        
        const result = await response.json();
        console.log(`[API] Response:`, result);
        
        if (response.status === 403) {
            console.warn('[API] Session expired - redirecting to login');
            clearUserSession();
            window.location.href = './index.html';
        }
        
        return result;
    } catch (error) {
        console.error('[API] Error:', error);
        return {
            status: 'error',
            message: `Network error: ${error.message}`
        };
    }
}

/**
 * Fetch JSON data from backend
 * @param {string} endpoint - API endpoint
 * @returns {Promise<object>} - Response data
 */
async function fetchData(endpoint) {
    return apiCall(endpoint, 'GET');
}

/**
 * POST data to backend
 * @param {string} endpoint - API endpoint
 * @param {object} data - Data to send
 * @returns {Promise<object>} - Response data
 */
async function postData(endpoint, data) {
    return apiCall(endpoint, 'POST', data);
}

/**
 * Show notification/toast message
 * @param {string} message - Message to display
 * @param {string} type - Type: 'success', 'error', 'info', 'warning'
 * @param {number} duration - Duration in milliseconds
 */
function showNotification(message, type = 'info', duration = 3000) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
        color: white;
        border-radius: 4px;
        z-index: 10000;
        font-size: 14px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after duration
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

/**
 * Redirect to page (with preserved query params)
 * @param {string} path - Relative path (e.g., './dashboard.html')
 */
function redirectTo(path) {
    window.location.href = path;
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
