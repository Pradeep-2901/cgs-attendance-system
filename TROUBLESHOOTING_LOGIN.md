# TROUBLESHOOTING: LOGIN FAILED ON RENDER

## What We Know

✅ **Locally (Flask on localhost:5000):**
- pradeep / test123 → SUCCESS (authenticated, emp001, employee role)
- Database connections working
- All Flask endpoints working

❌ **On Render:**
- Login showing "Login failed. Please try again."
- But Render deployment shows "live"

## Possible Causes

### 1. Password Issue (Most Likely)
- `pradeep` user may have been imported with different password hash
- Password hashing mismatch between local MySQL and Railway

### 2. User Not Found
- User record didn't import correctly from local to Railway
- SQL import missed the users table

### 3. Flask Environment Variable Issue  
- `MYSQL_HOST` might not be resolving correctly on Render
- `FLASK_SECRET_KEY` mismatch (Flask can't verify session)

## IMMEDIATE FIXES TO TRY

### Fix 1: Reset User Password to Known Value

Since `pradeep/test123` works locally but not on Render, let's reset it:

```bash
# On your local machine (with local MySQL):
python reset_password.py
```

This will set pradeep password to test123 hash.

Then verify the hash matches in BOTH databases.

### Fix 2: Check Render Logs for Exact Error

In Render dashboard:
1. Go to **Logs** tab
2. Filter for error messages around login time
3. Look for:
   - `Access denied for user`
   - `Unknown database`
   - `Connection refused`
   - `Authentication failed`

### Fix 3: Verify Render Environment Variables

In Render dashboard → Environment:
- Confirm `MYSQL_HOST=mysql.railway.internal` (NOT localhost)
- Confirm `MYSQL_DB=railway` (NOT cgs)
- Confirm password has no extra spaces

---

## STEP-BY-STEP RESOLUTION

### Step 1: Check Render Logs (Do This First)
Go to: https://dashboard.render.com/ → cgs-backend → Logs

Copy any ERROR messages that appear during login attempts.

### Step 2: Run Password Reset Locally
```bash
python reset_password.py
```

This ensures pradeep has known password hash.

### Step 3: Verify Password Hash in Railway

We'll query Railway to show password hashes and compare.

### Step 4: If Hashes Don't Match

We'll need to:
- Export user table from local MySQL
- Drop users table in Railway
- Re-import with correct hashes

---

## USERS WHO SHOULD EXIST IN RAILWAY

Based on backup from local MySQL:

| Username | Role | Expected ID |
|----------|------|-------------|
| pradeep | employee | emp001 |
| sounthar | employee | emp002 |
| aadhi | employee | emp003 |
| francis | admin | adm001 |

---

**NEXT ACTION:**

1. Check Render logs for error message
2. Run `python reset_password.py` locally
3. Tell me the error from Render logs
4. I'll fix the password hashes in Railway
