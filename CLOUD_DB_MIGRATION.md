# Cloud MySQL Migration Guide - CGS Attendance System
## From Local MySQL → Railway (for Render backend)

**Current State:** Local MySQL on localhost:3306  
**Target State:** Railway cloud MySQL  
**Deployment:** Render backend + Netlify frontend  
**Demo Users:** 10-20 employees  
**Migration Time:** ~20 minutes  

---

## WHAT HAPPENS IN THIS MIGRATION

```
┌─────────────────┐
│ Local MySQL     │
│ localhost:3306  │
│ • users table   │
│ • attendance    │
│ • leaves        │
└────────┬────────┘
         │ EXPORT (SQL dump)
         ▼
┌─────────────────┐
│  SQL File (.sql)│
│ • Schema + data │
│ • Ready to copy │
└────────┬────────┘
         │ IMPORT (via Railway/MySQL client)
         ▼
┌─────────────────────────────────────┐
│ Railway Cloud MySQL                 │
│ • hosted-db-xxx.railway.app:3306    │
│ • Same schema as local              │
│ • All data preserved                │
│ • SSL/TLS connection ready          │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Flask app.py (on Render)            │
│ Updated connection:                 │
│ • MYSQL_HOST = railway DNS          │
│ • MYSQL_USER = railway user         │
│ • MYSQL_PASSWORD = railway pwd      │
│ • Same logic, new host              │
└─────────────────────────────────────┘
```

---

# STEP-BY-STEP MIGRATION CHECKLIST

## PREREQUISITE: Current Local Database Status

### Check 1: Verify Local MySQL is Running
```powershell
# Command
mysql -u root -p -e "SELECT VERSION();"

# Enter password: root (from your setup)

# Expected Output
+--------------------+
| VERSION()          |
+--------------------+
| 8.0.x or similar   |
+--------------------+
```

### Check 2: Verify CGS Database Exists
```powershell
# Command
mysql -u root -p -e "USE cgs; SHOW TABLES;"

# Expected Output
+-----------------------+
| Tables_in_cgs         |
+-----------------------+
| attendance_records    |
| employee_remote       |
| employees             |
| leave_requests        |
| users                 |
| (other tables)        |
+-----------------------+

# Count should match your schema structure
```

### Check 3: Count Users and Records
```powershell
# Command
mysql -u root -p cgs -e "SELECT COUNT(*) as user_count FROM users; SELECT COUNT(*) as attendance_count FROM attendance_records; SELECT COUNT(*) as leave_count FROM leave_requests;"

# Expected Output
+------------+
| user_count |
+------------+
| 4          | (or your count)
+------------+
+-----------------+
| attendance_count|
+-----------------+
| 25              | (or your count)
+-----------------+
+-----------+
| leave_count|
+-----------+
| 3         | (or your count)
+-----------+
```

---

## PHASE 1: EXPORT LOCAL DATABASE (5 minutes)

### Step 1.1: Create Export Directory
```powershell
# Command
mkdir backup_export

# Verify
Test-Path backup_export

# Expected
True
```

### Step 1.2: Export Full Database with Data and Schema
```powershell
# OPTION A: Export with credentials in command (single-line)
mysqldump -u root -proot cgs > backup_export/cgs_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql

# OPTION B: Export and prompt for password
mysqldump -u root -p cgs > backup_export/cgs_backup.sql

# Enter password when prompted: root
```

**Expected Output:**
- File created: `backup_export/cgs_backup_YYYYMMDD_HHMMSS.sql`
- File size: 50KB - 500KB (depending on data)
- Contains: `CREATE TABLE`, `INSERT INTO`, `USE cgs`, etc.

**Common Error:**
```
mysqldump: [Warning] Using a password on the command line interface can be insecure.
```
**Quick Fix:** This is just a warning (not an error). The export still works. For production, use .my.cnf file (out of scope for this demo).

### Step 1.3: Verify Export File
```powershell
# Command
Get-ChildItem backup_export/ | Format-Table Name, Length

# Expected
Name                                Length
----                                ------
cgs_backup_20260328_123456.sql      123456

# Verify it has CREATE TABLE statements
Select-String "CREATE TABLE" backup_export/cgs_backup*.sql

# Expected
cgs_backup_20260328_123456.sql:28:CREATE TABLE `users` (
cgs_backup_20260328_123456.sql:45:CREATE TABLE `employees` (
cgs_backup_20260328_123456.sql:62:CREATE TABLE `attendance_records` (
(... more tables ...)
```

### Step 1.4: Verify Data Rows are Included
```powershell
# Command
Select-String "INSERT INTO" backup_export/cgs_backup*.sql | Measure-Object

# Expected
Count: 30-100+ (depending on your data)

# Sample check - look for INSERT statements
Select-String "INSERT INTO `users`" backup_export/cgs_backup*.sql | Select-Object -First 3

# Expected shows actual user inserts
```

✅ **PHASE 1 COMPLETE:** You now have a local backup file ready to import into Railway.

---

## PHASE 2: CREATE RAILWAY CLOUD MYSQL DB (10 minutes)

### Step 2.1: Create Railway Account & Project
1. Go to **https://railway.app/**
2. Click "**Start a New Project**"
3. Select "**MySQL**"
4. Choose plan: **Free tier** (for demo)
5. Railway creates database and assigns credentials automatically

**Expected:**
- Railway generates 6 credentials:
  - `RAILWAY_MYSQL_HOST` → `xxx-production.up.railway.app`
  - `RAILWAY_MYSQL_PORT` → `3306`
  - `RAILWAY_MYSQL_DB` → `railway` (or your choice)
  - `RAILWAY_MYSQL_USER` → `root` (or auto-generated)
  - `RAILWAY_MYSQL_PASSWORD` → (complex auto-generated)
  - `DATABASE_URL` → `mysql://user:password@host:port/db`

### Step 2.2: Copy Railway Credentials
In Railway dashboard:
- Go to **Variables** section
- Copy these values:
  ```
  MYSQL_HOST = xxx-production.up.railway.app
  MYSQL_PORT = 3306
  MYSQL_USER = root
  MYSQL_PASSWORD = xxxxxxxxxxxxxxxx
  MYSQL_DB = railway
  ```

**⚠️ IMPORTANT:** Save these somewhere safe (you'll need them for Render and Flask .env)

### Step 2.3: Verify Railway Connection (Optional - but recommended)
From your local machine, test if you can reach Railway:
```powershell
# Command (using MySQL client)
mysql -h xxx-production.up.railway.app -u root -p -P 3306 -e "SELECT 'Railway connection successful';"

# When prompted, enter the Railway password
# Expected
+--------------------------------------+
| Railway connection successful        |
+--------------------------------------+
```

**Common Error:**
```
ERROR 2003 (HY000): Can't connect to MySQL server on 'xxx-production.up.railway.app:3306'
```
**Quick Fix:** 
- Verify Railway MySQL is running (check dashboard)
- Wait 1-2 minutes after creation (sometimes needs startup time)
- Check network firewall isn't blocking port 3306

---

## PHASE 3: IMPORT INTO RAILWAY (5 minutes)

### Step 3.1: Import Your Database Schema & Data
```powershell
# Command
mysql -h xxx-production.up.railway.app -u root -p -P 3306 < backup_export/cgs_backup_YYYYMMDD_HHMMSS.sql

# When prompted, enter Railway password
```

**Expected Output:**
```
(no output = success)
(or you might see warnings about triggers/procedures, which is OK for database import)
```

**Common Errors & Fixes:**

| Error | Cause | Fix |
|-------|-------|-----|
| `ERROR 1045 (28000): Access denied` | Wrong password | Re-check Railway dashboard credentials |
| `ERROR 2003: Can't connect` | Host unreachable | Verify Railway is running + host DNS is correct |
| `ERROR 1227: Access denied; you need ...` | Permission issue | Some imports have permission errors. Use `--force` flag |

**If you get permission errors, retry with:**
```powershell
mysql -h xxx-production.up.railway.app -u root -p -P 3306 --force < backup_export/cgs_backup_YYYYMMDD_HHMMSS.sql
```

### Step 3.2: Verify Data Imported Successfully
```powershell
# Command 1: List all databases
mysql -h xxx-production.up.railway.app -u root -p -P 3306 -e "SHOW DATABASES;"

# You should see 'railway' (or your chosen DB name)

# Command 2: List tables in your database
mysql -h xxx-production.up.railway.app -u root -p -P 3306 railway -e "SHOW TABLES;"

# Expected
+-----------+
| Tables_in_railway |
+-----------+
| attendance_records |
| employees |
| leave_requests |
| users |
| (more tables) |
+-----------+

# Command 3: Count rows to verify data came through
mysql -h xxx-production.up.railway.app -u root -p -P 3306 railway -e "SELECT 'users' as table_name, COUNT(*) as row_count FROM users UNION SELECT 'attendance_records', COUNT(*) FROM attendance_records UNION SELECT 'leave_requests', COUNT(*) FROM leave_requests;"

# Expected (numbers should match your local DB)
+--------------------+-----------+
| table_name         | row_count |
+--------------------+-----------+
| users              | 4         |
| attendance_records | 25        |
| leave_requests     | 3         |
+--------------------+-----------+
```

### Step 3.3: Check One User Record Still Exists
```powershell
# Command
mysql -h xxx-production.up.railway.app -u root -p -P 3306 railway -e "SELECT id, username, email, role FROM users LIMIT 1;"

# Enter Railway password

# Expected
+----+----------+-------------------+----------+
| id | username | email             | role     |
+----+----------+-------------------+----------+
| 1  | pradeep  | pradeep@email.com | employee |
+----+----------+-------------------+----------+
```

✅ **PHASE 3 COMPLETE:** Your data is now in Railway cloud!

---

## PHASE 4: UPDATE FLASK LOCAL .env (5 minutes)

### Step 4.1: Backup Current .env
```powershell
# Command
Copy-Item .env .env.backup

# Verify
Test-Path .env.backup
```

### Step 4.2: Update .env with Railway Credentials
Edit `.env` file in VS Code or terminal:

**Before:**
```
FLASK_ENV=development
FLASK_SECRET_KEY=your-secret-key
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DB=cgs
DATABASE_URL=mysql://root:root@localhost:3306/cgs
```

**After (with Railway credentials):**
```
FLASK_ENV=development
FLASK_SECRET_KEY=your-secret-key
MYSQL_HOST=xxx-production.up.railway.app
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=xxxxxxxxxxxxxxxx
MYSQL_DB=railway
DATABASE_URL=mysql://root:xxxxxxxxxxxxxxxx@xxx-production.up.railway.app:3306/railway
```

---

## PHASE 5: VERIFY FLASK CAN CONNECT TO RAILWAY (5 minutes)

### Step 5.1: Stop Local MySQL (optional but recommended)
```powershell
# Command (Windows)
# For MySQL running as Windows service:
Get-Service | findstr mysql

# If it shows "running", you can stop it for this test (optional)
# Stop-Service MySQL80

# Or just kill the process if no service
Get-Process | findstr mysql
```

### Step 5.2: Test Flask Connection to Railway
```powershell
# Kill any running Flask instance first
# Then start Flask
python app.py
```

**Expected Output:**
```
🚀 Starting CGS Attendance Management System...
📊 Admin Panel: Login with admin credentials
👥 Employee Portal: Login with employee credentials
🌐 Access: http://localhost:5000
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
 ✓ [STARTUP] Database connection successful!
 ✓ [STARTUP] Using database: railway (on xxx-production.up.railway.app)
```

### Step 5.3: Test Health Endpoint
```powershell
# In another terminal
Invoke-WebRequest http://localhost:5000/health -UseBasicParsing | Select-Object StatusCode, Content

# Expected
StatusCode Content
----------- -------
200         {"status":"healthy","database_connected":true,"host":"xxx-production.up.railway.app"}
```

### Step 5.4: Test Login Endpoint
```powershell
# Command
$loginData = @{
    username = "pradeep"
    password = "test123"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $loginData | Select-Object StatusCode, @{n='Content';e={$_.Content | ConvertFrom-Json}}

# Expected
StatusCode Content
----------- -------
200         @{status=success; authenticated=True; user_id=emp001; ...}
```

### Step 5.5: Test Dashboard Endpoint (with session)
```powershell
# Command - This captures the session cookie from login
$loginData = @{
    username = "pradeep"
    password = "test123"
} | ConvertTo-Json

$loginResponse = Invoke-WebRequest -Uri "http://localhost:5000/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $loginData `
    -SessionVariable session

# Now use that session for dashboard
$dashboardResponse = Invoke-WebRequest -Uri "http://localhost:5000/dashboard?format=json" `
    -WebSession $session

$dashboardResponse | Select-Object StatusCode, @{n='Content';e={$_.Content | ConvertFrom-Json | Select-Object status, date}}

# Expected
StatusCode Content
----------- -------
200         @{status=success; date=2026-03-28; ...}
```

**Common Error:**
```
ERROR]: Database connection failed: Access denied for user 'root'@'xxx.railway.app' (using password: YES)
```
**Quick Fix:**
- Verify .env file has correct Railway password
- Make sure there are no extra spaces in .env values
- Check Railway dashboard → Variables for exact values
- Password might have special characters - verify it's not truncated

✅ **PHASE 5 COMPLETE:** Flask is successfully connecting to Railway!

---

## PHASE 6: UPDATE RENDER ENVIRONMENT VARIABLES

### Step 6.1: Update Render Dashboard
1. Go to **https://dashboard.render.com/**
2. Select your **cgs-backend** service
3. Go to **Environment** section
4. Update these variables:

| Variable | Old Value | New Value |
|----------|-----------|-----------|
| `MYSQL_HOST` | `localhost` | `xxx-production.up.railway.app` |
| `MYSQL_PORT` | `3306` | `3306` |
| `MYSQL_USER` | `root` | `root` |
| `MYSQL_PASSWORD` | `root` | `xxxxxxxxxxxxxxxx` (Railway password) |
| `MYSQL_DB` | `cgs` | `railway` |
| `DATABASE_URL` | `mysql://root:root@localhost:3306/cgs` | `mysql://root:xxxxx@xxx-production.up.railway.app:3306/railway` |

### Step 6.2: Manual Redeploy on Render
In Render dashboard:
1. Scroll to **Recent Deploys**
2. Click **Manual Deploy** button
3. Select **Deploy latest commit**
4. Wait 3-5 minutes for deployment

**Check logs:**
- Go to **Logs** tab
- Should see: `Database connection successful!`
- Should NOT see: `ERROR: Connection to localhost failed`

---

## PHASE 7: FINAL VALIDATION - TEST ENTIRE FLOW

### Validation 1: Check Render Backend Health
```pow
# In PowerShell (after Render redeploys)
$renderUrl = "https://cgs-backend-xxxxx.onrender.com"

# Test health check
Invoke-WebRequest "$renderUrl/health" -UseBasicParsing | Select-Object StatusCode, @{n='Body';e={$_.Content}}

# Expected
StatusCode Body
----------- ----
200         {"status":"healthy","database_connected":true,"host":"xxx-production.up.railway.app"}
```

### Validation 2: Test Render Login
```powershell
# Command
$renderUrl = "https://cgs-backend-xxxxx.onrender.com"

$loginData = @{
    username = "pradeep"
    password = "test123"
} | ConvertTo-Json

Invoke-WebRequest -Uri "$renderUrl/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $loginData -UseBasicParsing | Select-Object StatusCode, @{n='Body';e={$_.Content | ConvertFrom-Json}}

# Expected
StatusCode Body
----------- ----
200         @{status=success;user_id=emp001;authenticated=True;...}
```

### Validation 3: Frontend (Netlify) Can Now Connect
1. Visit: **https://cgs-attendance-xxxxx.netlify.app**
2. Open browser Console (F12)
3. Look for: `[CONFIG] API URL: https://cgs-backend-xxxxx.onrender.com`
4. Try login:
   - Username: `pradeep`
   - Password: `test123`
5. Expected: Dashboard loads, user authenticated ✅

### Validation 4: Database Query to Confirm Migration
Run this from anywhere to verify all data migrated:

```sql
-- Query 1: Total users
SELECT COUNT(*) as total_users FROM users;

-- Query 2: Users by role
SELECT role, COUNT(*) as count FROM users GROUP BY role;

-- Query 3: Attendance records
SELECT COUNT(*) as total_attendance FROM attendance_records;

-- Query 4: Leave requests
SELECT COUNT(*) as total_leaves FROM leave_requests;

-- Query 5: Sample user login attempt query (what Flask runs)
SELECT id, username, password_hash, role, email FROM users WHERE username = 'pradeep';
```

Run via:
```powershell
mysql -h xxx-production.up.railway.app -u root -p -P 3306 railway -e "SELECT COUNT(*) as total_users FROM users;"
```

---

## TROUBLESHOOTING MATRIX

| Symptom | Root Cause | Diagnosis Command | Quick Fix |
|---------|-----------|-------------------|-----------|
| Login fails on Netlify | CORS issue or wrong API URL | Check browser console for CORS error | Verify `API_URL` in Netlify environment |
| Render shows 502 error | Database connection failed | Check Render logs: `tail -f logs` | Verify `.env` vars on Render match Railway |
| `Access denied for user 'root'` | Wrong password in `.env` | Compare `.env` value with Railway dashboard | Copy exact password from Railway Variables |
| `Can't connect to host` | Railway host unreachable | `nslookup xxx-production.up.railway.app` | Wait 2 min, check Railway status page |
| Authentication works locally but fails on Render | Python version different | Check `python --version` locally vs Render logs | Ensure `requirements.txt` has same versions |
| Data not showing in cloud DB | Import failed | Query Railway: `SELECT COUNT(*) FROM users;` | Re-run import with `--force` flag |

---

# ROLLBACK PLAN (If Something Goes Wrong)

```powershell
# Step 1: Revert to Local MySQL
# Edit .env back to localhost
MYSQL_HOST=localhost
MYSQL_USER=root  
MYSQL_PASSWORD=root
MYSQL_DB=cgs

# Step 2: Restart Flask
# Kill running Flask instance and start again
python app.py

# Step 3: Restart local MySQL (if needed)
# For Windows service:
Start-Service MySQL80

# Step 4: Revert Render .env (in dashboard)
# Change MYSQL_HOST back to localhost (NOT recommended, but temporary)
# OR contact Render support
```

---

## WHAT YOU NOW HAVE

```
✅ Local MySQL backup: backup_export/cgs_backup_xxxxx.sql
✅ Railway cloud MySQL: Set up and populated
✅ Flask .env updated: Points to Railway
✅ Render environment: Updated with Railway credentials
✅ End-to-end verified: Login works via Netlify → Render → Railway
✅ Data preserved: All users, attendance, leaves intact
✅ Session management: Still works via HTTP cookies
✅ CORS: Still configured for Netlify domain
```

---

## DEPLOYMENT SUMMARY

| Component | Old | New | Status |
|-----------|-----|-----|--------|
| Flask Backend | localhost:5000 | Render (xxx.onrender.com) | ✅ |
| MySQL Database | localhost:3306 | Railway (xxx-production.up.railway.app) | ✅ |
| Frontend | localhost:8000 | Netlify (xxx.netlify.app) | ✅ |
| Session Management | In-memory (Flask) | HTTP cookies (secure) | ✅ |
| CORS | localhost only | Netlify domain | ✅ |
| Environment Config | .env (local) | Render dashboard (prod) | ✅ |

---

## FINAL CHECKLIST - RUN IN THIS ORDER

- [ ] **1. Export local MySQL:** `mysqldump -u root -proot cgs > backup_export/cgs_backup.sql`
- [ ] **2. Create Railway MySQL:** Account → Project → MySQL → Free Tier
- [ ] **3. Copy Railway credentials:** Save MYSQL_HOST, USER, PASSWORD, DB, PORT
- [ ] **4. Import to Railway:** `mysql -h railway-host ... < backup_export/cgs_backup.sql`
- [ ] **5. Verify Railway data:** `SELECT COUNT(*) FROM users;` returns 4+
- [ ] **6. Update .env locally:** MYSQL_HOST, PASSWORD, DB = Railway values
- [ ] **7. Test Flask locally:** `python app.py` → Test `/health` endpoint
- [ ] **8. Test login locally:** `Invoke-WebRequest /login` → Should return 200 OK
- [ ] **9. Push to GitHub:** `git add . && git commit && git push`
- [ ] **10. Update Render env:** MYSQL_HOST, PASSWORD, DB = Railway values
- [ ] **11. Redeploy on Render:** Manual Deploy → Trigger → Monitor logs
- [ ] **12. Verify Render health:** `https://xxx-xxx-xxx.onrender.com/health` → 200 OK
- [ ] **13. Test Netlify login:** Visit Netlify site → Try logging in
- [ ] **14. Confirm attendance works:** Check-in → View records from cloud DB

---

**YOU'RE READY! Let me know when you want to execute each step, and I'll run all commands for you.**
