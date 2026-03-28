/**
 * Authentication Handler
 * Manages login, logout, and session validation
 */

/**
 * Handle login form submission
 * @param {Event} e - Form submit event
 */
async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.querySelector('input[name="username"]').value;
    const password = document.querySelector('input[name="password"]').value;
    const role = document.querySelector('input[name="role"]').value || 'employee';
    
    // Disable submit button
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Logging in...';
    
    try {
        const result = await apiCall('/login', 'POST', {
            username: username,
            password: password,
            role: role
        });
        
        if (result.status === 'success' || result.authenticated) {
            // Store user info
            setCurrentUser({
                user_id: result.user_id,
                username: result.username,
                role: result.role,
                name: result.name
            });
            
            console.log('[AUTH] Login successful:', result);
            showNotification(`Welcome ${result.name}!`, 'success', 2000);
            
            // Redirect based on role
            setTimeout(() => {
                if (result.role === 'admin') {
                    window.location.href = './admin/dashboard.html';
                } else {
                    window.location.href = './dashboard.html';
                }
            }, 500);
        } else {
            console.error('[AUTH] Login failed:', result);
            showNotification(result.message || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('[AUTH] Error:', error);
        showNotification('Login error: ' + error.message, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

/**
 * Handle logout
 */
async function handleLogout() {
    try {
        const result = await apiCall('/logout', 'POST');
        console.log('[AUTH] Logout response:', result);
    } catch (error) {
        console.error('[AUTH] Logout error:', error);
    }
    
    // Clear local storage regardless of API response
    clearUserSession();
    
    // Redirect to login
    showNotification('Logged out successfully', 'success', 1500);
    setTimeout(() => {
        window.location.href = './index.html';
    }, 1000);
}

/**
 * Check if user is authenticated and redirect if needed
 * @param {Array<string>} allowedRoles - Roles allowed to access (e.g., ['employee', 'admin'])
 */
function requireAuth(allowedRoles = ['employee', 'admin']) {
    const user = getCurrentUser();
    
    if (!user.user_id) {
        console.warn('[AUTH] Not authenticated - redirecting to login');
        window.location.href = './index.html';
        return false;
    }
    
    if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
        console.warn(`[AUTH] Insufficient permissions. Required: ${allowedRoles.join(', ')}, Got: ${user.role}`);
        window.location.href = './index.html';
        return false;
    }
    
    return true;
}

/**
 * Check if user is NOT authenticated and redirect if needed
 */
function requireNoAuth() {
    const user = getCurrentUser();
    
    if (user.user_id) {
        console.log('[AUTH] Already authenticated - redirecting to dashboard');
        if (user.role === 'admin') {
            window.location.href = './admin/dashboard.html';
        } else {
            window.location.href = './dashboard.html';
        }
        return false;
    }
    
    return true;
}

/**
 * Initialize authentication on page load
 * This should be called on every page that requires authentication
 */
function initAuth() {
    // Setup logout buttons
    document.querySelectorAll('[data-action="logout"]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            if (confirm('Are you sure you want to logout?')) {
                handleLogout();
            }
        });
    });
    
    // Setup login forms
    document.querySelectorAll('form[id*="loginForm"], form[id*="Login"]').forEach(form => {
        form.addEventListener('submit', handleLogin);
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initAuth);
