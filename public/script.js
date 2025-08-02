// public/script.js (MODIFIED)

document.addEventListener('DOMContentLoaded', () => {
    // --- ELEMENT SELECTORS ---
    const employeeLoginBtn = document.getElementById('employeeLoginBtn');
    const adminLoginBtn = document.getElementById('adminLoginBtn');

    // Add IDs to the forms and buttons in index.html if you haven't already
    // Example: <button id="employeeLoginBtn">Login</button>

    // --- EVENT LISTENERS ---
    employeeLoginBtn.addEventListener('click', () => handleLogin('employee'));
    adminLoginBtn.addEventListener('click', () => handleLogin('admin'));

    // --- CORE FUNCTIONS ---

    /**
     * Handles the login logic by sending data to the backend server.
     * @param {string} userType - Either 'employee' or 'admin'.
     */
    async function handleLogin(userType) {
        let username, password, errorElement;

        // 1. Get data from the correct form
        if (userType === 'employee') {
            username = document.getElementById('employeeUsername').value;
            password = document.getElementById('employeePassword').value;
            errorElement = document.getElementById('employeeError');
        } else {
            username = document.getElementById('adminUsername').value;
            password = document.getElementById('adminPassword').value;
            errorElement = document.getElementById('adminError');
        }
        
        // Clear any previous error messages
        errorElement.textContent = '';

        try {
            // 2. Send login credentials to the backend server
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password, userType }),
            });

            const data = await response.json();

            // 3. Handle the server's response
            if (response.ok && data.success) { // Check for successful HTTP status and success flag
                // Login successful
                alert(`Login successful! Welcome, ${data.user.name}.`);
                
                // Store user info to be used on the dashboard page
                localStorage.setItem('loggedInUser', JSON.stringify(data.user));
                
                // Redirect to the appropriate dashboard
                window.location.href = data.dashboardUrl;
            } else {
                // Login failed - display error from server
                errorElement.textContent = data.message || 'An error occurred.';
            }
        } catch (error) {
            console.error('Login request failed:', error);
            errorElement.textContent = 'Could not connect to the server.';
        }
    }
});


// --- UI HELPER FUNCTIONS (from your original code - NO CHANGES NEEDED) ---

function toggleForms() {
  const employeeForm = document.getElementById('employeeForm');
  const adminForm = document.getElementById('adminForm');
  const toggleBtn = document.getElementById('toggleBtn');
  const isEmployeeVisible = !employeeForm.classList.contains('hidden');

  if (isEmployeeVisible) {
    employeeForm.classList.add('hidden');
    adminForm.classList.remove('hidden');
    toggleBtn.innerText = "Employee";
  } else {
    adminForm.classList.add('hidden');
    employeeForm.classList.remove('hidden');
    toggleBtn.innerText = "Admin";
  }
}

function togglePassword(inputId, iconElement){
    const input = document.getElementById(inputId);
    if (input.type === "password"){
        input.type = "text";
        iconElement.textContent = "🙈";
    }
    else{
        input.type = "password";
        iconElement.textContent = "👁️";
    }
}