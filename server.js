// server.js

const express = require('express');
const mysql = require('mysql2');
const path = require('path');

const app = express();
const port = 3000;

// --- IMPORTANT: DATABASE CONNECTION ---
// Replace the placeholder values with your actual MySQL credentials.
const dbConfig = {
    host: 'localhost',
    user: 'root',
    password: 'root', // <-- PUT YOUR MYSQL PASSWORD HERE
    database: 'cgs_attendance'           // <-- The database name you created
};

const db = mysql.createConnection(dbConfig);

db.connect((err) => {
    if (err) {
        console.error('Error connecting to MySQL database:', err);
        // If connection fails, provide helpful feedback
        if (err.code === 'ER_ACCESS_DENIED_ERROR') {
            console.error('Access denied. Please check your username and password in dbConfig.');
        }
        if (err.code === 'ENOTFOUND' || err.code === 'ECONNREFUSED') {
            console.error('Connection refused. Is the MySQL server running on localhost?');
        }
        if (err.code === 'ER_BAD_DB_ERROR') {
            console.error(`Database '${dbConfig.database}' not found. Did you run the CREATE DATABASE command?`);
        }
        return;
    }
    console.log('Successfully connected to the MySQL database.');
});


// --- MIDDLEWARE ---
// This allows the server to understand JSON data from the frontend.
app.use(express.json());
// This serves all the files from your 'public' folder (index.html, css, etc.)
app.use(express.static(path.join(__dirname, 'public')));


// --- API ENDPOINTS ---
app.post('/login', (req, res) => {
    const { username, password, userType } = req.body;

    if (!username || !password || !userType) {
        return res.status(400).json({ success: false, message: 'Missing credentials.' });
    }

    const sql = `SELECT * FROM users WHERE username = ? AND password = ? AND role = ?`;

    db.query(sql, [username, password, userType], (err, results) => {
        if (err) {
            console.error('Database query error:', err);
            return res.status(500).json({ success: false, message: 'Server error.' });
        }

        if (results.length > 0) {
            // User found, login successful
            const user = results[0];
            const dashboardUrl = user.role === 'admin' ? 'admin-dashboard.html' : 'employee-dashboard.html';
            res.json({
                success: true,
                message: 'Login successful!',
                user: { name: user.name, id: user.id },
                dashboardUrl: dashboardUrl
            });
        } else {
            // User not found or credentials incorrect
            res.status(401).json({ success: false, message: 'Invalid username or password.' });
        }
    });
});


// --- START SERVER ---
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
    console.log('Your website is now live. Open your browser and go to the address above.');
});