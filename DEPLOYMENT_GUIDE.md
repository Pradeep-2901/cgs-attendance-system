# Deployment Guide: CGS Attendance System

## Overview
This guide covers deploying the CGS Attendance System with:
- **Backend**: Flask API on Render
- **Frontend**: Static site on Netlify
- **Database**: External MySQL server

---

## Prerequisites

### Tools Needed:
1. GitHub account (for version control)
2. Render account (render.com) - free tier available
3. Netlify account (netlify.app) - free tier available
4. External MySQL database (or connection string from existing server)
5. Git installed locally

### Project Structure:
```
CGS/
├── app.py                 (Flask backend)
├── requirements.txt       (Python dependencies)
├── .env.example          (Config template)
├── render.yaml           (Render deployment config)
└── frontend/             (Netlify site)
    ├── index.html
    ├── dashboard.html
    ├── netlify.toml
    ├── _redirects
    └── js/
        ├── api.js
        ├── auth.js
        └── config.js
```

---

## Phase 1: Prepare GitHub Repository

### 1.1 Initialize Git
```bash
cd d:\PROJECTS\CGS
git init
git add .
git commit -m "Initial commit: Flask backend + standalone frontend"
git branch -M main
```

### 1.2 Push to GitHub
```bash
git remote add origin https://github.com/YOUR-USERNAME/cgs-attendance.git
git push -u origin main
```

### 1.3 Create `.env` (NEVER commit this!)
```bash
# Create from template
copy .env.example .env

# Edit .env with your database credentials
# Then add .env to .gitignore
echo ".env" >> .gitignore
echo "node_modules/" >> .gitignore
echo "__pycache__/" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"
git push
```

---

## Phase 2: Deploy Backend on Render

### 2.1 Create Render Web Service

1. Go to **https://dashboard.render.com**
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Enter service details:
   - **Name**: `cgs-backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
   - **Region**: Choose closest to your data center

### 2.2 Set Environment Variables

In Render dashboard, go to your service → **Environment**:

```
FLASK_ENV = production
FLASK_SECRET_KEY = (generate: python -c "import secrets; print(secrets.token_hex(32))")
MYSQL_HOST = your-database-host.com
MYSQL_USER = your_db_user
MYSQL_PASSWORD = your_db_password
MYSQL_DB = cgs
GOOGLE_MAPS_API_KEY = (optional)
```

**To generate FLASK_SECRET_KEY safely:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2.3 Deploy

1. Click **"Create Web Service"**
2. Render will automatically deploy when you push to GitHub
3. Wait for deployment to complete (usually 2-3 minutes)
4. Note your backend URL: `https://cgs-backend.onrender.com` (or yourname.onrender.com)

### 2.4 Test Backend

Open terminal and test the API:
```bash
# Test health endpoint
curl https://cgs-backend.onrender.com/health

# Response should be:
# {"status":"ok"}
```

**If this fails:**
- Check Render logs: Dashboard → Your Service → Logs
- Verify database credentials are correct
- Ensure MySQL server is accessible from Render IP

---

## Phase 3: Deploy Frontend on Netlify

### 3.1 Create Netlify Site

**Option A: Via GitHub (Recommended)**

1. Go to **https://app.netlify.com**
2. Click **"Add new site"** → **"Import an existing project"**
3. Choose **GitHub** → Authorize
4. Select your `cgs-attendance` repository
5. Configure build settings:
   - **Base directory**: `frontend`
   - **Build command**: (leave empty)
   - **Publish directory**: `frontend`

**Option B: Drag & Drop**

1. Go to https://app.netlify.com/drop
2. Drag the `frontend` folder to Netlify
3. (This creates a temporary deployment, ideal for testing)

### 3.2 Set Environment Variables (Netlify)

In Netlify dashboard:
1. Go to your site → **Site settings** → **Build & deploy** → **Environment**
2. Add:
   ```
   API_URL = https://cgs-backend.onrender.com
   ```

### 3.3 Verify Frontend URLs

Your frontend will be deployed at: `https://your-site.netlify.app`

Test login page loads: `https://your-site.netlify.app/index.html`

The `_redirects` file ensures all routes work properly.

---

## Phase 4: Update CORS Settings

Now that you know your Netlify URL, update Flask CORS in `app.py`:

```python
CORS(app, 
     origins=[
         "http://localhost:3000",  # Local testing
         "https://your-site.netlify.app"  # Your Netlify URL
     ],
     supports_credentials=True)
```

Then push to GitHub:
```bash
git add app.py
git commit -m "Update CORS for production Netlify domain"
git push
```

Render will auto-redeploy within minutes.

---

## Phase 5: Testing & Verification

### 5.1 Test Login Flow

1. Open frontend: `https://your-site.netlify.app/index.html`
2. Open DevTools (F12) → **Console** tab
3. Try logging in with employee credentials

**Expected Console Logs:**
```
[CONFIG] API URL: https://cgs-backend.onrender.com
[AUTH] Login successful: {status: 'success', ...}
```

### 5.2 Test Check-in

1. After login, go to **Mark Attendance**
2. Allow location permissions
3. Click **Check In** button
4. Verify success message appears

**If it fails:**
- Check Console for API errors
- Verify backend is accessible: `curl https://cgs-backend.onrender.com/health`
- Check Render logs for backend errors

### 5.3 Test Session Persistence

1. Refresh the page
2. User should remain logged in (session persisted via cookies)
3. Logout and verify redirect to login page

### 5.4 Load Testing (demo with 10-20 employees)

- Create test users in database
- Have multiple employees log in
- Verify concurrent users don't cause issues
- Monitor Render dashboard for CPU/memory usage

---

## Phase 6: Final Checklist

### Backend (Render)
- [ ] Service deployed and healthy
- [ ] Environment variables set correctly
- [ ] Database connection working (`/health` endpoint responds)
- [ ] Logs show no errors
- [ ] CORS headers configured for Netlify domain
- [ ] SSL certificate active (Render provides free HTTPS)

### Frontend (Netlify)
- [ ] Site deployed
- [ ] API_URL environment variable set
- [ ] `_redirects` file present
- [ ] All HTML files accessible
- [ ] CSS and JS files loading (check DevTools Network tab)
- [ ] Login form works

### End-to-End
- [ ] Login with employee account works
- [ ] Dashboard loads attendance data
- [ ] Check-in/Check-out submits successfully
- [ ] Photos upload works
- [ ] Leave request functionality works
- [ ] Session persists on refresh
- [ ] Logout works
- [ ] Mobile responsiveness verified

---

## Troubleshooting

### Issue: "Network Error" on Login

**Causes:**
1. Backend URL incorrect in frontend
2. CORS not configured for Netlify domain
3. Backend service is down

**Solution:**
```javascript
// In browser console, check API URL:
localStorage.getItem('API_URL')

// Should output: https://cgs-backend.onrender.com
```

If wrong, update `frontend/js/config.js` or set Netlify environment variable.

### Issue: "Session Expired" After Login

**Cause:** Cookies not being sent with requests

**Solution:** Verify `api.js` has:
```javascript
credentials: 'include'  // This line is CRITICAL
```

### Issue: Photos Not Uploading

**Cause:** File upload endpoint issue

**Check:**
1. Backend logs: `Render → Your Service → Logs`
2. Verify `UPLOAD_FOLDER` exists: `static/attendance_photos/`
3. Render has write permissions

### Issue: "Bad Gateway" or 502 Errors

**Cause:** Backend service crashed

**Solution:**
1. Check Render logs for Python errors
2. Verify database connection: Can you connect manually?
3. Check `requirements.txt` for missing packages
4. Redeploy manually from Render dashboard

### Issue: Slow Database Queries

**If 10-20 employee demo is slow:**
1. Check database server location (latency)
2. Consider adding indexes to attendance table (acceptable for demo)
3. Render free tier may have CPU throttling—upgrade if needed

---

## Performance Optimization (Optional for Demo)

For a smoother 10-20 employee demo:

1. **Database Indexes:**
   ```sql
   CREATE INDEX idx_attendance_user_date ON attendance(user_id, date);
   CREATE INDEX idx_users_username ON users(username);
   ```

2. **Caching:**
   - Add Redis for session storage (advanced)
   - Or use Render Redis add-on

3. **Render Resources:**
   - Upgrade from free tier if experiencing slowness
   - Free tier: 0.5 CPU, 512 MB RAM (usually sufficient for 10-20 users)

---

## Ongoing Maintenance

### Monitor Deployments
- **Render**: Dashboard shows auto-redeploy status
- **Netlify**: Shows deployment history and build logs

### Database Backups
- Set up automated backups on your MySQL server
- Especially important before major demos

### Update Environment Variables
- To change database password: Update in Render dashboard (redeploys automatically)
- To update API URLs: Push code changes to GitHub

### Monitoring
- Use Render logs for backend errors
- Use Netlify deployment logs for frontend issues
- Monitor database query performance

---

## Quick Reference: Deployment URLs

After setup, you'll have:

| Component | URL |
|-----------|-----|
| **Backend API** | `https://cgs-backend.onrender.com` |
| **Frontend** | `https://your-site.netlify.app` |
| **Admin Dashboard** | `https://your-site.netlify.app/admin/dashboard.html` |
| **Health Check** | `https://cgs-backend.onrender.com/health` |

---

## Support & Issues

### Common Questions

**Q: Can I use free tier for production?**  
A: Yes, for demo with 10-20 employees. For larger scale, upgrade Render plan.

**Q: How do I update the frontend?**  
A: Push to GitHub → Netlify auto-deploys within minutes.

**Q: How do I update the backend?**  
A: Push to GitHub → Render auto-deploys within minutes.

**Q: Can I revert to a previous version?**  
A: Yes, both Render and Netlify have deployment history. Revert with one click.

---

## Next Steps

1. ✅ Deploy backend on Render
2. ✅ Deploy frontend on Netlify
3. ✅ Test end-to-end workflow
4. ✅ Prepare demo data (10-20 test employees)
5. ✅ Brief demo script for stakeholders
6. ✅ Monitor first 24 hours for any issues

Great! Your CGS Attendance System is now live! 🚀
