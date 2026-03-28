/**
 * Session Initialization Script
 * Runs on all pages to check authentication and manage session state
 */

// Determine API URL based on environment
const API_URL = (() => {
    const hostname = window.location.hostname;
    if (hostname.includes('netlify.app')) {
        return 'https://cgs-attendance-system.onrender.com';
    }
    if (hostname.includes('localhost') || hostname.includes('127.0.0.1')) {
        return 'http://localhost:5000';
    }
    return 'https://cgs-attendance-system.onrender.com';
})();

// Store API URL for use in other scripts
window.API_URL = API_URL;
localStorage.setItem('API_URL', API_URL);

// Current User object
let currentUser = null;

/**
 * Check if user is authenticated
 * Tries to get session data from server
 */
async function checkAuthentication() {
    try {
        const response = await fetch(`${API_URL}/api/check_session`, {
            method: 'GET',
            credentials: 'include', // Important: send cookies
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            if (data.authenticated) {
                currentUser = {
                    user_id: data.user_id,
                    username: data.username,
                    name: data.name,
                    role: data.role
                };
                return true;
            }
        }
        
        // Session expired or invalid
        currentUser = null;
        return false;
    } catch (error) {
        console.error('Session check error:', error);
        currentUser = null;
        return false;
    }
}

/**
 * Logout user - clear session on both server and client
 */
async function logout() {
    try {
        // Call server logout endpoint
        await fetch(`${API_URL}/logout`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        }).catch(e => console.log('Logout request sent'));

        // Clear client-side data
        currentUser = null;
        localStorage.removeItem('currentUser');
        localStorage.removeItem('API_URL');
        sessionStorage.clear();

        // Redirect to login
        window.location.href = './index.html';
    } catch (error) {
        console.error('Logout error:', error);
        // Force redirect anyway
        window.location.href = './index.html';
    }
}

/**
 * Handle logout button clicks
 */
function handleLogout(e) {
    if (e) e.preventDefault();
    logout();
}

/**
 * Redirect to login if not authenticated
 */
async function requireAuth() {
    const isAuth = await checkAuthentication();
    if (!isAuth) {
        window.location.href = './index.html';
        return false;
    }
    return true;
}

/**
 * Initialize page - check auth and populate user data
 */
async function initializePage() {
    // Check authentication
    const isAuth = await checkAuthentication();
    
    if (!isAuth) {
        // Redirect to login if not on login page
        if (!window.location.href.includes('index.html') && 
            !window.location.href.includes('login.html')) {
            console.log('Not authenticated, redirecting to login');
            window.location.href = './index.html';
        }
        return false;
    }
    
    // Update user display elements
    const userDisplays = document.querySelectorAll('[data-user-display]');
    userDisplays.forEach(el => {
        el.textContent = `${currentUser.name || currentUser.username}`;
    });
    
    const roleDisplays = document.querySelectorAll('[data-role-display]');
    roleDisplays.forEach(el => {
        el.textContent = currentUser.role || 'Employee';
    });
    
    // Set up logout buttons
    const logoutButtons = document.querySelectorAll('[data-logout-btn]');
    logoutButtons.forEach(btn => {
        btn.addEventListener('click', handleLogout);
    });
    
    return true;
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializePage);

// Make functions global
window.currentUser = currentUser;
window.checkAuthentication = checkAuthentication;
window.logout = logout;
window.handleLogout = handleLogout;
window.requireAuth = requireAuth;
window.initializePage = initializePage;
