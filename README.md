# CGS Attendance Management System - Netlify + Render Edition

> Converted from Flask monolithic app to separated frontend (Netlify) + backend (Render) architecture. Ready for demo deployment with 10-20 employees.

## 📋 Quick Start

### For Development (Local Testing)

```bash
# 1. Setup backend
pip install -r requirements.txt
copy .env.example .env
# Edit .env with your database credentials

# 2. Run Flask backend
python app.py
# Backend runs on http://localhost:5000

# 3. Open frontend
# Open frontend/index.html in browser with live server
# Or directly: file:///d:/PROJECTS/CGS/frontend/index.html
```

### For Deployment (Production on Render + Netlify)

**See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for complete step-by-step instructions**

Quick summary:
1. Push to GitHub
2. Connect GitHub to Render (backend)
3. Connect GitHub to Netlify (frontend)  
4. Set environment variables
5. Deploy (auto-deploy on git push)

---

## 📁 Project Structure

```
CGS/
├── app.py                      # Flask backend (main application)
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── render.yaml                # Render deployment config
│
├── frontend/                  # Standalone website (deploy to Netlify)
│   ├── index.html            # Login page
│   ├── dashboard.html        # Employee dashboard
│   ├── mark_attendance.html  # Check-in/Check-out
│   ├── leave_management.html # Leave requests
│   ├── view_attendance.html  # Attendance records
│   ├── netlify.toml          # Netlify config
│   ├── _redirects            # Netlify routing
│   ├── js/
│   │   ├── config.js         # Environment config
│   │   ├── api.js            # Centralized API client
│   │   └── auth.js           # Authentication handler
│   └── css/
│       ├── styles.css        # Main stylesheet
│       └── bootstrap.min.css # Bootstrap framework
│
├── templates/                 # Jinja2 templates (legacy, can be removed)
├── static/                    # Static assets (legacy)
├── database_schema/          # SQL migration scripts
│
├── MIGRATION_PLAN.md         # Detailed migration strategy
├── DEPLOYMENT_GUIDE.md       # Step-by-step deployment
├── IMPLEMENTATION_SUMMARY.md # Quick reference
└── README.md                 # This file
```

---

## 🎯 Architecture Overview

### Before (Monolithic)
```
Client Browser
    ↓ (HTTP)
Flask App (localhost:5000)
    ├── Renders HTML templates
    ├── Serves static files
    ├── Processes forms
    └── Queries MySQL
```

### After (Separated)
```
Client Browser (Netlify)
    ↓ REST API (JSON)
Flask Backend (Render)
    ├── /login (JSON)
    ├── /checkin (JSON)
    ├── /checkout (JSON)
    └── Queries MySQL
```

**Benefits:**
- Frontend can be deployed independently
- Easier to scale backend
- Frontend can work offline/static
- Better for mobile apps later

---

## 🚀 Core Features

### ✅ Employee Features
- **Login/Logout** - Secure authentication
- **Check-in/Check-out** - Location + photo capture
- **View Attendance** - Historical records with filters
- **Apply Leave** - Submit leave requests
- **Dashboard** - Quick status overview
- **Account Settings** - Profile management

### ✅ Admin Features  
- **Employee Management** - CRUD operations
- **Attendance Dashboard** - Overview of all staff
- **Leave Management** - Approve/reject requests
- **Reports** - Export attendance data
- **Settings** - Configure system

### ✅ Technical Features
- **Session Authentication** - Secure cookie-based sessions
- **Geofencing** - Location validation
- **Photo Capture** - Check-in/out documentation
- **Responsive Design** - Works on mobile/tablet
- **CORS Support** - Cross-domain API calls

---

## 🔧 Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | JavaScript, HTML5, CSS3 | ES6 |
| Backend | Flask | 3.0.0 |
| Database | MySQL | 5.7+ |
| Hosting (Backend) | Render | - |
| Hosting (Frontend) | Netlify | - |
| CORS | Flask-CORS | 4.0.0 |
| WSGI | Gunicorn | 21.2.0 |

---

## 🔐 Security

- ✅ Password hashing with bcrypt
- ✅ Session-based authentication with HTTP-only cookies
- ✅ CSRF protection on form endpoints
- ✅ HTTPS/SSL on both Render and Netlify
- ✅ CORS restricted to known domains
- ✅ No sensitive data in localStorage
- ✅ SQL injection prevention with parameterized queries

---

## 📊 Demo Information

### Recommended Demo Setup
- **Users**: 10-20 employees + 1 admin
- **Duration**: 15-20 minute walkthrough
- **Focus**: Login → Dashboard → Check-in/out → Leave → Admin View
- **Scale**: Render free tier (0.5 CPU, 512MB RAM) is sufficient

### Test Credentials
```
Employee:
  username: emp001
  password: password123
  
Admin:
  username: admin
  password: admin123
```

---

## 📚 Documentation

1. **[MIGRATION_PLAN.md](./MIGRATION_PLAN.md)**
   - Complete migration strategy
   - Code examples for all changes
   - Frontend/backend conversion details
   - Phase-by-phase checklist

2. **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)**
   - Step-by-step Render setup
   - Step-by-step Netlify setup
   - Environment variable configuration
   - Testing & troubleshooting
   - Production checklist

3. **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)**
   - Quick reference of all changes
   - File-level summary
   - Testing checklist
   - Common issues & solutions

---

## 🛠️ Development

### Adding New Frontend Page

1. Create `frontend/mypage.html`
2. Add authentication check:
   ```html
   <script>
     document.addEventListener('DOMContentLoaded', () => {
       requireAuth(['employee']); // or ['admin']
     });
   </script>
   ```
3. Use API client for backend calls:
   ```javascript
   const result = await apiCall('/endpoint', 'GET');
   ```

### Adding New Backend Endpoint

1. Add route in `app.py`:
   ```python
   @app.route('/api/myendpoint', methods=['GET', 'POST'])
   @employee_required  # or @admin_required
   def my_endpoint():
       # Handle request
       return jsonify({'status': 'success', ...})
   ```

2. Call from frontend:
   ```javascript
   const result = await apiCall('/api/myendpoint', 'POST', data);
   ```

---

## 🐛 Troubleshooting

### Login Not Working
- Check browser console for error messages
- Verify backend is accessible: `https://your-backend.onrender.com/health`
- Ensure database credentials in .env are correct
- Check CORS configuration includes your Netlify domain

### Photos Not Uploading
- Verify camera permissions in browser settings
- Check file size isn't exceeding backend limit
- Ensure `UPLOAD_FOLDER` exists on server with write permissions

### Slow Performance  
- Check database server latency
- Review Render logs for CPU/memory throttling
- Consider adding database indexes on frequently queried columns
- Upgrade Render plan if needed

### Session Expires on Page Refresh
- Verify browser allows third-party cookies
- Check that `credentials: 'include'` is in `api.js`
- Verify session cookie is being sent (check DevTools → Application → Cookies)

---

## 📈 Monitoring & Logs

### Render (Backend)
- **Dashboard**: https://dashboard.render.com
- **Logs**: Service → Logs tab
- **Metrics**: Service → Metrics tab

### Netlify (Frontend)
- **Dashboard**: https://app.netlify.com
- **Build Logs**: Deploys → Click deployment
- **Analytics**: Analytics tab (if enabled)

---

## 🔄 Deployment Workflow

```
Local Development (on your machine)
  ↓ git push
GitHub Repository
  ↓ (webhook)
Render (Backend)
  - Auto-pulls from GitHub
  - Installs dependencies
  - Starts gunicorn server

Netlify (Frontend)  
  - Auto-pulls from GitHub
  - Publishes `frontend/` folder
  - Sets environment variables
```

**Updates are automatic!** After pushing to GitHub, both services redeploy within 2-3 minutes.

---

## 📞 Support

### Common Commands

```bash
# Test backend health
curl https://your-backend.onrender.com/health

# Test API endpoint
curl -X POST https://your-backend.onrender.com/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123","role":"employee"}'

# View backend logs
# Go to Render Dashboard → Your Service → Logs

# Clear browser cache
# Ctrl+F5 (or Cmd+Shift+R on Mac)
```

### Getting Help

1. **Check logs first** (Render or Netlify)
2. **Review error in browser console** (F12)
3. **Check network tab** (F12 → Network → see API calls)
4. **Test independently** (use curl to test backend directly)

---

## 📝 Version History

- **v2.0** (Current) - Netlify + Render deployment ready
  - Separated frontend to standalone website
  - Backend converted to JSON API
  - Added deployment configurations
  - Ready for demo with 10-20 users

- **v1.0** (Original) - Monolithic Flask app
  - Everything in one Flask application
  - Templates rendered server-side
  - Static files served by Flask

---

## ✨ What's Not Changed

All existing business logic is preserved:
- ✅ MySQL queries unchanged
- ✅ Authentication logic same
- ✅ Attendance validation same
- ✅ Leave request approval workflow same
- ✅ Geofencing logic same
- ✅ Photo upload functionality same
- ✅ Database schema unchanged

**You're just changing how the frontend and backend communicate!**

---

## 🎓 Learning Resources

### Frontend Learning
- Fetch API: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
- localStorage: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage
- Geolocation API: https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API

### Backend Learning
- Flask-CORS: https://flask-cors.readthedocs.io
- Flask Patterns: https://flask.palletsprojects.com/patterns
- REST API Best Practices: https://restfulapi.net

### Deployment Learning
- Render Docs: https://render.com/docs
- Netlify Docs: https://docs.netlify.com

---

## 📄 License

Same as original project (if applicable).

---

## 🎉 Next Steps

1. ✅ Review [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
2. ✅ Set up GitHub repository
3. ✅ Deploy backend to Render
4. ✅ Deploy frontend to Netlify
5. ✅ Test end-to-end workflow
6. ✅ Run demo with stakeholders

**You're all set! Happy deploying! 🚀**

---

**Questions or issues?** Review the detailed guides or check the troubleshooting section above.
