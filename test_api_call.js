
// Test frontend API call to backend
fetch('http://localhost:5000/login', {
    method: 'POST',
    credentials: 'include',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        username: 'pradeep',
        password: 'test123',
        role: 'employee'
    })
})
.then(r => r.json())
.then(data => {
    console.log('LOGIN RESPONSE:', JSON.stringify(data, null, 2));
    console.log('TEST PASSED: Frontend can call backend API');
})
.catch(e => console.error('TEST FAILED:', e.message));
