# Netlify Deployment Setup Guide

## Overview
The frontend is a static HTML/CSS/JS site that communicates with the Flask backend deployed on Render.

## Environment Variables Required

After connecting your GitHub repository to Netlify, set these environment variables in **Netlify Site Settings > Build & Deploy > Environment**:

| Variable | Example Value | Description |
|----------|---------------|-------------|
| `API_URL` | `https://cgs-backend-xxxxx.onrender.com` | Backend URL (obtained after Render deployment) |

## Step-by-Step Netlify Setup

### 1. Connect Git Repository
1. Go to https://app.netlify.com/
2. Click "Add new site" → "Import an existing project"
3. Select GitHub, authenticate, and choose `cgs-attendance` repository
4. Click "Deploy site"

### 2. Configure Build Settings
- **Base directory:** `frontend`
- **Build command:** `echo 'Static content'` (or leave empty)
- **Publish directory:** `frontend`

### 3. Set Environment Variables
1. Go to **Site settings** → **Build & deploy** → **Environment**
2. Add new variable:
   - Key: `API_URL`
   - Value: `https://YOUR-RENDER-BACKEND-URL.onrender.com` (from Render deployment)

### 4. Add to Site Configuration

Add this to your Netlify UI or `netlify.toml`:

```toml
[context.production]
  environment = { API_URL = "https://cgs-backend-xxxxx.onrender.com" }
```

Or set manually:
- Variable name: `API_URL`
- Variable value: Render backend URL

### 5. Redeploy Site
After setting environment variables:
1. Click **Deploys** → **Trigger deploy** → **Deploy site**
2. Netlify rebuilds and frontend will now use correct backend URL

## Frontend Configuration

The frontend (`frontend/js/config.js`) automatically:
- Detects `localhost` → uses `http://localhost:5000`
- Detects `netlify.app` → uses `API_URL` from localStorage
- Falls back to localStorage value if set

## Verify Deployment

1. Visit your Netlify site URL: `https://your-site.netlify.app`
2. Open browser console (F12)
3. Look for: `[CONFIG] API URL: https://cgs-backend-xxxxx.onrender.com`
4. Try login with credentials:
   - Username: `pradeep` (or other employee)
   - Password: `test123` (if reset_password.py was run)

## Troubleshooting

### Blank screen or login fails
1. Check console (F12) for errors
2. Verify API_URL in Environment variables
3. Check Render backend is running

### CORS errors
1. Backend must have CORS enabled (already configured in app.py)
2. Verify API_URL matches Render deployment exactly

### Session not persisting
1. Ensure cookies are enabled in browser
2. Frontend uses `credentials: 'include'` in fetch() calls
3. Backend session cookie domain must match

## Next Steps

1. Deploy backend to Render (see DEPLOYMENT_GUIDE.md)
2. Get Render URL (e.g., `https://cgs-backend-xxxxx.onrender.com`)
3. Set `API_URL` environment variable in Netlify
4. Redeploy Netlify site
5. Test full login flow
